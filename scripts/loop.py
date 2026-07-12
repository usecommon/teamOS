"""Class A loop (FK6) — path (a), the runtime of record. A scheduled headless
run produces a daily digest + >=3 compiled recurring deliverables as SHADOW
drafts (designed capacity 4+ vs floor 3, CN-6), scores each into L7, and anchors
the chain heads off-box. Multi-step and checkpointed: a kill mid-run resumes
from the last checkpoint (FR4). Deterministic core; the A-A4 clock measures on
top.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anchor  # noqa: E402
import measurement  # noqa: E402
import safety_agent  # noqa: E402
from checkpoint import run_checkpointed  # noqa: E402

DELIVERABLE_CAP = 4  # designed capacity > floor of 3 (CN-6)
REPO_ROOT = Path(__file__).resolve().parent.parent


class LoopHalted(RuntimeError):
    pass


def _render_shadow_draft(node, out_dir):
    path = Path(out_dir) / "deliverables" / f"{node['task_type']}-shadow.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# {node['task_type']} (shadow draft)\n\n"
        f"cadence: {node['cadence']}\nsource: {', '.join(node['sources'])}\n"
        f"built from {node['occurrences']} exemplars.\n")
    return str(path)


def run_daily_loop(job_graph, out_dir, ledger_dir, anchor_dir, run_id,
                   skill_id="compile", skill_version=None, checkpoint_path=None,
                   safety_check=True):
    """Run one loop pass. Returns a manifest. Resumable via checkpoint_path.
    Pre-flight (T9): the safety agent runs FIRST — a threshold breach trips
    the breaker and halts the loop before any side effect."""
    out_dir = Path(out_dir)
    ledger_dir = Path(ledger_dir)
    if safety_check:
        breaker = os.environ.get("TEAMOS_BREAKER",
                                 str(REPO_ROOT / "ledgers" / "breaker.json"))
        verdict = safety_agent.check(ledger_dir, ledger_dir / "safety.jsonl",
                                     breaker)
        if verdict["status"] == "tripped":
            raise LoopHalted(
                f"safety agent tripped the breaker: {verdict['breaches']}")
    checkpoint_path = checkpoint_path or (out_dir / f"{run_id}.checkpoint.json")
    skill_version = skill_version or measurement.l6_version(
        Path(__file__).resolve().parent.parent / "stores" / "skills" / "compile")

    nodes = job_graph.get("nodes", [])
    targets = nodes[:DELIVERABLE_CAP]

    steps = [("digest", lambda _r: {"lines": len(nodes)})]
    for node in targets:
        def make(_r, node=node):
            path = _render_shadow_draft(node, out_dir)
            rec = measurement.score_deliverable(
                path, skill_id, skill_version,
                invocation_id=f"{run_id}:{node['task_type']}", ledger_dir=ledger_dir)
            return {"path": path, "score": rec["score"], "l7_hash": rec["hash"]}
        steps.append((f"deliverable:{node['task_type']}", make))
    steps.append(("anchor", lambda _r: anchor.anchor_heads(ledger_dir, anchor_dir, run_id)))

    results = run_checkpointed(steps, checkpoint_path)
    deliverables = {k: v for k, v in results.items() if k.startswith("deliverable:")}
    return {
        "run_id": run_id,
        "deliverables": deliverables,
        "count": len(deliverables),
        "anchor": results.get("anchor"),
        "skill_version": skill_version,
    }
