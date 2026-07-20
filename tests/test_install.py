"""FK6c gate activation: merge is idempotent, preserves existing settings, and
--apply writes with a backup. All in temp dirs — never touches the real .claude."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import install  # noqa: E402

FRAGMENT = REPO / "hooks" / "settings-fragment.json"
GATE_CMD = 'python3 "$CLAUDE_PROJECT_DIR/hooks/gate.py"'


class GateActivation(unittest.TestCase):
    def _frag(self):
        return json.loads(FRAGMENT.read_text())

    def test_merge_from_empty_adds_gate(self):
        merged = install.merge_gate_settings({}, self._frag())
        cmds = [h["command"] for e in merged["hooks"]["PreToolUse"] for h in e["hooks"]]
        self.assertIn(GATE_CMD, cmds)

    def test_merge_is_idempotent(self):
        once = install.merge_gate_settings({}, self._frag())
        twice = install.merge_gate_settings(once, self._frag())
        self.assertEqual(once, twice)  # no duplicate hook

    def test_merge_preserves_existing_settings_and_hooks(self):
        existing = {"model": "opus", "hooks": {"Stop": [{"matcher": "*", "hooks": [
            {"type": "command", "command": "echo bye"}]}]}}
        merged = install.merge_gate_settings(existing, self._frag())
        self.assertEqual(merged["model"], "opus")
        self.assertIn("Stop", merged["hooks"])          # unrelated hook kept
        self.assertIn("PreToolUse", merged["hooks"])     # gate added

    def test_preview_does_not_write_apply_does(self):
        with tempfile.TemporaryDirectory() as t:
            dc = Path(t) / ".claude"
            # preview
            res = install.activate(dc, FRAGMENT, apply=False)
            self.assertTrue(res["changed"])
            self.assertFalse(res["applied"])
            self.assertFalse((dc / "settings.json").exists())
            # apply
            res2 = install.activate(dc, FRAGMENT, apply=True)
            self.assertTrue(res2["applied"])
            self.assertTrue((dc / "settings.json").exists())
            self.assertIn("PreToolUse", (dc / "settings.json").read_text())
            # re-apply is a no-op (idempotent)
            res3 = install.activate(dc, FRAGMENT, apply=True)
            self.assertFalse(res3["changed"])

    def test_apply_backs_up_existing(self):
        with tempfile.TemporaryDirectory() as t:
            dc = Path(t) / ".claude"
            dc.mkdir()
            (dc / "settings.json").write_text('{"model": "sonnet"}')
            install.activate(dc, FRAGMENT, apply=True)
            self.assertTrue((dc / "settings.json.bak").exists())
            self.assertIn("sonnet", (dc / "settings.json.bak").read_text())
            self.assertIn("sonnet", (dc / "settings.json").read_text())  # preserved in merge


if __name__ == "__main__":
    unittest.main()
