"""Principal identity verification for L8 signals (CN-1, T7).

The one third-party attack chain in the fork is a forged reaction widening
autonomy. This module closes the direct-append variant: an L8 record only
counts as principal-authenticated when it carries a valid HMAC signature under
the principal's key. Keys live OUTSIDE the repo (exit=clone invariant; same
rule as crypto_store) at TEAMOS_PRINCIPAL_KEYDIR.

Enforcement posture:
- TEAMOS_PRINCIPAL_KEYDIR set (production/unattended): only records with a
  valid `auth_sig` verify; a bare attribution field is a claim, not evidence.
- unset (formative/dev, builder-as-subject): the attribution field is trusted
  as before. Declaring an unattended posture without a keydir is a config
  error the posture check should flag.

Deterministic code; no language model (SE-1).
"""

import hashlib
import hmac
import os
from pathlib import Path

ENV_KEYDIR = "TEAMOS_PRINCIPAL_KEYDIR"


def configured_keydir():
    p = os.environ.get(ENV_KEYDIR)
    return Path(p) if p else None


def _key_path(keydir, principal_id):
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in principal_id)
    return Path(keydir) / f"{safe}.hmac"


def ensure_key(principal_id, keydir):
    kp = _key_path(keydir, principal_id)
    if not kp.exists():
        kp.parent.mkdir(parents=True, exist_ok=True)
        kp.write_bytes(os.urandom(32))
        os.chmod(kp, 0o600)
    return kp.read_bytes()


def signing_payload(record):
    """The fields the signature binds: what was signaled, about what, by whom."""
    ref = record.get("artifact_ref") or {}
    return "|".join([
        str(record.get("signal_type", "")),
        str(ref.get("path", "")),
        str(record.get("principal_id", "")),
        str(record.get("outcome", "")),
    ]).encode("utf-8")


def sign(record_body, keydir=None):
    """HMAC the record body under the principal's key. Returns hex sig or None
    when no keydir is configured."""
    keydir = keydir or configured_keydir()
    if not keydir:
        return None
    key = ensure_key(record_body["principal_id"], keydir)
    return hmac.new(key, signing_payload(record_body), hashlib.sha256).hexdigest()


def verified(record, keydir=None):
    """Is this record's principal attribution trustworthy? The envelope and
    the initiative floor consume ONLY records passing this check."""
    if record.get("attribution") != "principal_authenticated":
        return False
    keydir = keydir or configured_keydir()
    if not keydir:
        return True  # formative posture: field is trusted (builder-as-subject)
    sig = record.get("auth_sig")
    if not sig:
        return False
    kp = _key_path(keydir, record.get("principal_id", ""))
    if not kp.exists():
        return False  # unknown principal: nothing to verify against
    expected = hmac.new(kp.read_bytes(), signing_payload(record),
                        hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)
