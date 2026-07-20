# markitdown — fit for Team OS file extraction

- **Date:** 2026-07-19 · **Ref:** github.com/microsoft/markitdown (MIT, Python 3.10+, AutoGen team)

## Verdict: high fit for local deterministic extraction — use it, with the LLM/cloud features OFF.

markitdown converts PDF / Word / PowerPoint / Excel / HTML / CSV / JSON / XML / ZIP / EPub / Outlook `.msg` / images / audio → **Markdown**, and — critically for us — **its core conversions run offline with standard libraries, no network, no LLM.** Our compiler already speaks markdown and our stack is Python 3.10+, so this is the natural way to extend ingestion from "markdown fixtures only" to a **real footprint**.

## Where it plugs in — one place

`compile_footprint.load_footprint()` today only globs `*.md`. markitdown becomes a **deterministic pre-step**: real files → markdown → the existing distill/quarantine/exemplar path unchanged. That's the whole integration surface. It directly unblocks the #1 gap from the status check — **FK4/FK5 need a real footprint**, and this is how a real footprint (PDFs, docs, spreadsheets, emails) gets in.

## Why it fits the architecture (better than Graphify's approach)

- **Deterministic + local by default** → satisfies SE-1/CN-2 ("no model in the evidence or commit path"). Graphify uses an LLM for docs/PDF/images; markitdown does the same formats **deterministically**, so extraction stays out of the trust path.
- **Lineage-clean.** A markitdown-extracted item is legitimately tagged `basis: extracted`, `transformation: markitdown-<format>`, `source_type: connector:local-folder`. It slots straight into the L3 lineage we just sharpened.
- **MIT + markdown output** → drops in; minimal surface.
- **Narrowest-API guidance** (`convert_local()` / `convert_stream()`) matches our taint posture: footprint content is **untrusted** and must still pass the imperative-quarantine before becoming an exemplar (the sim confirmed that guard works).

## Guardrails — the parts to keep OFF (invariant lines)

1. **Never pass `llm_client`/`llm_model`.** markitdown's optional image/pptx "descriptions" put a model in the extraction path — that's *inference*, not extraction (`basis: inferred/ambiguous`), and it violates SE-1/CN-2 if it feeds the corpus. If image content is ever needed, it's a labeled, out-of-trust-path step, never silent.
2. **Azure Doc Intelligence / Content Understanding = network egress.** These ship document content to a cloud processor — a data-exfil path and a DSAR/erasure concern. Off by default; if ever enabled, it's a configured connector under the gate's egress rules + FK3b credential domains, not a library default.
3. **YouTube / audio transcription = network + external content.** Off; if used, treat the result as an untrusted external source (taint).
4. **Plugins off by default (keep them off).** Third-party code on the principal's files.
5. **Parser safety + dependency surface.** markitdown runs as a library *inside* the compile process, so it bypasses the gate hook (which governs tool calls, not in-process parsing). Untrusted PDFs/ZIPs/XML are a real attack surface (zip bombs, XXE, malicious embeds), and it pulls transitive deps (pdfminer, python-docx, openpyxl…). Mitigate: `convert_local()` only, size caps, run inside the gated compile step, vet/pin the dependency set, and rely on the post-extraction quarantine as the backstop.

## How much can we use it — scope

| Use | Verdict |
|---|---|
| Local extraction of the footprint (PDF/Office/HTML/CSV/JSON/email → md) | ✅ Use — deterministic, lineage-clean, unblocks a real footprint |
| Feeding extracted text into the existing compile/quarantine/exemplar path | ✅ Use — one pre-step in `load_footprint`, no downstream change |
| LLM image/pptx descriptions | ❌ Off — model in the trust path |
| Azure Doc Intelligence / Content Understanding | ❌ Off by default — network egress; only ever as a gated connector |
| YouTube/audio network transcription | ❌ Off — network + untrusted |
| Plugins | ❌ Off — untrusted third-party code |

## Recommendation

Add markitdown as an **optional, local-only extraction adapter** in front of `load_footprint` (feature-flagged; markdown-only path stays the default so CI/fixtures are unaffected). Label everything it produces `basis: extracted` / `transformation: markitdown-<format>`. This is the cheapest way to run the compiler on your **actual** work — which is the prerequisite for starting the A-A4 clock on a real footprint. It also strengthens the positioning line: like Graphify we reject embeddings, but unlike Graphify our doc/PDF extraction is **deterministic** (no model in the evidence path), which markitdown makes possible.
