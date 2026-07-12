**`v0.1 — 2026-07-12`** *(VISION — thesis-level; NOT governing, NOT driving FK work. Beyond the validated fork. Written to be on the record before it drifts. Precedence: below every doc in the fork spec's precedence order. Do not build from this without an explicit, separate scoping decision.)*

# Team OS — Emergence Architecture

> **Generate freely. Let it compound, let it go off the rails. Record everything.
> Study the trends. Keep the interesting-but-unproven as candidates. Unwind what
> turns out wrong. The only hard stops are on things you can't unwind.**

## 0. Status & scope

This is a **vision doc**, not a spec. It captures a design direction reached in
discussion. It is:

- **Beyond the validated fork.** The fork (FK1–FK8) validates a proactive,
  gated, on-the-record *personal* agent. This is a *new thesis* on top of that.
- **Density-gated.** Real emergence needs scale — many agents × many people ×
  a dense corpus. The *engine* is buildable now; the *payoff* is an FK7+ /
  multi-user property. At n≤3 you build the substrate and watch proto-emergence,
  not the real thing. Do not claim emergence at current scale.
- **A contrarian bet.** The market is fleeing autonomous agency — trust is
  falling, ~40% of agent projects are forecast dead by 2027, and the cause is
  emergent agency in the wild (agents doing unplanned things). Going *toward*
  emergence is the risk. The Observatory (§6) is what makes the bet defensible.

Nothing here overrides an invariant in `team-os-fork-harness-native.md` or the
architecture. Where this doc and a governing doc appear to conflict, the
governing doc wins and this doc is what needs revising.

## 1. Thesis

Most agent systems try to *prevent* emergence — bound the agent so it can never
surprise you. That kills the upside with the downside: a system that can't
surprise you can't discover anything either. So many inventions are accidents —
penicillin, vulcanized rubber, the microwave, Post-it notes — anomalies someone
**studied instead of discarded**.

Team OS can do the opposite, safely, because of one property nobody else has:
**it is built on a substrate that remembers and rewinds.** Files are the system
of record; every write carries lineage; git is the ledger. That means any
emergent branch of behavior can be *taken back, completely*. When unwind is
total and cheap, letting behavior run wild is not reckless — it is free.

The category: **the agent system that lets emergence run and can always take it
back — a lab, not a cage.**

## 2. The core principle — safety is unwind, not prevention

A brake that halts a compounding trend **destroys the thing you wanted to
study**. "Off the rails" is not a failure state to prevent; it is a *result to
observe and then judge from outcomes*. Pre-defining "off the rails" with
thresholds presumes you already know what is bad — the exact assumption that
kills discovery.

So the safety mechanism is not a governor that stops. It is the **guaranteed
ability to unwind**. Generate, let it play out, evaluate the *outcome*, keep
what proved good, revert what proved bad. Judgment comes *after*, from results —
never *before*, from rules.

## 3. The one line that defines the field — reversible vs. irreversible

The principle draws its own boundary. "It's ok *because it can be reversed.*"
That sentence is the architecture:

- **Where unwind exists → the playground.** Off-the-rails is welcome. Let it
  run, keep the receipts, rewind if it turns out wrong. Cost of a bad branch ≈
  the cost of reverting it ≈ zero (git + lineage *is* the rewind).
- **Where unwind does not exist → a proposal.** A sent email, a deleted record,
  spent money — already left the building. Not "stopped to be safe"; rather, the
  unwind principle simply *has no road there*. You cannot study-and-revert a
  thing you cannot rewind to compare against. So this narrow set stays a
  proposal a human ratifies.

This is not a brake re-imposed on the vision. It is the vision's own rule
running out of road.

## 4. The only governors that survive

Separate two things unwind treats differently:

- **Reversible artifacts** — a draft, a corpus write, a link, a skill fork, an
  internal proposal. Unwind recovers these fully. **No outcome-judging brake is
  allowed on them.** "This trend looks weird, halt it" is deleted.
- **Irreversible resource burn** — a runaway loop spawning subagents that spawn
  subagents burns tokens / compute / spend that unwind cannot refund. Here a
  brake is legitimate, because it protects something unwind *can't* recover.

**Clean line: brake irreversible cost, never reversible outcome.**

Legitimate governors (protect irreversible loss):
- spend / token caps,
- spawn-depth and spawn-rate bounds,
- the external-send / delete gate,
- the authenticated-consent line on autonomy widening (§7).

Deleted governors (pre-judge reversible outcomes):
- threshold "this is anomalous, stop,"
- decay-as-safety-brake (see §5 for what decay becomes instead),
- any rule that halts a trend because it looks unusual.

## 5. The engine — autocatalytic trails

Emergence needs a medium and a feedback loop. The medium is the shared store
(corpus + ledgers). The loop is **autocatalysis**, the ant-colony-optimization
dynamic:

- Agents deposit **typed trails** on the shared substrate as they work
  ("touched," "claimed," "needs-review," "worked-well").
- A trail that is **successfully reused is reinforced** — its weight grows, it
  pulls more agents onto the path. This is the compounding. Unplanned
  optimization emerges from local reinforcement; no orchestrator chooses it.
- A trail that goes **unused fades** — but *fading is not deletion*.

**Decay is reframed as archival forgetting.** An unused trail loses active
*influence* but stays in the record, fully observable. Nothing is destroyed; the
active system stays uncluttered while the trend stays studiable forever. You
lose nothing to look back on. (This is why decay is *not* a §4 governor — it
removes influence, never information.)

Compounding is the engine *and* the source of the interesting anomalies. It is
not the danger — under §2 there is no danger from a reversible trend, only data.

## 6. The Observatory — an instrument, not a guardrail

The Observatory does not stop anything. It is the laboratory bench.

- **It studies.** Trends are preserved in full, never truncated — a trend cut
  short cannot be learned from.
- **Its detector is a curiosity function, not an alarm.** It surfaces what is
  surprising, novel, or compounding *unexpectedly* — precisely *because* it is
  unexpected. A system tuned to suppress outliers is a system that cannot
  invent. The detector's bias is toward preserving anomalies.
- **Its output is a candidate, not a verdict.** Interesting-but-unverified is
  held for a human to examine — never auto-promoted, never auto-killed.
- **It notifies; the user decides.** The guardrail is not that it halts
  emergence. The guardrail is that *it sees emergence and tells you*, and unwind
  is always available if you don't like what you see.

Read-only, derived, rebuildable — same discipline as every other surface. What
it shows (topic clusters forming, skill ecology, self-organized division of
labor, cross-person knowledge that assembled itself) is structure **no one
authored**, even though every underlying write was authorized. Gated ≠ planned;
authorized ≠ authored. Emergence lives in that gap.

## 7. What stays hard-gated, and why it is not a contradiction

Two boundaries hold, and both are consistent with "study the trend, don't stop
it":

1. **The irreversible commit** (external send, delete, spend). Emergence still
   *flows* here — the trend "this agent keeps wanting to do X" is data, studied
   and surfaced like any other. Only the final irreversible *trigger* waits for
   a hand. Emergence is not suppressed at the boundary; it is *converted to a
   proposal a human ratifies*.
2. **Autonomy widening on authenticated consent only** (CN-1). An emergent trend
   may *propose* a wider envelope; only the principal's authenticated ✓
   *executes* it. This is security, not conservatism: drop it and an attacker
   seeds a trail, the trail compounds, and the envelope widens *itself* — the one
   third-party attack chain, reopened. Emergence proposes; authenticated human
   commits.

Everywhere else — the whole reversible interior — emergence runs free.

## 8. Why the invariants are enablers, not constraints

The invariants that look like limits are the two things that make "let it go off
the rails" a sane sentence:

- **Files are the system of record + git** = the total, cheap rewind. This is
  what makes unwind real.
- **Lineage on every write** = every emergent structure decomposes back into
  labeled, attributable steps. This is what makes emergence *studiable* — you can
  always ask "what produced this?" and get an answer.

Nobody else can say "let it go off the rails," because nobody else can unwind and
nobody else can explain what emerged. The safety and the emergence come from the
*same* substrate.

## 9. Open questions — what to validate before building

- **Resource-governor calibration.** Spend/spawn caps are the only interior
  brakes; where are they set, and are they truly outcome-blind (protecting cost,
  not judging behavior)?
- **Unwind completeness.** Is every interior action genuinely, *fully*
  reversible? Any action that is "reversible in principle" but leaves a residue
  (a cache, an external mirror, a notification already seen) is secretly at the
  boundary and must be treated as §3-irreversible. Audit for hidden residues.
- **Candidate volume.** At density, the curiosity function could produce more
  candidates than a human can study. What is the triage — and does triage
  re-introduce a suppression bias the whole design rejects?
- **Density threshold.** How much scale before emergence is real and not
  proto-noise? This is the FK7+ gating question.
- **The contrarian bet.** Does "emergence you can always take back" actually
  move buyers who are currently *fleeing* autonomy — or does the word
  "emergence" scare them regardless of the unwind guarantee? Positioning test.

## 10. Relationship to the fork

- The **autocatalytic trail engine** (§5) is a near-term, buildable primitive
  that is useful *even with no emergence* — stigmergic coordination is real
  product at any scale. It could be scoped as a fork-adjacent item.
- The **Observatory** (§6) earns its keep only at density; it is FK7+ / v2.
- The **hard gates** (§7) already exist — this doc changes nothing about them; it
  only clarifies that they are the *boundary*, and the interior is free.

This doc is the record of the direction. It drives no work until a separate,
explicit scoping decision promotes a piece of it into the build order.
