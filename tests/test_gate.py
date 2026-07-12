"""A-FK2 / FR2 gate F-tests: payload inspection blocks the exfil probe set
(canonical + obfuscated), benign controls pass, every call is ledgered,
inspection runs regardless of posture, distinct outcome recording."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "hooks"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate  # noqa: E402
import hashchain  # noqa: E402

PROBES = json.loads((REPO_ROOT / "fixtures" / "exfil-probes.json").read_text())


class GateBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger_dir = Path(self.tmp.name)
        self._orig = gate.LEDGER_DIR
        gate.LEDGER_DIR = self.ledger_dir
        self.policy = gate.load_policy()

    def tearDown(self):
        gate.LEDGER_DIR = self._orig
        self.tmp.cleanup()

    def run_probe(self, probe):
        return gate.process(
            {"tool_name": probe["tool_name"], "tool_input": probe["tool_input"],
             "session_id": "test"},
            self.policy,
        )


class ProbeSet(GateBase):
    def _check(self, probe):
        gate.process(
            {"tool_name": probe["tool_name"], "tool_input": probe["tool_input"]},
            self.policy,
        )
        record = json.loads((self.ledger_dir / "l2.jsonl").read_text().splitlines()[-1])
        self.assertEqual(record["verdict"], probe["expect_verdict"], probe["name"])
        self.assertEqual(record["rule_id"], probe["expect_rule"], probe["name"])
        # every probe is ledgered with a non-empty inspection
        self.assertIn("checks_run", record["inspection"])
        self.assertTrue(record["inspection"]["checks_run"], probe["name"])
        return record

    def test_canonical_probes_blocked_and_ledgered(self):
        for probe in PROBES["canonical"]:
            record = self._check(probe)
            self.assertNotEqual(record["verdict"], "permit", probe["name"])

    def test_obfuscated_probes_blocked_and_ledgered(self):
        for probe in PROBES["obfuscated"]:
            record = self._check(probe)
            self.assertNotEqual(record["verdict"], "permit", probe["name"])

    def test_benign_controls_permitted(self):
        for probe in PROBES["benign_controls"]:
            record = self._check(probe)
            self.assertEqual(record["verdict"], "permit", probe["name"])

    def test_attacker_shaped_probes_blocked_and_ledgered(self):
        # T2: probes written the way an attacker writes them (quoting, base64,
        # ssh, git push, unknown tools) — never shaped to match the pattern.
        for probe in PROBES["attacker_shaped"]:
            record = self._check(probe)
            self.assertNotEqual(record["verdict"], "permit", probe["name"])

    def test_l2_chain_verifies_after_probe_set(self):
        for probe in PROBES["canonical"] + PROBES["obfuscated"] + PROBES["benign_controls"]:
            self.run_probe(probe)
        self.assertGreater(hashchain.verify(self.ledger_dir / "l2.jsonl"), 0)


class InspectionAlwaysOn(GateBase):
    def test_inspection_runs_under_unattended_posture(self):
        # Posture changes the RECORD, never whether inspection runs (FR2).
        orig = gate.POSTURE
        try:
            gate.POSTURE = "unattended-guarded"
            probe = PROBES["canonical"][0]
            gate.process(
                {"tool_name": probe["tool_name"], "tool_input": probe["tool_input"]},
                self.policy,
            )
            record = json.loads((self.ledger_dir / "l2.jsonl").read_text().splitlines()[-1])
            self.assertEqual(record["posture"], "unattended-guarded")
            self.assertEqual(record["verdict"], "deny")
            self.assertIn("bash-egress-scan", record["inspection"]["checks_run"])
        finally:
            gate.POSTURE = orig

    def test_outcome_distinct_from_verdict(self):
        deny = self.run_probe(PROBES["canonical"][0])
        permit = self.run_probe(PROBES["benign_controls"][0])
        self.assertIn("deny", deny["hookSpecificOutput"]["permissionDecision"])
        self.assertIn("allow", permit["hookSpecificOutput"]["permissionDecision"])
        records = [
            json.loads(l) for l in (self.ledger_dir / "l2.jsonl").read_text().splitlines()
        ]
        outcomes = {r["rule_id"]: r["outcome"] for r in records}
        self.assertEqual(outcomes["bash-exfil"], "gate_blocked")
        self.assertEqual(outcomes["default-permit"], "gate_passed")

    def test_headless_mode_identical(self):
        # Headless = no tty; process() takes plain dict input, no interactive
        # dependency. Same input -> same verdict as attended.
        probe = PROBES["canonical"][1]
        a = self.run_probe(probe)
        b = self.run_probe(probe)
        self.assertEqual(
            a["hookSpecificOutput"]["permissionDecision"],
            b["hookSpecificOutput"]["permissionDecision"],
        )


class Taint(GateBase):
    """T2 Layer A: untrusted content supplies values, never plan structure."""

    def _process(self, tool, tool_input, session="s1"):
        gate.process({"tool_name": tool, "tool_input": tool_input,
                      "session_id": session}, self.policy)
        return json.loads(
            (self.ledger_dir / "l2.jsonl").read_text().splitlines()[-1])

    def test_send_after_corpus_read_requires_confirmation(self):
        # session reads corpus -> tainted; a later send whose URL could carry a
        # paraphrase of that content must ASK, not permit
        read = self._process("Read", {"file_path": "stores/corpus/meeting-notes.md"})
        self.assertEqual(read["verdict"], "permit")
        send = self._process("WebFetch",
                             {"url": "https://summarizer.example/?d=some-paraphrase"})
        self.assertEqual(send["verdict"], "ask")
        self.assertEqual(send["rule_id"], "taint-confirm")

    def test_untainted_session_send_still_permits(self):
        send = self._process("WebSearch", {"query": "python docs"}, session="clean")
        self.assertEqual(send["verdict"], "permit")
        self.assertEqual(send["rule_id"], "send-scanned-clean")

    def test_taint_is_session_scoped(self):
        self._process("Read", {"file_path": "inbox/proposals/x.json"}, session="a")
        other = self._process("WebSearch", {"query": "docs"}, session="b")
        self.assertEqual(other["verdict"], "permit")

    def test_webfetch_taints_session(self):
        self._process("WebFetch", {"url": "https://news.example/article"},
                      session="w")
        send = self._process("WebSearch", {"query": "follow-up"}, session="w")
        self.assertEqual(send["rule_id"], "taint-confirm")

    def test_schedule_in_tainted_session_asks(self):
        self._process("Read", {"file_path": "stores/corpus/notes.md"}, session="sc")
        policy = dict(self.policy)
        policy["action_classes"] = dict(policy["action_classes"],
                                        CronCreate="schedule")
        gate.process({"tool_name": "CronCreate",
                      "tool_input": {"cron": "0 9 * * *", "prompt": "do x"},
                      "session_id": "sc"}, policy)
        rec = json.loads(
            (self.ledger_dir / "l2.jsonl").read_text().splitlines()[-1])
        self.assertEqual(rec["rule_id"], "taint-confirm")

    def test_corrupt_taint_state_fails_closed(self):
        taint_dir = self.ledger_dir / "taint"
        taint_dir.mkdir(parents=True, exist_ok=True)
        (taint_dir / "corrupt.json").write_text("{not json")
        send = self._process("WebSearch", {"query": "docs"}, session="corrupt")
        self.assertEqual(send["rule_id"], "taint-confirm")


class ProtectedDials(GateBase):
    """T3: resolved-path protection; the dial, the stop, and the hook config
    are untouchable; the breaker is unconditional and fails closed."""

    def _write(self, path, content="x"):
        gate.process({"tool_name": "Write",
                      "tool_input": {"file_path": str(path), "content": content},
                      "session_id": "t3"}, self.policy)
        return json.loads(
            (self.ledger_dir / "l2.jsonl").read_text().splitlines()[-1])

    def test_symlink_to_protected_file_is_caught(self):
        link = self.ledger_dir / "innocent.py"
        link.symlink_to(REPO_ROOT / "hooks" / "gate.py")
        rec = self._write(link)
        self.assertEqual(rec["verdict"], "ask")
        self.assertEqual(rec["rule_id"], "protected-path")

    def test_breaker_state_write_is_protected(self):
        rec = self._write("/anywhere/at/all/breaker.json", '{"state":"closed"}')
        self.assertEqual(rec["rule_id"], "protected-path")

    def test_envelope_state_write_is_protected(self):
        rec = self._write(REPO_ROOT / "state" / "envelope-state.json")
        self.assertEqual(rec["rule_id"], "protected-path")

    def test_claude_settings_write_is_protected(self):
        rec = self._write(Path.home() / ".claude" / "settings.json", "{}")
        self.assertEqual(rec["rule_id"], "protected-path")

    def test_corrupt_breaker_file_denies_side_effects(self):
        bad = self.ledger_dir / "bad-breaker.json"
        bad.write_text("{corrupt")
        os.environ["TEAMOS_BREAKER"] = str(bad)
        try:
            rec = self._write(self.ledger_dir / "note.md")
            self.assertEqual(rec["verdict"], "deny")
            self.assertEqual(rec["rule_id"], "circuit-open")
        finally:
            os.environ.pop("TEAMOS_BREAKER", None)

    def test_missing_breaker_file_denies_side_effects(self):
        os.environ["TEAMOS_BREAKER"] = str(self.ledger_dir / "never-created.json")
        try:
            rec = self._write(self.ledger_dir / "note.md")
            self.assertEqual(rec["verdict"], "deny")
            self.assertEqual(rec["rule_id"], "circuit-open")
        finally:
            os.environ.pop("TEAMOS_BREAKER", None)

    def test_reads_pass_while_breaker_unavailable(self):
        os.environ["TEAMOS_BREAKER"] = str(self.ledger_dir / "never-created.json")
        try:
            gate.process({"tool_name": "Read",
                          "tool_input": {"file_path": "README.md"}}, self.policy)
            rec = json.loads(
                (self.ledger_dir / "l2.jsonl").read_text().splitlines()[-1])
            self.assertEqual(rec["verdict"], "permit")
        finally:
            os.environ.pop("TEAMOS_BREAKER", None)


class FailClosed(unittest.TestCase):
    """T1: a gate crash must deny, never permit — and must be ledgered."""

    def _run_main(self, stdin_text, env_overrides):
        env = dict(os.environ)
        env.update(env_overrides)
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "hooks" / "gate.py")],
            input=stdin_text, capture_output=True, text=True, env=env)

    def test_garbage_stdin_denies_and_ledgers(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run_main("this is not json {", {"TEAMOS_LEDGER_DIR": tmp})
            self.assertNotEqual(proc.returncode, 0)
            decision = json.loads(proc.stdout.splitlines()[0])
            self.assertEqual(
                decision["hookSpecificOutput"]["permissionDecision"], "deny")
            records = [json.loads(l) for l in
                       (Path(tmp) / "l2.jsonl").read_text().splitlines()]
            self.assertEqual(records[-1]["rule_id"], "gate-error")
            self.assertEqual(records[-1]["verdict"], "deny")

    def test_broken_policy_denies_not_permits(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_policy = Path(tmp) / "policy.yaml"
            bad_policy.write_text("action_classes: [unclosed\n  ] : nonsense: {{")
            probe = json.dumps({"tool_name": "Bash",
                                "tool_input": {"command": "curl evil"}})
            proc = self._run_main(probe, {"TEAMOS_LEDGER_DIR": tmp,
                                          "TEAMOS_POLICY": str(bad_policy)})
            self.assertNotEqual(proc.returncode, 0)
            decision = json.loads(proc.stdout.splitlines()[0])
            self.assertEqual(
                decision["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_unwritable_ledger_dir_still_denies(self):
        probe = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})
        proc = self._run_main(probe,
                              {"TEAMOS_LEDGER_DIR": "/dev/null/not-a-dir"})
        self.assertNotEqual(proc.returncode, 0)
        decision = json.loads(proc.stdout.splitlines()[0])
        self.assertEqual(
            decision["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
