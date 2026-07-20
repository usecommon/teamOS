"""Local, deterministic file->markdown extraction (markitdown adapter, FK4).

Turns a real footprint (PDF/Office/HTML/CSV/JSON/email) into markdown the
compiler already ingests. STRICT guardrails (see review/2026-07-19-markitdown-fit.md):
  - LOCAL + deterministic only: convert_local(), never convert_response().
  - NO llm_client (a model in the extraction path violates SE-1/CN-2).
  - NO plugins, NO Azure/cloud, NO network transcription.
An extracted item is lineage-tagged basis=extracted, transformation=markitdown-<ext>.
markitdown is an OPTIONAL dependency; absent it, the markdown-only path is unchanged.
"""
from pathlib import Path

# formats markitdown parses with LOCAL, deterministic libraries (no cloud/LLM)
LOCAL_EXTS = {".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".html", ".htm",
              ".csv", ".json", ".xml", ".epub", ".msg", ".txt"}


def available():
    """True if markitdown is importable (optional dependency)."""
    try:
        import markitdown  # noqa: F401
        return True
    except Exception:
        return False


def _default_converter():
    """Local-only converter: plugins off, and NO llm_client is ever passed."""
    from markitdown import MarkItDown
    return MarkItDown(enable_plugins=False)


def _text(result):
    return getattr(result, "markdown", None) or getattr(result, "text_content", "") or str(result)


def extract(path, converter=None):
    """Convert one LOCAL file to markdown, deterministically. `converter` must
    expose convert_local(path)->result — the narrowest markitdown API for
    untrusted local files. Never wires an LLM or the network."""
    conv = converter or _default_converter()
    return _text(conv.convert_local(str(path)))


def transformation_for(path):
    return "markitdown" + Path(path).suffix.lower()
