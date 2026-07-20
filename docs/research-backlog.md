# Team OS — Research Backlog (open technical questions)

Living list of **technical / architecture research questions** deferred out of the current fork build but worth returning to. This complements two other lists:

- **Fork spec "Out of scope (mainline-deferred)"** (CLAUDE.md) — what the *plan* defers, by decision.
- **`positioning/research/`** — *market/competitive* research threads.

This file is for open **engineering/architecture** questions: things that are *possible* but not *now*, each with a provisional answer, the blocker, and the trigger that would make us pick it up. Append new entries; don't rewrite settled ones — supersede with a note.

| # | Topic | Status | Trigger to revisit |
|---|---|---|---|
| R1 | Isolated per-principal self-tuned model | open · deferred (mainline / confirmatory stage) | drafter quality plateaus AND retrieval/skill path exhausted AND an owned open-weights runtime exists |

---

## R1 — Isolated per-principal self-tuned (fine-tuned) model

**Status:** open, deferred. Architecturally compatible under strict conditions; out of current fork scope (needs infra + a model we control). Sits next to the fork spec's deferred *"Tier-3 pooled learning + DP"* — this is the **non-pooled** (per-principal, no cross-person) sibling, which is cleaner.

**The question.** Can Team OS incorporate a self-tuned model without breaking its invariants, if the model is *separated out and isolated per principal* rather than a shared artifact?

**Provisional answer: yes — but isolation alone isn't enough.** It becomes compatible only as an **isolated + draft-only + rebuildable-from-files** derived index. See the reasoning:

**What per-principal isolation fixes**
- Cross-principal leakage → solved (Alice's weights are hers, encrypted under her key, unreadable by others).
- Exit = clone → solved (the checkpoint is a file in her scope).
- No-individuation → fine (that invariant bans per-person *comparative* surfaces, not per-person possessions).
- Pooled-learning risk → sidestepped (no shared weights, so no differential-privacy requirement).

**What isolation does NOT fix (the hard two)**
1. **Datum-level unlearn** — you still can't surgically cut one document out of the weights.
2. **Datum-level lineage** — weights carry no source/evidence for a given behavior.

**The reframe that makes it compatible** — isolation + two rules:
1. **Draft-only.** The tuned model only *proposes*; the gate, lineage-tagged commit, and human acceptance stay deterministic. Then it is a *smarter drafter*, not "a model in the trust path" (SE-1/CN-2). Fine-tuning the drafter ≠ fine-tuning the commit path — the invariants only ever forbade the latter.
2. **Derived and rebuildable from files.** Per the invariant *"files are the system of record; databases and indexes are derived, rebuildable, never authoritative,"* **a fine-tuned model is just another index.** Checkpoint = content-addressed + a training manifest (base model, dataset-snapshot hash, hyperparams, time) → coarse lineage + rollback (revert = swap checkpoint). **Erasure = delete the datum from the files, then retrain/refresh from the clean set** — you don't unlearn, you rebuild a derived index the datum is no longer in.

**Caveats / open sub-questions**
- **Erasure latency** — between a deletion request and the next retrain, the removed datum still shapes outputs. Bound by refresh cadence, or train only on the principal's *own* data and never on erasable third-party data. Same family as mainline's deferred *datum-granular taint*.
- **Cost & control** — needs retraining infra *and* an open-weights model we run ourselves (can't fine-tune Claude, the runtime of record). This is the platform spend the fork exists to defer.
- **Poisoning** — a poisoned training set biases proposals; contained because the gate + human ✓ still filter every action (a biased drafter wastes proposals, can't act).
- **Probably unnecessary first** — retrieval + prompt-scoping over lineage-tagged files (already built) and transferable *skills* (FK7) compound governably at zero infra cost. Reach for tuning only if drafter quality plateaus and that path is exhausted.

**Revised rule of thumb (supersedes the blunt "never fine-tune"):** *don't put learning in the trust path, and don't let the model be authoritative.* An isolated, draft-only, rebuildable tuned model breaks neither — so it is a legitimate **mainline / confirmatory-stage** option, just not a now option.

**Related:** `review/2026-07-16-graphify-borrows.md` §3 (the "why not self-fine-tune" argument this refines); CLAUDE.md invariants (files-as-record, deletion, exit=clone, SE-1/CN-2, no-individuation); fork-spec deferred list (*Tier-3 pooled learning + DP*, *datum-granular taint*).
