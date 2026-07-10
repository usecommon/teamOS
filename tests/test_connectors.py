"""FK3b F-tests: off-by-default returns nothing until toggled; toggle ledgered;
every ingested item carries workspace provenance; allowlist blocks a non-listed
source; shipped config holds no opinion (empty allowlist, all sources off)."""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import connectors  # noqa: E402
import hashchain  # noqa: E402

SHIPPED = connectors.load_config()


class ShippedConfigNeutral(unittest.TestCase):
    def test_ships_with_empty_allowlist_and_all_sources_off(self):
        self.assertEqual(SHIPPED["allowlist"], [])
        for s in SHIPPED["sources"]:
            self.assertFalse(s["enabled"], s["source_id"])
        for ch in SHIPPED["notification_channels"]:
            self.assertFalse(ch["enabled"], ch["channel_id"])

    def test_sources_are_teamos_plane_a_on_owned_inference(self):
        # teamOS has its OWN connections; runs on owned inference, excludes Claude
        self.assertEqual(SHIPPED["inference"]["mode"], "owned")
        self.assertTrue(SHIPPED["inference"].get("excludes_claude"))
        for s in SHIPPED["sources"]:
            self.assertEqual(s["credential_domain"], "teamos_plane_a", s["source_id"])


class CredentialDomains(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.cfg_path = self.d / "connectors.json"
        cfg = copy.deepcopy(SHIPPED)
        for s in cfg["sources"]:
            s["enabled"] = True  # isolate the domain/inference gates
        self.cfg = cfg
        connectors.save_config(cfg, self.cfg_path)
        self.sid = "local-claude-footprint"

    def tearDown(self):
        self.tmp.cleanup()

    def test_plane_a_source_reachable_by_path_a_loop(self):
        eligible, rule = connectors.eligibility(self.cfg, self.sid, runtime="path_a")
        self.assertTrue(eligible, rule)

    def test_plane_a_source_not_reachable_by_cloud_path_b(self):
        # non-interchangeable: cloud path (b) reaches no direct teamOS source
        eligible, rule = connectors.eligibility(self.cfg, self.sid, runtime="path_b")
        self.assertFalse(eligible)
        self.assertEqual(rule, "credential-domain-mismatch")

    def test_claude_account_source_not_reachable_by_path_a(self):
        cfg = copy.deepcopy(self.cfg)
        connectors._source(cfg, self.sid)["credential_domain"] = "claude_account"
        eligible, rule = connectors.eligibility(cfg, self.sid, runtime="path_a")
        self.assertFalse(eligible)
        self.assertEqual(rule, "credential-domain-mismatch")

    def test_plane_a_blocked_without_owned_inference(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["inference"] = {"mode": "subscription", "backend": "claude_subscription"}
        eligible, rule = connectors.eligibility(cfg, self.sid, runtime="path_a")
        self.assertFalse(eligible)
        self.assertEqual(rule, "plane-a-needs-owned-inference")

    def test_provenance_carries_credential_domain(self):
        out = connectors.ingest(self.sid, [{"x": 1}], config_path=self.cfg_path,
                                ledger_dir=self.d)
        self.assertEqual(out[0]["provenance"]["credential_domain"], "teamos_plane_a")


class OptInGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.cfg_path = self.d / "connectors.json"
        connectors.save_config(copy.deepcopy(SHIPPED), self.cfg_path)
        self.sid = "local-claude-footprint"

    def tearDown(self):
        self.tmp.cleanup()

    def test_off_by_default_returns_nothing(self):
        out = connectors.ingest(self.sid, [{"x": 1}], config_path=self.cfg_path,
                                ledger_dir=self.d)
        self.assertEqual(out, [])
        # nothing ingested => no L3 provenance written
        self.assertFalse((self.d / "l3.jsonl").exists())

    def test_toggle_enables_and_is_ledgered(self):
        connectors.toggle(self.sid, True, config_path=self.cfg_path, ledger_dir=self.d)
        record = json.loads((self.d / "l2.jsonl").read_text().splitlines()[-1])
        self.assertEqual(record["rule_id"], "source-toggle")
        self.assertIn(self.sid, record["proposed_action"]["target"])
        # reload persisted config: now enabled
        cfg = connectors.load_config(self.cfg_path)
        self.assertTrue(connectors._source(cfg, self.sid)["enabled"])

    def test_ingest_after_toggle_carries_provenance(self):
        connectors.toggle(self.sid, True, config_path=self.cfg_path, ledger_dir=self.d)
        out = connectors.ingest(self.sid, [{"x": 1}, {"y": 2}],
                                config_path=self.cfg_path, ledger_dir=self.d)
        self.assertEqual(len(out), 2)
        for item in out:
            self.assertEqual(item["provenance"]["workspace"], "~/.claude")
            self.assertEqual(item["provenance"]["source_id"], self.sid)
        # L3 provenance written per item, workspace present
        l3 = [json.loads(l) for l in (self.d / "l3.jsonl").read_text().splitlines()]
        self.assertEqual(len(l3), 2)
        self.assertEqual(l3[0]["source_type"], "connector:local-folder")
        self.assertEqual(hashchain.verify(self.d / "l3.jsonl"), 2)

    def test_dm_email_opt_in_separate_toggle(self):
        # DMs/email are opt-in: enabling the source alone doesn't flip dm_email
        connectors.toggle(self.sid, True, config_path=self.cfg_path, ledger_dir=self.d)
        cfg = connectors.load_config(self.cfg_path)
        self.assertFalse(connectors._source(cfg, self.sid)["dm_email"])
        connectors.toggle(self.sid, True, config_path=self.cfg_path, ledger_dir=self.d,
                          field="dm_email")
        cfg = connectors.load_config(self.cfg_path)
        self.assertTrue(connectors._source(cfg, self.sid)["dm_email"])


class Allowlist(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.cfg_path = self.d / "connectors.json"
        cfg = copy.deepcopy(SHIPPED)
        # populate allowlist with a DIFFERENT source; enable the tested one
        cfg["allowlist"] = ["some-other-source"]
        for s in cfg["sources"]:
            if s["source_id"] == "local-claude-footprint":
                s["enabled"] = True
        connectors.save_config(cfg, self.cfg_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_allowlist_blocks_non_listed_even_when_enabled(self):
        eligible, rule = connectors.eligibility(
            connectors.load_config(self.cfg_path), "local-claude-footprint")
        self.assertFalse(eligible)
        self.assertEqual(rule, "allowlist-block")
        out = connectors.ingest("local-claude-footprint", [{"x": 1}],
                                config_path=self.cfg_path, ledger_dir=self.d)
        self.assertEqual(out, [])

    def test_allowlisted_and_enabled_source_ingests(self):
        cfg = connectors.load_config(self.cfg_path)
        cfg["allowlist"].append("local-claude-footprint")
        connectors.save_config(cfg, self.cfg_path)
        out = connectors.ingest("local-claude-footprint", [{"x": 1}],
                                config_path=self.cfg_path, ledger_dir=self.d)
        self.assertEqual(len(out), 1)

    def test_policy_neutral_refuses_to_toggle_unconfigured_source(self):
        with self.assertRaises(ValueError):
            connectors.toggle("not-in-config", True, config_path=self.cfg_path,
                              ledger_dir=self.d)


if __name__ == "__main__":
    unittest.main()
