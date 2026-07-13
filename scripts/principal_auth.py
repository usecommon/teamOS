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
from datetime import datetime, timezone
from pathlib import Path

ENV_KEYDIR = "TEAMOS_PRINCIPAL_KEYDIR"
# Replay/freshness window for signals that MOVE autonomy. A captured signature
# is useless outside this window (freshness) and can be spent only once (nonce).
DEFAULT_MAX_AGE_S = 24 * 3600


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


def _harvested_at(record):
    return (record.get("harvest") or {}).get("harvested_at") \
        or record.get("harvested_at") or ""


def signing_payload(record):
    """The fields the signature binds: what was signaled, about what, by whom,
    HOW MUCH it was edited, plus a per-record nonce + timestamp.

    edit_distance is bound because it decides acceptance (WO-2): leaving it
    unsigned let a holder of a valid endorsement sig flip it to 0 and force a
    widen. nonce + harvested_at are bound so a captured signature is neither
    replayable nor re-timestampable — the envelope's freshness/replay checks
    (verified_fresh) verify fields the signature actually covers."""
    ref = record.get("artifact_ref") or {}
    return "|".join([
        str(record.get("signal_type", "")),
        str(ref.get("path", "")),
        str(record.get("principal_id", "")),
        str(record.get("outcome", "")),
        str(record.get("edit_distance_normalized", "")),
        str(record.get("nonce", "")),
        str(_harvested_at(record)),
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


# --- WO-2: ingestion-time replay + freshness (for signals that MOVE autonomy) -
# verified() above stays PURE — aggregation (measurement.weekly_accepted) re-reads
# historical records and must not freshness- or replay-reject them. The envelope,
# which is the only consumer that WIDENS on a signal, uses verified_fresh().

def _is_fresh(record, now=None, max_age_s=DEFAULT_MAX_AGE_S):
    ts = _harvested_at(record)
    if not ts:
        return True  # no bound timestamp (synthetic/formative) -> not gated on age
    try:
        t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return False  # a record we're age-gating with an unparseable stamp: reject
    now = now or datetime.now(timezone.utc)
    age = (now - t).total_seconds()
    return -60 <= age <= max_age_s  # future-dated (>60s skew) or too old -> stale


def _seen_path(seen_store, nonce):
    safe = hashlib.sha256(str(nonce).encode()).hexdigest()
    return Path(seen_store) / f"{safe}.seen"


def _nonce_unseen_and_mark(seen_store, nonce):
    """Atomic check-and-consume. True if the nonce was NOT seen before (and is
    now recorded); False if already spent (replay). O_EXCL makes it race-safe."""
    p = _seen_path(seen_store, nonce)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.close(os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
        return True
    except FileExistsError:
        return False


def verified_fresh(record, seen_store, keydir=None, now=None,
                   max_age_s=DEFAULT_MAX_AGE_S):
    """Trustworthy AND first-use AND fresh — the check the envelope consumes.
    Adds replay + freshness on top of verified():
      - signature valid over the full payload (incl. edit_distance),
      - timestamp within the window (a stale captured sig is refused),
      - nonce not previously spent (a duplicate is refused) — consumes it.
    A record with no nonce is not deduped, and no timestamp is not age-gated
    (keeps synthetic/formative signals working); real L8 records carry both."""
    if not verified(record, keydir):
        return False
    if not _is_fresh(record, now, max_age_s):
        return False
    nonce = record.get("nonce")
    if nonce and seen_store is not None:
        if not _nonce_unseen_and_mark(seen_store, nonce):
            return False  # replay
    return True
