# Graphify borrows — implemented + why we don't self-fine-tune

- **Date:** 2026-07-16
- **Source:** github.com/Graphify-Labs/graphify (README, ARCHITECTURE.md)
- **Status:** 4 of 5 borrows landed in code + tests (250 pass, mapping GATE PASS); 1 is a reference note (below).

---

## 1. What landed

| Borrow | Where | Status |
|---|---|---|
| **`extracted` / `inferred` / `ambiguous` edge tag** | `lineage-sidecar.schema.json` (optional enum on each source edge + entity-level), `l3_writer.entity_basis`/`edge_basis` (weakest edge wins; missing → ambiguous), `gate_processor` sets it (skill=inferred, door=ambiguous), `adapter/mapping.yaml` (fork-native) | ✅ + tests |
| **Provenance-peek shows the tags** | `review/2026-07-14-viz-gallery-2.html` DAG — edges colored extracted/inferred/ambiguous, ambiguous dashed | ✅ |
| **"No model in the trust path" said out loud** | `README.md` opening | ✅ |
| **Honest efficiency metric** | `measurement.context_efficiency` — raw-read vs compiled tokens, labelled an estimate not a benchmark | ✅ + test |
| **"Surprises / questions" framing** | `day_one_brief.assemble_brief` (`_surprises`, `_questions`, deterministic) + `render_dm` | ✅ + test |
| **SKILL.md + `hook install` as a kit reference** | this doc, §2 | reference note (FK6c is future scope) |

Two of these touch protected paths and **need human review before merge**: `adapter/mapping.yaml` (added `basis` to the `sidecar-writer-supplied`, fork-native group) and the `docs/schemas/` contract change. Both are additive and backward-compatible (optional field, missing → ambiguous), and the FR1 mapping gate passes.

The `basis` semantics chosen:
- **extracted** — read directly / verbatim from an authenticated source.
- **inferred** — resolved / derived by the agent.
- **ambiguous** — uncertain; routes to human review. Door/untrusted content defaults here, and the existing human-approval step for schedule/skill proposals *is* the ambiguous→review route (T9).

---

## 2. FK6c kit reference — Graphify's packaging mapped to ours

Graphify ships as harness-native primitives, the same shape FK6c targets. Concrete borrows for the kit build:

| Graphify | Mechanism | FK6c analogue / lesson |
|---|---|---|
| `/graphify` slash command + a single `SKILL.md` | One skill file as the entry; manual install = copy to `~/.claude/skills/graphify/` | Keep one SKILL.md per capability as the discoverable entry; the kit's install is a copy-to-`~/.claude` step, not a framework. |
| `graphify hook install` (post-commit) | One command wires the git hook | **Add `teamos install`** that merges `hooks/settings-fragment.json` into `.claude/settings.json` — today `teamos doctor` only *tells* the user to do this by hand. A one-command gate-install is a direct, cheap win. |
| `--mcp` stdio server | Single flag serves the tool over MCP | The FK6c minimal door (`door.py`) served behind one flag; `propose_*` → inbox only. |
| `--update` + SHA256 cache | Re-extract only changed files, merge | Incremental compile: recompile only changed footprint items; keep the graph fresh without a full rebuild. |
| Multi-format export (Obsidian, GraphML, JSON) | Derived, portable | Reinforces exit=clone; low-cost export formats make the "you own it" story tangible. |

**The discipline to copy:** stateless stages, "no side effects outside the out-dir," schema-validated before consumption. We already hold this (files-as-record); Graphify is a clean reference implementation to diff our kit against.

---

## 3. Why Team OS must NOT self-fine-tune

Graphify does zero learning — it's a deterministic extractor. Team OS *does* adapt (acceptance → envelope, promotion, transfer), but that adaptation must live in **files and ledgers, never in model weights.** Fine-tuning would break the product at the level of its core invariants. The reasons, in priority order:

**1. A weight update is an unlabelled write — it violates lineage by construction.**
Every memory/corpus write must carry lineage (source, evidence, transformation, confidence/basis) or it is *rejected by construction* (CN-12). A fine-tune delta has no lineage: you cannot name the source, cite the evidence, or state the transformation behind a given weight change. Learning-into-weights is exactly the unlabelled write the whole substrate is built to refuse — at scale, and irreversibly.

**2. It defeats deletion and exit=clone — the killer for a *team* product.**
Deletion must remove content (L9); a leaver's `git clone` carries only their own decryptable scope; per-principal stores are never readable by others. **You cannot crypto-shred one colleague's data out of a fine-tuned model.** Their contribution is baked into a shared, opaque artifact forever. This breaks GDPR erasure and per-principal isolation the moment real others' data is ingested — which is precisely the stage the fork is built to reach safely.

**3. It puts a model in the trust path — the one thing SE-1/CN-2 forbid.**
No language model sits in the evidence or commit path; a model only drafts. Fine-tuning *makes the model the store*: an opaque, non-deterministic evidence path. Poisoned or prompt-injected data would be laundered into weights, undetectable and un-attributable. The deterministic, inspectable commit path — the thing that lets us say "you always know what was recorded and why" — collapses.

**4. It isn't reversible or auditable — it breaks undo, rollback, and the envelope.**
Adaptation in Team OS is a ledgered number in a file you can read and revert: git-backed skill versions (L6), the envelope level in JSON, `teamos undo`, `teamos envelope reset`. A weight update is not byte-diffable, not cheaply revertible to a prior version, not inspectable. Every control a nervous user reaches for stops meaning anything.

**5. It industrializes Goodhart, and it individuates.**
Fine-tuning on the acceptance signal would optimize the model to produce whatever earns a ✓ — Goodhart on the exact metric we already guard against padding. And a per-person fine-tune is an individuation surface by construction, which the no-individuation invariant forbids.

**6. It's unnecessary — files already give compounding, governably.**
The thesis is that improvement lives in files: versioned skills, corpus, profile, earned autonomy. A skill that improves and *transfers to another person* (FK7) is the compounding mechanism — and it compounds precisely because it's a file: inspectable, promotable via PR+CI, revertible, transferable. Fine-tuning would trade all of that for a marginal, opaque quality bump.

**7. It's the platform spend the fork exists to defer — on a model we don't even own.**
The fork runs on the harness's own inference. Fine-tuning means owning training infra and a model lifecycle — the exact platform cost the fork avoids until the thesis is proven — and in the runtime of record you'd be trying to tune a model you don't control.

**The line to hold:** *learning that changes a file is in; learning that changes a weight is out.* If model-level personalization is ever wanted, the governable form is retrieval / prompt-scoping over lineage-tagged files (which we already do) — never gradient updates. "Self-improving" for Team OS means the skills, memory, and autonomy get better on the record, not that the model quietly rewrites itself.

**Corollary — isolated per-principal tuning.** There *is* a compatible form: an **isolated + draft-only + rebuildable-from-files** tuned model (per principal, encrypted, only *proposing*, rebuilt from the lineage-tagged corpus so erasure = delete-from-files-then-retrain). That converts fine-tuning from "forbidden" to "just another derived index," at the cost of infra + a model we control. Logged as a research topic: **`docs/research-backlog.md` §R1** (mainline / confirmatory-stage, not now).
