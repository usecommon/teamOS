"""Gate activation (FK6c kit): merge hooks/settings-fragment.json into
.claude/settings.json so the FK2 gate fires on every tool call. The Graphify
`hook install` analogue — one step instead of hand-editing JSON.

Safe by construction: the merge is idempotent (never duplicates the hook) and
PRESERVES any existing settings/hooks. Activation is the principal's explicit
step (review hooks/gate.py vs hooks/BEHAVIOR.md first, X-1); the CLI previews by
default and only writes with --apply, keeping a .bak.
"""
import copy
import json
from pathlib import Path


def merge_gate_settings(existing, fragment):
    """Deep-merge the fragment's hooks into `existing`, deduped by command and
    grouped by matcher. Returns a new dict; existing keys are preserved."""
    merged = copy.deepcopy(existing) if existing else {}
    for event, entries in fragment.get("hooks", {}).items():
        cur = merged.setdefault("hooks", {}).setdefault(event, [])
        seen = {h.get("command") for e in cur for h in e.get("hooks", [])}
        for entry in entries:
            fresh = [h for h in entry.get("hooks", []) if h.get("command") not in seen]
            if not fresh:
                continue
            match = next((e for e in cur if e.get("matcher") == entry.get("matcher")), None)
            if match:
                match.setdefault("hooks", []).extend(fresh)
            else:
                e2 = {k: v for k, v in entry.items() if k != "hooks"}
                e2["hooks"] = fresh
                cur.append(e2)
    return merged


def activate(dot_claude, fragment_path, apply=False):
    """Preview or apply gate activation. Returns a result dict:
    {changed, applied, path, merged}. --apply writes settings.json (+ .bak)."""
    settings_path = Path(dot_claude) / "settings.json"
    existing = json.loads(settings_path.read_text()) if settings_path.exists() else {}
    fragment = json.loads(Path(fragment_path).read_text())
    merged = merge_gate_settings(existing, fragment)
    changed = merged != existing
    res = {"changed": changed, "applied": False, "path": str(settings_path), "merged": merged}
    if apply and changed:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        if settings_path.exists():
            settings_path.with_suffix(".json.bak").write_text(settings_path.read_text())
        settings_path.write_text(json.dumps(merged, indent=2) + "\n")
        res["applied"] = True
    return res
