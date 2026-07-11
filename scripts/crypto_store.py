"""Per-principal encrypted personal stores + access self-ledgering (FK7-pre).

Invariants (before the 2nd user exists):
- personal stores are encrypted per principal; keys NEVER live in the shared
  repo — a clone delivers your own decryptable scope + shared artifacts you're
  keyed for, never another principal's readable personal store (exit = clone).
- any read of a principal's personal store lands in THEIR feed (self-ledgering),
  whether it succeeds or is denied.

Uses Fernet (AES-128-CBC + HMAC) — a vetted AEAD; wrong key => InvalidToken =>
the read is refused by construction.
"""

import sys
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

FEED_AGENT_ID = "teamos-access-feed/0.1"


class CrossPrincipalDenied(PermissionError):
    pass


class KeyInRepoError(RuntimeError):
    pass


def generate_key():
    return Fernet.generate_key()


def _assert_key_outside_repo(keydir, repo_root):
    kd = Path(keydir).resolve()
    rr = Path(repo_root).resolve()
    if str(kd) == str(rr) or str(kd).startswith(str(rr) + "/"):
        raise KeyInRepoError(
            f"key dir {kd} is inside the shared repo {rr} — keys must never be "
            f"committable (exit=clone invariant)")


def load_or_create_key(keydir, principal, repo_root):
    _assert_key_outside_repo(keydir, repo_root)
    keydir = Path(keydir)
    keydir.mkdir(parents=True, exist_ok=True)
    kp = keydir / f"{principal}.key"
    if not kp.exists():
        kp.write_bytes(generate_key())
    return kp.read_bytes()


def write_personal_store(owner, plaintext, store_dir, key):
    """Encrypt `plaintext` under the owner's key; write ciphertext into the
    (shareable) store. The store holds only ciphertext at rest."""
    token = Fernet(key).encrypt(plaintext.encode())
    path = Path(store_dir) / "personal" / owner / "store.enc"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(token)
    return path


def _self_ledger(ledger_dir, reader, owner, ok):
    feed = Path(ledger_dir) / "feeds" / f"{owner}.jsonl"
    hashchain.append(feed, {
        "event": "personal_store_read",
        "reader": reader, "owner": owner, "granted": ok,
    }, FEED_AGENT_ID)


def read_personal_store(reader, owner, store_dir, reader_key, ledger_dir):
    """Attempt to read owner's personal store with the reader's key. ALWAYS
    self-ledgers to the owner's feed. A cross-principal read fails (the reader's
    key cannot decrypt the owner's token) and is denied + ledgered."""
    path = Path(store_dir) / "personal" / owner / "store.enc"
    token = path.read_bytes()
    try:
        plaintext = Fernet(reader_key).decrypt(token).decode()
    except InvalidToken:
        _self_ledger(ledger_dir, reader, owner, ok=False)
        raise CrossPrincipalDenied(
            f"{reader} cannot read {owner}'s personal store (not keyed)")
    _self_ledger(ledger_dir, reader, owner, ok=True)
    return plaintext
