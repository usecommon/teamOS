"""FK4 extraction adapter (markitdown): local-only, deterministic, no LLM.
Uses a fake converter so the adapter logic is tested without the optional dep;
a real end-to-end runs only when markitdown is installed."""
import inspect
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import extract  # noqa: E402
import compile_footprint as cf  # noqa: E402


class FakeConverter:
    """Stand-in markitdown: records that the NARROWEST API (convert_local) was used."""
    def __init__(self):
        self.local_calls = []

    def convert_local(self, path):
        self.local_calls.append(path)
        name = Path(path).name
        return type("R", (), {"text_content": f"# extracted {name}\n\ndeliverable_type: doc\n"})()


class ExtractionAdapter(unittest.TestCase):
    def test_missing_dir_returns_empty_not_crash(self):
        # regression: iterdir() raises on a missing dir where glob returned []
        items = cf.load_footprint(Path(tempfile.gettempdir()) / "teamos-does-not-exist-xyz")
        self.assertEqual(items, [])

    def test_default_is_markdown_only(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            (d / "a.md").write_text("---\ndeliverable_type: x\n---\nhi\n")
            (d / "b.pdf").write_bytes(b"%PDF-1.4 fake")
            items = cf.load_footprint(d)  # no extract flag
            self.assertEqual(len(items), 1)
            self.assertTrue(items[0]["path"].endswith("a.md"))

    def test_nonmd_extracted_when_enabled(self):
        fake = FakeConverter()
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            (d / "a.md").write_text("md\n")
            (d / "b.pdf").write_bytes(b"x")
            (d / "c.docx").write_bytes(b"x")
            items = cf.load_footprint(d, extract_nonmd=True, converter=fake)
            self.assertEqual(len(items), 3)
            pdf = [i for i in items if i["path"].endswith(".pdf")][0]
            self.assertIn("extracted b.pdf", pdf["content"])
            self.assertEqual(pdf["provenance"]["extracted_via"], "markitdown.pdf")
        # the narrowest, local API was used for each non-md file (never a network call)
        self.assertEqual(len(fake.local_calls), 2)

    def test_no_llm_client_and_no_plugins_by_construction(self):
        # guardrail: the default converter never PASSES an llm_client kwarg
        # (a bare mention in the docstring is fine; the wiring is what matters).
        src = inspect.getsource(extract._default_converter)
        self.assertNotIn("llm_client=", src)
        self.assertIn("enable_plugins=False", src)

    @unittest.skipUnless(extract.available(), "markitdown not installed (optional dep)")
    def test_real_markitdown_html(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "x.html"
            p.write_text("<h1>Hello</h1><p>world</p>")
            md = extract.extract(p)
            self.assertIn("Hello", md)


if __name__ == "__main__":
    unittest.main()
