**`v0.3 — 2026-07-12`** *(VISION — thesis-level; NOT governing, NOT driving FK work. Beyond the validated fork. Written to be on the record before it drifts. Precedence: below every doc in the fork spec's precedence order. Do not build from this without an explicit, separate scoping decision.)*

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
  emergence is the risk. The Observatory (§7) is what makes the bet defensible.

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

## 2. The core principle — safety is observability; unwind is a decision on candidates

A brake that halts a compounding trend **destroys the thing you wanted to
study**. "Off the rails" is not a failure state to prevent; it is a *result to
observe and then judge from outcomes*. Pre-defining "off the rails" with
thresholds presumes you already know what is bad — the exact assumption that
kills discovery. So the safety mechanism is not a governor that stops.

But it is not "unwind," either — unwind is not a guarantee you can make. In a
live, coupled system the clean rewind degrades the instant other agents read a
trail and act on it, and it is gone entirely for the things §4 catalogs. So the
always-on safety property is the one thing that does *not* degrade under
coupling or time:

**Safety is observability.** Every emergent act, every token burned, every
boundary-crossing is on the record and surfaceable — by construction (files as
truth + lineage). Nothing happens invisibly. That is the promise the system can
actually keep, and the honest one: *not "the agent never errs," but "no error is
silent — you will see every one, with the receipts, and hold the switch."*

**Unwind is demoted from guarantee to verb.** It is one option a human exercises
**at the candidate stage** — when the Observatory surfaces something to decide
on. Generate, observe, let the detector flag a candidate, then choose: promote,
keep watching, or unwind. Judgment comes *after*, from results — never *before*,
from rules. Unwind is real, but bounded (see the requirements below); it is a
move you make, not a net that is always under you.

### Safety splits at the reversibility line

Observability is *sufficient* safety only where the act is reversible. Watching
an irreversible act is not safety — it is forensics: the perfect audit log of a
crash whose passengers are still dead. So:

- **Interior (reversible): safety = observability + unwind-on-candidate.**
- **Boundary (irreversible, §4): safety = prevention** — the gate still stands
  ahead of the act. Observability is true inside and false at the door.

### The three standing requirements

For "safety is observability" to hold rather than degrade into excellent
post-mortems, three things are load-bearing — requirements, not nice-to-haves:

- **(a) Keep the boundary gate.** Irreversible acts (§4) are prevented, not
  merely observed. The gate does not go away; it is confined to the door.
- **(b) Two detectors, not one.** The Observatory needs a *curiosity* detector
  (surface the novel/surprising) **and** a distinct *harm / irreversibility*
  detector (surface the dangerous — especially the boring, slow, irreversible
  trail a curiosity detector ignores by design). Novel ≠ harmful; harmful ≠
  novel. See §7.
- **(c) Detection latency under the reversibility half-life.** Unwind-on-
  candidate only works if candidacy is caught while the rewind is still clean.
  Detect too slow and you are "unwinding" a thing that already coupled. For
  irreversible acts this collapses to (a): the harm detector must fire *ahead*
  of the trigger, which makes it a gate, not an observer.

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
running out of road. And that road ends in specific, nameable places — §4.

## 4. What cannot be unwound — the irreversibility catalog

Unwind is total for *state*. It is never total for a *live system*. The moment
you compute, communicate, or touch another party, something has already happened
that reverting the artifact does not take back. The reversible-interior claim
(§3) is about **results and state** — never about the **act of producing them**
or its **effects on the world**. You can unwind the result. You cannot unwind:

**Consumption — burned in the act, no refund on revert**
- Tokens / inference compute — spent the instant the model ran.
- Money, API spend, cloud cost.
- Rate-limit budget and quota.
- Wall-clock time, and the opportunity cost of it.
- Energy.

Every emergent exploration costs this *even if its output is reverted*. There is
a baseline irreversible price to emergence: the cost of thinking it. Emergence is
**reversible in artifact, paid-for in compute** — never free.

**Communication that left the system — a third party saw it**
- Sent email.
- Posted message, DM, chat.
- PR / issue comment, posted review.
- A notification already delivered — and read.
- Anything a human's eyes landed on: you can delete the message, not the memory.

**Third-party / external side effects**
- API calls that mutate external state — ticket created, order placed, webhook
  fired, CI kicked, deploy triggered.
- Payments, transactions, commitments.
- Pushes / edits to shared systems others have already pulled or acted on.
- Anything that starts a chain someone else acted on before you reverted.

**Disclosure — secrecy is a one-way door**
- A leaked secret / credential / PII — even deleted, it may be cached, indexed,
  screenshotted, scraped, or trained on. Disclosure cannot be recalled.
- Data sent to an external service that may retain, index, or learn from it.

**Destruction**
- Deleted or overwritten data with no backup and no version history. (With them,
  the backup *is* the unwind; without them, it is gone.)

**Perception & trust**
- The impression a human formed from an emergent action — a wrong draft they saw,
  a bad recommendation they read. Revert the artifact; you cannot revert their
  having seen it, or the trust it spent.

These classes are exactly what §5's cost governors and §8's hard gates protect.
This section is the *enumeration* of that boundary. Anything on this list is
either: (a) an accepted **baseline cost of exploring** (consumption), bounded by
a cost governor — never an outcome judge; (b) a **gated proposal** a human
triggers (sends, external mutations, deletion, disclosure); or (c) a **residue**
that secretly promotes a "reversible" action to the irreversible side, which the
§10 unwind-completeness audit exists to catch.

**Mistakes are mistakes — and mistakes can be discovery.** Because this is a live
system, some mistakes are permanent. Do not pretend otherwise: own the cost, log
it, keep the record honest. But irreversible ≠ worthless. The accident you cannot
take back may *be* the discovery — the contaminated dish was penicillin, the
melted bar was the microwave. An irreversible mistake is still **data**, and it is
studied, not just mourned. Serendipity never required reversibility; it requires
only that someone was paying attention when the mistake happened — which is
precisely what the Observatory (§7) is for.

## 5. The only governors that survive

Separate two things unwind treats differently:

- **Reversible artifacts** — a draft, a corpus write, a link, a skill fork, an
  internal proposal. Unwind recovers these fully. **No outcome-judging brake is
  allowed on them.** "This trend looks weird, halt it" is deleted.
- **Irreversible resource burn** — a runaway loop spawning subagents that spawn
  subagents burns tokens / compute / spend (§4) that unwind cannot refund. Here a
  brake is legitimate, because it protects something unwind *can't* recover.

**Clean line: brake irreversible cost, never reversible outcome.**

Legitimate governors (protect irreversible loss):
- spend / token caps,
- spawn-depth and spawn-rate bounds,
- the external-send / delete gate,
- the authenticated-consent line on autonomy widening (§8).

Deleted governors (pre-judge reversible outcomes):
- threshold "this is anomalous, stop,"
- decay-as-safety-brake (see §6 for what decay becomes instead),
- any rule that halts a trend because it looks unusual.

## 6. The engine — autocatalytic trails

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
lose nothing to look back on. (This is why decay is *not* a §5 governor — it
removes influence, never information.)

Compounding is the engine *and* the source of the interesting anomalies. It is
not the danger — under §2 there is no danger from a reversible trend, only data.

## 7. The Observatory — instrument and safety surface

The Observatory studies emergence; it also *is* the safety surface, because
safety is observability (§2) and this is where observability lives. That makes it
load-bearing — not a deferrable v2 nicety (see §11).

It runs **two detectors**, deliberately distinct:

- **Curiosity detector** — surfaces what is surprising, novel, or compounding
  *unexpectedly*, precisely *because* it is unexpected. A system tuned to
  suppress outliers cannot invent; this detector's bias is to *preserve*
  anomalies. This is the discovery half.
- **Harm / irreversibility detector** — surfaces what is *dangerous*, with the
  opposite bias: it must catch the **boring, slow, irreversible** trail the
  curiosity detector ignores. Novel ≠ harmful; harmful ≠ novel. It is
  latency-critical and boundary-facing — for irreversible acts (§4) it fires
  *ahead* of the trigger, i.e. it is the gate of §2(a)/(c), not a rear-view. This
  is the safety half.

Shared discipline across both:

- **It studies; it does not truncate.** Trends are preserved in full — a trend
  cut short cannot be learned from.
- **Its output is a candidate, not a verdict.** Interesting-but-unverified is
  held for a human — never auto-promoted, never auto-killed.
- **It notifies; the user decides** (promote / keep watching / unwind). The
  guarantee is not that it halts emergence — it is that *nothing emerges
  invisibly*, and the decision, and the switch, are yours.

Read-only, derived, rebuildable — same discipline as every other surface. What
it shows (topic clusters forming, skill ecology, self-organized division of
labor, cross-person knowledge that assembled itself) is structure **no one
authored**, even though every underlying write was authorized. Gated ≠ planned;
authorized ≠ authored. Emergence lives in that gap.

## 8. What stays hard-gated, and why it is not a contradiction

Two boundaries hold, and both are consistent with "study the trend, don't stop
it":

1. **The irreversible commit** (external send, delete, spend — §4). Emergence
   still *flows* here — the trend "this agent keeps wanting to do X" is data,
   studied and surfaced like any other. Only the final irreversible *trigger*
   waits for a hand. Emergence is not suppressed at the boundary; it is
   *converted to a proposal a human ratifies*.
2. **Autonomy widening on authenticated consent only** (CN-1). An emergent trend
   may *propose* a wider envelope; only the principal's authenticated ✓
   *executes* it. This is security, not conservatism: drop it and an attacker
   seeds a trail, the trail compounds, and the envelope widens *itself* — the one
   third-party attack chain, reopened. Emergence proposes; authenticated human
   commits.

Everywhere else — the whole reversible interior — emergence runs free.

## 9. Why the invariants are enablers, not constraints

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

## 10. Open questions — what to validate before building

- **Unwind completeness (the load-bearing risk).** Is every interior action
  genuinely, *fully* reversible? Any action "reversible in principle" that leaves
  a **residue** — a cache, an external mirror, a notification already seen, a
  downstream system that already read it — is secretly a §4-irreversible act and
  must be treated as boundary, not interior. Audit relentlessly for hidden
  residues; a leaky interior is how "safe emergence" quietly stops being safe.
- **Resource-governor calibration.** Spend / spawn caps are the only interior
  brakes; where are they set, and are they truly outcome-blind (protecting cost,
  not judging behavior)?
- **Consumption budget for emergence.** Since every exploration burns §4
  consumption even when reverted, what is the standing budget for "off the rails"
  compute — and who sets it? Emergence has a real, permanent price tag.
- **Candidate volume.** At density, the curiosity function could produce more
  candidates than a human can study. What is the triage — and does triage
  re-introduce a suppression bias the whole design rejects?
- **Density threshold.** How much scale before emergence is real and not
  proto-noise? This is the FK7+ gating question.
- **The contrarian bet.** Does "emergence you can always take back" actually
  move buyers who are currently *fleeing* autonomy — or does the word
  "emergence" scare them regardless of the unwind guarantee? Positioning test.

## 11. Relationship to the fork

- The **autocatalytic trail engine** (§6) is a near-term, buildable primitive
  that is useful *even with no emergence* — stigmergic coordination is real
  product at any scale. It could be scoped as a fork-adjacent item.
- The **Observatory** (§7) is now *load-bearing for safety*, not a density-gated
  nicety: because safety is observability (§2), its **harm-detector half must
  ship with the boundary gate, day one**. Its **curiosity half** — the discovery
  payoff — is what earns its keep only at density (FK7+ / v2). Split the two: the
  safety detector is near-term; the discovery detector is later.
- The **hard gates** (§8) already exist — this doc changes nothing about them; it
  only clarifies that they are the *boundary*, and the interior is free.

This doc is the record of the direction. It drives no work until a separate,
explicit scoping decision promotes a piece of it into the build order.
