"""Checkpoint-file shim (FR4) — the durable-execution stand-in. A multi-step
flow persists after every step; a box killed mid-run resumes from the last
checkpoint on the next invocation, losing no completed work and never repeating
a completed step.

This is the fork's biggest shim (spec §5 risk 3); if it leaks, durable
execution promotes to fork-required.
"""

import json
import os
from pathlib import Path


class Checkpoint:
    def __init__(self, path):
        self.path = Path(path)
        self.state = {"done": [], "results": {}}
        if self.path.exists():
            try:
                loaded = json.loads(self.path.read_text())
                if isinstance(loaded, dict) and "done" in loaded and "results" in loaded:
                    self.state = loaded
                else:
                    raise ValueError("checkpoint missing done/results")
            except (ValueError, OSError):
                # E4: a torn checkpoint must not brick every resume. Preserve the
                # corrupt bytes for audit and restart clean — at most a redo of
                # the in-flight run, never a permanent crash.
                self.path.replace(self.path.with_suffix(self.path.suffix + ".corrupt"))

    def is_done(self, name):
        return name in self.state["done"]

    def record(self, name, result):
        self.state["done"].append(name)
        self.state["results"][name] = result
        self._save()

    def _save(self):
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tmp.open("w") as f:
            json.dump(self.state, f)
            f.flush()
            os.fsync(f.fileno())
        tmp.replace(self.path)  # atomic: a crash mid-write leaves the old state


def run_checkpointed(steps, checkpoint_path):
    """steps: list of (name, fn) where fn(results_so_far) -> result.

    Completed steps are skipped on resume. Returns the results dict. A step that
    raises leaves prior steps durably recorded — re-invoking resumes past them.
    """
    cp = Checkpoint(checkpoint_path)
    for name, fn in steps:
        if cp.is_done(name):
            continue
        result = fn(cp.state["results"])
        cp.record(name, result)
    return cp.state["results"]
