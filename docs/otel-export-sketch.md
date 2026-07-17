**`v0.1 — 2026-07-16`** *(SKETCH — a design note, NOT built. Shows how Team OS ledgers feed existing observability tools via OpenTelemetry so we interoperate instead of rebuilding LangSmith/Langfuse/Arize. Status: Vision. See `positioning-vs-landscape.md` §"Visualization & observability".)*

# OpenTelemetry export — ledger → trace tree

## Stance

The ledgers are the **source of truth**; an OTel trace is a **derived, rebuildable
view** — like every index in Team OS. Export is **one-way and read-only**: it reads
the ledgers and emits spans; it never writes a ledger and never sits in the commit
path. This lets users bring **Langfuse / Arize / LangSmith / any OTLP backend** to
Team OS for deep debugging, while the hash-chained ledger stays authoritative.

Key inversion vs. telemetry-first tools: for LangSmith/Langfuse the *trace is the
record* (sampled, lossy — drop a span, lose the truth). Here the **ledger is the
record**; OTel is a lossy *projection*, and losing a span loses nothing, because the
truth is reconstructible from the chain.

## Mapping — ledger event → OTel span

| Ledger source | OTel construct | Key attributes |
|---|---|---|
| A run / loop pass / session | **trace** (`trace_id`) | `run_id`, `posture` |
| `spawns.jsonl` spawn (parent→child) | **span**, nested under parent's span | `agent.id`, `agent.type` (agent/sub), `spawn.depth`, `task`, `status` |
| Denied spawn (depth/rate bound hit) | span with `status=ERROR` + event `spawn.denied` | `reason` (e.g. `MAX_DEPTH=3`), `bound` |
| `l2.jsonl` gate decision | **span event** on the acting agent's span | `verdict`, `rule_id`, `action_class`, `target`, `findings` |
| `l7.jsonl` score | span attribute / event | `skill_id`, `skill_version`, `metric`, `score` |
| `l3.jsonl` lineage write | span event `corpus.write` | `source_type`, `transformation`, `confidence` |
| `l8.jsonl` signal (✓/✗) | span event `signal` | `signal_type`, `attribution` |

Span start/end come from ledger `ts`. Parent/child nesting comes straight from
`spawns.jsonl` — the tree is already in the data (§ the spawn ledger *is* a tree).

## Thin exporter (sketch — not built)

```python
# scripts/otel_export.py  (SKETCH)
# Read-only, deterministic, no model. Reads ledgers -> emits OTLP spans.
import json
from pathlib import Path
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def _read(p):
    p = Path(p)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []

def export(ledger_dir, endpoint):
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    tracer = provider.get_tracer("teamos")

    spawns = _read(Path(ledger_dir) / "spawns.jsonl")
    gate   = _read(Path(ledger_dir) / "l2.jsonl")

    # build spawn tree: parent id -> children
    by_parent, spans = {}, {}
    for s in spawns:
        by_parent.setdefault(s["parent"], []).append(s)

    def emit(agent_id, parent_ctx):
        for s in by_parent.get(agent_id, []):
            with tracer.start_as_current_span(s["child"], context=parent_ctx) as span:
                span.set_attribute("agent.type", "sub")
                span.set_attribute("spawn.depth", s["depth"])
                span.set_attribute("task", s["task"])
                if s.get("denied"):
                    span.set_status(trace.StatusCode.ERROR)
                    span.add_event("spawn.denied", {"reason": s.get("reason", "bound")})
                # gate decisions attributed to this agent become span events
                for g in gate:
                    if g["proposed_action"].get("agent") == s["child"]:
                        span.add_event("gate", {"verdict": g["verdict"], "rule": g["rule_id"]})
                emit(s["child"], trace.set_span_in_context(span))   # recurse -> nested tree

    root_agents = {s["parent"] for s in spawns} - {s["child"] for s in spawns}
    for a in sorted(root_agents):
        with tracer.start_as_current_span(a) as root:
            root.set_attribute("agent.type", "agent")
            emit(a, trace.set_span_in_context(root))
    provider.force_flush()
```

*(Illustrative — field names track the schemas in `docs/schemas/`; a real version
would batch-tail the ledgers and reconcile against the hash chain.)*

## Invariant compliance & honest caveats

- **Read-only / deterministic / no model.** The exporter reads ledgers and emits
  spans — it never writes a ledger, never runs a model, and is not in the commit
  path. Consistent with SE-1/CN-2 and files-as-truth.
- **The OTLP endpoint is egress — so it crosses the boundary.** Sending trace data
  to an external observability SaaS is a *send* (§4 irreversible: disclosure). It
  must pass the gate and the user's **allow policy**; the endpoint is allow-listed
  by the user, and trace payloads carrying content/PII are **scrubbed or the export
  is denied by default**. Governance-neutral: the user chooses the backend and what
  leaves.
- **Lossy by design, and that's fine.** Sampling or a dropped span loses nothing
  authoritative — the ledger remains the record and the trace is rebuildable. The
  opposite of telemetry-first tools.
- **Direction of dependency.** Team OS depends on no observability vendor; any OTLP
  backend is optional and swappable. This keeps the vendor-independence line intact
  (`positioning-vs-landscape.md` §Rebuttal).

## Why this is the right move

Rebuilding LangSmith/Langfuse is a losing use of effort — they are mature and
better at debugging than anything we would ship. Emitting OTel makes Team OS the
**governed, auditable spine** that feeds them: users get best-in-class trace tooling
for free, and the hash-chained ledger stays the source of truth. Interop, not
reinvention.

## Status

Vision / sketch. Not scoped to build. If promoted: one thin script
(`scripts/otel_export.py`), the OTLP endpoint as an allow-listed egress, and a
config toggle. No change to the ledgers or the gate.
