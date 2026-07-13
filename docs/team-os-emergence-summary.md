# Team OS — Emergence Architecture, in plain language

*A one-page reader for the full spec at [`team-os-emergence-architecture.md`](./team-os-emergence-architecture.md) (v0.6). Vision, not yet a build spec.*

---

## The idea in one line

**Let the agents surprise you — and be able to see everything, take back what's reversible, and stop nothing at the door except what you haven't explicitly allowed.**

Most agent products try to *prevent* surprise (bound the agent so it can never do anything unplanned). That kills the upside with the downside — a system that can't surprise you can't discover anything. Team OS goes the other way: it lets emergent behavior run, because it sits on a substrate (plain files + git + lineage) that can **see and rewind**.

## Why we can do this when others can't

- **Files are the system of record; git is the ledger.** Anything reversible can be taken back, completely and cheaply.
- **Every write carries lineage.** You can always ask "what produced this?" and get an answer. Emergence is *studiable*, not a black box.

Those two properties are what make "let it go off the rails" a sane sentence.

## The one distinction everything rests on

**Reversible vs. irreversible.**

- **Reversible (the interior):** private drafts, corpus writes, internal proposals, agents coordinating. If it's wrong, undo it. Here emergence runs free and is *observed*, not gated.
- **Irreversible (the boundary):** sent email, spent money, deleted data, disclosed information, anything a third party saw. You can't take these back. Here we don't observe — we **prevent**.

## Safety, honestly stated

Safety is **the ability to unwind — limited.** Unwind is total for private, fresh, uncoupled work; it fades once other agents act on it, and it's void for irreversible things. So:

- **Where unwind reaches → that's the safety.** Let it run, study it, revert what's wrong.
- **Where it doesn't → prevention.** The boundary.

**Observability is not the safety — it's what makes safety possible** (you can only unwind what you can see) **and it's the promise:** *nothing happens invisibly.* Not "the agent never errs," but "no error is silent — you'll see every one, with the receipts, and hold the switch."

## The boundary: deny-by-default (the key decision)

We do **not** try to *detect harm* at the boundary — that needs a language model making semantic judgments, which is forbidden in the gate, and novel harm has no pattern to match anyway. Instead we flip it:

> **The boundary permits only what's explicitly allowed, and denies everything else.** Allowlist, not blocklist. It never asks "is this bad?" — only "is this on the allow list?" — which is deterministic and needs no model.

- **The allow policy is an editable markdown file the user owns.** Default: **empty** — so every irreversible act needs an explicit human confirmation. Safe *and* neutral: the tool ships no opinion of harm, only "irreversible things need explicit say-so."
- The user can pre-authorize (populate the allowlist) to remove friction — that's their owned choice.

**The one guarantee we'll stand behind (and that a deployment could *violate*):**

> No irreversible action ever occurs without either an allow-policy match or a human confirmation — and every one has a pre-act record. If one ever does, that's a bug, not an acceptable residual.

Everything else in the design is best-effort. This one isn't.

## How emergence is generated and watched

- **Autocatalytic trails.** Agents leave typed marks in the shared store; marks that get reused strengthen (compounding), unused ones fade. Unplanned coordination emerges from local reinforcement — no orchestrator. Fading = archived, not destroyed; still studiable.
- **The Observatory.** A read-only surface that *studies* emergence and *curates* the allowlist. Two advisors: a **curiosity detector** (surface the novel/interesting) and a **concern detector** (surface the worrying). They only *propose* — a human decides. They may use a read-only model to reason; they never sit in the gate.
- **You decide on candidates.** Promote it, keep watching it, or unwind it.

## The user is always in control

Three modes, the user's choice (default is the safest):

| Mode | What's automatic | Boundary |
|---|---|---|
| **Review** (default) | nothing — you approve each graduation | deny-by-default |
| **Auto-approve interior** | reversible work graduates automatically | still deny-by-default |
| **Auto-approve all** | full autonomy within your cost ceilings | your pre-set allowlist |

Non-negotiable in every mode: **observability stays on**, the **deny-by-default boundary + guarantee** holds, and **cost ceilings** bind. Honest caveat: auto-approve-all is the hatch back to an unsupervised agent — the design surfaces that risk; it's the user's owned choice, never the default.

## Deletion (right to be forgotten) on an un-rewritable record

The record is append-only and hash-chained — rewriting it breaks the tamper-evidence. So to delete, **destroy the encryption key** (key-destruction erasure; "crypto" = cryptography, not coins). The encrypted bytes stay (chain intact, structure survives as a tombstone); the content becomes permanently unreadable. Keys are **per data-subject** so one person can be erased without nuking the rest; erasure **propagates** to derivatives that still carry their data; the deletion is itself recorded. **Line: structure durable, content erasable.**

## What's honest about the limits

- This is a **new thesis beyond the current build**, and real emergence is **density-gated** — it needs many agents × many people × a dense corpus. At small scale you build the engine and watch proto-emergence, not the payoff.
- The **concern detector is best-effort** (it can miss things) — which is exactly why safety rests on the deterministic deny-by-default boundary, not on the detector.
- **Auto-approve-all** is a real strategic risk, surfaced not solved.
- It's a **contrarian bet** — the market is currently fleeing autonomous agency; the wager is that "emergence you can see, bound, and take back" is different enough to matter.

## Status

Vision doc. It drives no build work until a separate scoping decision promotes a piece of it. The near-term, buildable piece is the **deny-by-default boundary + allow policy** (deterministic, no density needed); the Observatory earns its keep later, at scale.
