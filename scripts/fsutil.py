"""Atomic state-file writes (T13). Breaker, envelope, deletion, and schedule
state must never be half-written: a crash mid-write leaving corrupt JSON either
bricks a control (breaker fails closed) or loses a dial. tmp + fsync + rename
guarantees readers see the old state or the new state, never a torn one.
"""

import os
from pathlib import Path


def atomic_write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)
    return path
