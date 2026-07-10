"""F-tests for the docs/schemas contracts: meta-validity, fixture acceptance,
and rejection of lineage-incomplete objects (the invariant, tested)."""

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from jsonschema import ValidationError  # noqa: E402

import validate_schemas  # noqa: E402
from schema_registry import validator_for  # noqa: E402

VALID_SIDECAR = {
    "entity_id": "individual/example",
    "generated_by": {"transformation": "adapter-translation", "at": "2026-07-10T00:00:00Z"},
    "agent": "teamos-adapter/0.1",
    "sources": [
        {
            "source_type": "harness-artifact",
            "locator": "/fixtures/example.md",
            "content_hash": "sha256:abc",
        }
    ],
    "evidence": ["/fixtures/example.md"],
    "confidence": "high",
    "update_history": [],
}


class SchemaSuite(unittest.TestCase):
    def test_all_schemas_valid_and_refs_resolve(self):
        self.assertEqual(validate_schemas.main(), 0)

    def test_valid_sidecar_accepted(self):
        validator_for("lineage-sidecar.schema.json").validate(VALID_SIDECAR)

    def test_sidecar_missing_any_lineage_field_rejected(self):
        # An unlabelled write is rejected by construction: every load-bearing
        # lineage field is required, so dropping any one fails validation.
        validator = validator_for("lineage-sidecar.schema.json")
        for field in ["sources", "evidence", "confidence", "agent", "generated_by", "update_history"]:
            broken = {k: v for k, v in VALID_SIDECAR.items() if k != field}
            with self.assertRaises(ValidationError, msg=f"missing {field} must reject"):
                validator.validate(broken)

    def test_stores_manifest_conforms(self):
        manifest = json.loads((REPO_ROOT / "stores" / "manifest.json").read_text())
        validator_for("stores.schema.json").validate(manifest)
        by_id = {s["store_id"]: s for s in manifest["stores"]}
        self.assertEqual(len(by_id), 5)
        self.assertTrue(by_id["personal_memory"]["encrypted"])

    def test_corpus_entry_schema_stores_no_backlinks(self):
        # arch §3.3.1: links computed, never stored — the contract must not
        # grow a stored-backlink field without tripping this.
        schema = json.loads(
            (REPO_ROOT / "docs" / "schemas" / "corpus-entry.schema.json").read_text()
        )
        for forbidden in ("backlinks", "links", "graph"):
            self.assertNotIn(forbidden, schema["properties"])


if __name__ == "__main__":
    unittest.main()
