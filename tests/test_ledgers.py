"""FK2 ledger F-tests: L3 lineage-required (rejection ledgered, CN-12); L8
content-by-reference + no inlining (SE-2); L1 compile + chain; tamper breaks
chain; golden scripted session -> expected records."""

import json
import multiprocessing
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import hashchain  # noqa: E402
import l1_compile  # noqa: E402
import l8_capture  # noqa: E402
from l3_writer import LineageRejected, write_with_lineage, entity_basis  # noqa: E402


def _append_burst(args):
    """Module-level so multiprocessing can pickle it (spawn-safe)."""
    ledger_path, writer_id, n = args
    for i in range(n):
        hashchain.append(Path(ledger_path), {"writer": writer_id, "i": i},
                         f"test-writer-{writer_id}")
    return writer_id

TRANSCRIPT = (
    REPO_ROOT / "fixtures" / "harness-footprint" / "dot-claude"
    / "projects" / "fixture-project" / "session-0001.jsonl"
)

VALID_SIDECAR = {
    "entity_id": "individual/note",
    "generated_by": {"transformation": "human-authored", "at": "2026-07-10T00:00:00Z"},
    "agent": "principal:jeff",
    "sources": [{"source_type": "principal-direct", "locator": "chat", "content_hash": "sha256:x"}],
    "evidence": ["chat"],
    "confidence": "high",
    "update_history": [],
}


class Ledgers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_lineage_write_accepted_and_chained(self):
        rec = write_with_lineage(
            self.d / "corpus" / "note.md", "content", VALID_SIDECAR, ledger_dir=self.d
        )
        self.assertEqual(rec["target_id"], "individual/note")
        self.assertTrue((self.d / "corpus" / "note.md").exists())
        self.assertTrue((self.d / "corpus" / "note.md.lineage.json").exists())
        self.assertEqual(hashchain.verify(self.d / "l3.jsonl"), 1)

    def test_missing_lineage_rejected_AND_rejection_ledgered(self):
        broken = {k: v for k, v in VALID_SIDECAR.items() if k != "confidence"}
        with self.assertRaises(LineageRejected):
            write_with_lineage(self.d / "corpus" / "bad.md", "x", broken, ledger_dir=self.d)
        # the invariant's TEST (CN-12): rejection is itself ledgered to L2
        record = json.loads((self.d / "l2.jsonl").read_text().splitlines()[-1])
        self.assertEqual(record["verdict"], "deny")
        self.assertEqual(record["rule_id"], "lineage-required")
        self.assertFalse((self.d / "corpus" / "bad.md").exists())

    def test_basis_tag_flows_into_l3_and_defaults_ambiguous(self):
        # Graphify-borrow: EXTRACTED/INFERRED/AMBIGUOUS per derivation edge.
        tagged = dict(VALID_SIDECAR,
                      sources=[{"source_type": "principal-direct", "locator": "chat",
                                "content_hash": "sha256:x", "basis": "extracted"}])
        rec = write_with_lineage(self.d / "c1.md", "x", tagged, ledger_dir=self.d)
        self.assertEqual(rec["basis"], "extracted")
        self.assertEqual(rec["evidence"][0]["basis"], "extracted")
        # an untagged edge is read as the cautious value, not silently "trusted"
        rec2 = write_with_lineage(self.d / "c2.md", "x", VALID_SIDECAR, ledger_dir=self.d)
        self.assertEqual(rec2["basis"], "ambiguous")
        # weakest edge wins: one ambiguous drags the entity to ambiguous
        self.assertEqual(entity_basis([{"basis": "extracted"}, {"basis": "ambiguous"}]),
                         "ambiguous")

    def test_invalid_basis_value_rejected_by_schema(self):
        bad = dict(VALID_SIDECAR,
                   sources=[{"source_type": "principal-direct", "locator": "chat",
                             "content_hash": "sha256:x", "basis": "definitely"}])
        with self.assertRaises(LineageRejected):
            write_with_lineage(self.d / "bad2.md", "x", bad, ledger_dir=self.d)

    def test_l8_records_outcome_not_content(self):
        draft = self.d / "draft.md"
        edited = self.d / "edited.md"
        draft.write_text("Shipped: parser fix and SECRETSAUCE recipe.\n")
        edited.write_text("Shipped: parser fix.\n")
        rec = l8_capture.capture_edit(draft, edited, "principal:jeff", ledger_dir=self.d)
        # edited content never inlined in the L8 record (SE-2)
        self.assertNotIn("SECRETSAUCE", json.dumps(rec))
        self.assertNotIn("parser fix", json.dumps(rec))
        self.assertEqual(rec["diff_ref"]["store"], "l8-sidestore")
        # T7: no key, no principal stamp — attribution defaults unattributed
        self.assertEqual(rec["attribution"], "unattributed")
        self.assertGreater(rec["edit_distance_normalized"], 0)

    def test_l8_capture_stamps_principal_only_with_key(self):
        draft, edited = self.d / "d2.md", self.d / "e2.md"
        draft.write_text("hello world\n")
        edited.write_text("hello world!\n")
        keydir = self.d / "keys"
        rec = l8_capture.capture_edit(draft, edited, "principal:jeff",
                                      ledger_dir=self.d, keydir=keydir)
        self.assertEqual(rec["attribution"], "principal_authenticated")
        self.assertIn("auth_sig", rec)
        # a light edit emits the CONSUMED signal type — local accepts are live
        self.assertEqual(rec["signal_type"], "endorsement")

    def test_l8_capture_heavy_edit_is_engagement_not_endorsement(self):
        draft, edited = self.d / "d3.md", self.d / "e3.md"
        draft.write_text("alpha\n")
        edited.write_text("completely different content entirely\n")
        rec = l8_capture.capture_edit(draft, edited, "principal:jeff",
                                      ledger_dir=self.d)
        self.assertEqual(rec["signal_type"], "edit")
        self.assertEqual(rec["outcome"], "edited-heavily")

    def test_l8_erasure_of_sidestore_keeps_chain_verifiable(self):
        # SE-2: chain hashes the REFERENCE; deleting side-store content (DSAR
        # crypto-shred) does not break chain verification.
        for i in range(3):
            d, e = self.d / f"d{i}.md", self.d / f"e{i}.md"
            d.write_text(f"draft {i} content\n")
            e.write_text(f"edited {i} content changed\n")
            l8_capture.capture_edit(d, e, "principal:jeff", ledger_dir=self.d)
        self.assertEqual(hashchain.verify(self.d / "l8.jsonl"), 3)
        # shred one referenced diff
        diffs = list((self.d / "sidestore").glob("*.diff"))
        diffs[1].unlink()
        # chain still verifies — references intact, content gone
        self.assertEqual(hashchain.verify(self.d / "l8.jsonl"), 3)

    def test_l1_compile_and_chain(self):
        records = l1_compile.compile_transcript(TRANSCRIPT, ledger_dir=self.d)
        self.assertEqual(len(records), 3)  # 2 tool spans + 1 chat
        self.assertEqual(hashchain.verify(self.d / "l1.jsonl"), 3)

    def test_concurrent_appends_never_fork_the_chain(self):
        # T5: >=4 processes hammering one ledger; the flock spanning
        # read-last-hash + write must keep the chain linear and complete.
        ledger = self.d / "concurrent.jsonl"
        writers, per_writer = 6, 25
        with multiprocessing.Pool(writers) as pool:
            pool.map(_append_burst,
                     [(str(ledger), w, per_writer) for w in range(writers)])
        self.assertEqual(hashchain.verify(ledger), writers * per_writer)
        records = [json.loads(l) for l in ledger.read_text().splitlines()]
        self.assertEqual(len(records), writers * per_writer)
        # every writer's every record landed exactly once
        seen = {(r["writer"], r["i"]) for r in records}
        self.assertEqual(len(seen), writers * per_writer)

    def test_tamper_breaks_chain(self):
        l1_compile.compile_transcript(TRANSCRIPT, ledger_dir=self.d)
        path = self.d / "l1.jsonl"
        lines = path.read_text().splitlines()
        rec = json.loads(lines[1])
        rec["name"] = "forged-tool"
        lines[1] = hashchain.canonical(rec)
        path.write_text("\n".join(lines) + "\n")
        with self.assertRaises(ValueError):
            hashchain.verify(path)

    def test_golden_session_produces_expected_records(self):
        # scripted session: compile transcript (L1) + one lineage write (L3)
        l1 = l1_compile.compile_transcript(TRANSCRIPT, ledger_dir=self.d)
        write_with_lineage(self.d / "c.md", "x", VALID_SIDECAR, ledger_dir=self.d)
        self.assertEqual(len(l1), 3)
        self.assertEqual(hashchain.verify(self.d / "l1.jsonl"), 3)
        self.assertEqual(hashchain.verify(self.d / "l3.jsonl"), 1)


if __name__ == "__main__":
    unittest.main()
