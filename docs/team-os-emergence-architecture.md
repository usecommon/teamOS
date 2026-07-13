**`v0.5 — 2026-07-12`** *(VISION — thesis-level; NOT governing, NOT driving FK work. Beyond the validated fork. Written to be on the record before it drifts. Precedence: below every doc in the fork spec's precedence order. Do not build from this without an explicit, separate scoping decision.)*

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

## 2. The core principle — safety is unwind (limited); observability makes it possible

A brake that halts a compounding trend **destroys the thing you wanted to
study**. "Off the rails" is not a failure state to prevent; it is a *result to
observe and then judge from outcomes*. Pre-defining "off the rails" with
thresholds presumes you already know what is bad — the exact assumption that
kills discovery. So the safety mechanism is not a governor that stops.

**Safety is the ability to unwind — honestly limited.** Unwind is total for
private, uncoupled, fresh state. It **degrades** the instant another agent reads
a trail and acts on it (coupling), and further with time (the reversibility
half-life). It is **void** for the things §4 catalogs. So safety is not one
mechanism but two zones:

- **Where unwind reaches → that is the safety.** Let it run, study the trend,
  revert what proves wrong. Judgment comes *after*, from outcomes — never
  *before*, from rules.
- **Where unwind does not reach (§4; coupled; aged) → safety is prevention.** The
  boundary gate and the user's harm policy (§7, §12) stand *ahead* of the act.
  Nothing else can protect an act you cannot take back.

**Observability is not the safety — it is what makes safety possible, and it is
the promise.** You can only unwind what you can see, and candidates (§7) are how
unwind is aimed; so observability is the *enabler*. And "nothing happens
invisibly" is the *honesty promise* the system can always keep: *not "the agent
never errs," but "no error is silent — you will see every one, with the receipts,
and hold the switch."* But a complete record of an act you cannot undo is
**forensics, not safety** — which is precisely why observability *enables and
promises*, while unwind (limited) + prevention do the *protecting*.

**Unwind is a decision on candidates.** The Observatory surfaces; a human — or the
user's standing policy (§12) — chooses promote / keep watching / unwind. It is a
move you make on a flagged candidate, not a net always under you.

### The three standing requirements

For this to hold rather than degrade into excellent post-mortems, three things are
load-bearing — requirements, not nice-to-haves:

- **(a) Keep the boundary gate.** Irreversible acts (§4) are prevented, not merely
  observed. The gate does not go away; it is confined to the door, and it enforces
  the user's harm policy (§7).
- **(b) Two detectors, not one.** The Observatory needs a *curiosity* detector
  (surface the novel) **and** a distinct *harm* detector (surface the dangerous —
  especially the boring, slow, irreversible trail a curiosity detector ignores by
  design). Novel ≠ harmful; harmful ≠ novel. See §7.
- **(c) Detection latency under the reversibility half-life.** Unwind-on-candidate
  only works if candidacy is caught while the rewind is still clean. For
  irreversible acts this collapses to (a): the harm detector must fire *ahead* of
  the trigger, which makes it a gate, not an observer.

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

The Observatory studies emergence; it also carries the safety-critical half of
the system — it makes unwind targetable (candidates), it hosts the harm detector
that enforces the user's policy at the boundary, and it is where the "nothing
silent" promise lives (§2). That makes it load-bearing — not a deferrable v2
nicety (see §11).

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

  **"Harmful" is the user's policy, not the tool's opinion.** Harm is defined in
  an **editable markdown file the user owns** and can change anytime — the tool
  holds the *mechanism*, the user holds the *definition*. This is what keeps the
  harm detector policy-neutral (§3a of the fork) instead of the tool imposing a
  view of "bad": the detector enforces whatever the policy says, no more, no less.
  Default: the harm detector is **ON**. Honest limit: recall is bounded by how
  completely the policy names real harms — a file will not enumerate everything,
  so this detector is **best-effort**, and the user owns its completeness. Safety
  here is "unwind (limited) + a best-effort, user-defined boundary policy," never
  a claim of total prevention.

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
  re-introduce a suppression bias the whole design rejects? *(Addressed in §12:
  expire-to-inert default + user-set auto-approve; triage ranks, never kills.)*
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
  nicety: because its harm detector enforces the user's boundary policy and its
  candidates are how unwind is aimed (§2), its **harm-detector half must ship with
  the boundary gate, day one**. Its **curiosity half** — the discovery payoff — is
  what earns its keep only at density (FK7+ / v2). Split the two: the safety
  detector is near-term; the discovery detector is later.
- The **hard gates** (§8) already exist — this doc changes nothing about them; it
  only clarifies that they are the *boundary*, and the interior is free.

## 12. Auto-approve — the gate is a user setting, not a system opinion

The judgment bottleneck (a human must decide every graduation) is real only in
one mode. It is a *setting*, not a law — policy-neutral, like every other source
and rule in the system. The two regimes of §2 are the **default**; the user may
move the line.

Three modes:

- **Review (default).** Free reversible micro-compounding in the window; the
  human promotes each graduation to durable influence. Safety-by-judgment,
  throughput-limited.
- **Auto-approve interior.** Reversible graduation happens automatically per the
  user's policy; the irreversible boundary (§4) still gates. Removes the
  bottleneck for the cheap, recoverable work; keeps a hand on the door.
- **Auto-approve all.** Full autonomy within the user's cost ceilings. Maximum
  throughput; the user owns the risk.

Across every mode, what counts as harm is the **user's harm policy — the editable
markdown file** of §7, owned by the user; the tool enforces it, never its own
opinion. **Defaults: harm detector ON, no auto-approve.** The user always chooses
— edit the policy, turn auto on or off, per category. The default protects; the
hatch is the user's owned, attributed choice (see the honest note below).

Three invariants hold across **all three modes** — this is what keeps auto-approve
honest rather than reckless:

1. **Observability never turns off.** Auto-approve removes the *decision*, never
   the *record*. The harm detector (§7) still runs; under auto-approve it
   *notifies without blocking* instead of blocking. "Nothing happens invisibly"
   holds in every mode — observability is the one thing auto-approve cannot
   disable (§2), so unwind stays targetable and the promise stays kept even with
   the gate off.
2. **Cost governors bind the irreversible boundary.** Even under auto-approve-all,
   the §5 caps (spend / token / spawn) stand — they protect against *unrecoverable
   loss*, not *reversible outcomes*. The user can raise a ceiling; they cannot make
   it not exist.
3. **A harm-rate limit stands beside the cost cap — because harm ⊥ cost.** Spend
   caps stop a $10k burn; they do nothing about 500 individually-cheap irreversible
   sends, or a single $0.02 disclosure. So an **irreversible-action-rate limit**
   (sends / deletes / disclosures per window), governed by the harm policy, runs
   alongside the spend caps; a spike trips the circuit breaker. Cheap harm is still
   harm.

**Honest note (not a resolved point).** Auto-approve-all is the hatch that lets a
throughput-seeking user revert to an unsupervised autonomous agent — the category
the market is fleeing. The default (review + detector on) protects; the incentive
gradient still pulls toward the hatch. This is a *product-strategy* risk the design
cannot eliminate, only surface: it is the user's owned, attributed choice, made
visible, never the tool's default.

Auto-approve is the principal **pre-widening their own envelope**, authenticated
(CN-1, §8). It is the user's own attributed standing policy — not an emergent
trend widening itself — so it does not reopen the forged-signal attack chain. The
system still never widens on an *unattributed* signal; it honors an *attributed*
one set in advance.

Net: **the gate is a dial the user holds. Observability and the cost floor are
the system's only non-negotiables.**

## 13. Deletion on an append-only record — key-destruction erasure

The record is append-only and hash-chained: rewriting it breaks the chain, and
the chain's integrity is the tamper-evidence the whole system rests on. But
erasure must work (Ledger 9; the deletion invariant; the right to be forgotten).
Append-only durability vs. mandatory erasure — head-on.

**Resolution — key-destruction erasure (a.k.a. crypto-shredding; "crypto" =
cryptography, nothing to do with coins).** Each principal's content is already
encrypted with a per-principal key held outside the repo. To delete, **destroy
the key.** The encrypted bytes stay in the ledger — so the chain is *never
rewritten*, and the structure survives (that an entry existed, which agent
authored it, when, which cluster it joined, that it was deleted at T by principal
X). The *content* becomes permanently unreadable.

- Shred the only key to the drawer, not the filing cabinet. Cabinet stays (proof
  and structure); contents gone.
- **Deletion propagates** over the lineage DAG (Ledger 9 machinery, inherited not
  reinvented): the walk destroys the right keys; independent downstream artifacts
  survive but their citations are redacted to the tombstone.
- **The deletion is itself ledgered** — "nothing happens invisibly" (§2) includes
  erasures. You keep proof-you-erased; you do not keep the erased content.
- **Erasure reaches derivatives — including distilled conclusions.** A promoted
  skill/insight outlives its raw source **only if it is genuinely de-identified**;
  if it still carries the subject's personal data, erasure propagates to it too
  (destroy its key / redact it). "Distilled conclusions outlive their evidence"
  holds for *de-identified* discovery, **never** for personal data — otherwise
  erasure is defeated by laundering the data into a durable artifact under a key
  you did not destroy.

**Why this and not history-rewrite.** How others do it:
- *git / GitHub* — rewrite history + garbage-collect unreachable objects.
  Expensive, breaks the chain, best-effort (copies linger in forks / caches);
  their own guidance for a leaked secret is "assume compromised, rotate" — §4's
  one-way door, confirmed by the largest immutable-history system in the world.
- *event-sourcing / append-only logs* — crypto-shredding, exactly this pattern.
- *blockchain / GDPR* — keep content off the immutable store, hold only a hash
  inside; delete the off-store content and the hash becomes a dangling commitment.

Key-destruction wins here because we already hold the keys, it never touches the
chain, and it is instant and total.

**Granularity, hashes, and control.** Three corrections make the mechanism
actually satisfy erasure:

- **Per-subject, not per-principal, keys.** Erasure is per *data subject*, per
  request — "delete Alice's data," one person out of many. A per-principal key
  erases the whole store (the wrong unit); ingested others' data must be keyed
  **per subject** so one subject can be erased without nuking the rest.
- **Salt-and-shred the content hash.** A retained hash of low-entropy erased
  content (a short message, a name from a known set) is a brute-forceable
  commitment to it. Tombstone hashes of personal content are salted and the salt
  is destroyed with the key — the structure that stays must not leak the content
  that went.
- **User control, within legal floors.** The user sets the erasure and retention
  policy — scope, propagation depth, keep-vs-shred for *de-identified*
  derivatives. But a data subject's erasure right is a **floor the principal
  cannot opt out of**, and the safe **default is full propagation**. The tool
  gives the dials; the user owns compliance.

**Caveat — erasure by inaccessibility, not physical destruction.** Acceptable
under most readings of the right to erasure (data rendered permanently
unrecoverable). For the strictest cases, or against a future key compromise,
combine it with the blockchain pattern: store the raw content in an off-ledger
store you can *physically* wipe, keep only a hash in the chain. Belt and
suspenders.

**Line: structure durable, content erasable — and personal structure follows the
content.** The chain and the *de-identified* shape are studiable as long as the
system lives; content, and any structure that is *itself* personal data (a
person's authorship trace, a timing profile), only until erased. The person's
erasure right beats the system's memory — as it must.

## 14. Threat model — internal erosion of observability

Every safety property here assumes the recorder and the detector are trustworthy
and complete. But the emergent agents *generate* the records. In a system built to
let agents develop unplanned behavior, an agent that emergently learns to
under-report, or learns what the harm policy flags and routes around it, attacks
safety **from the inside**. The fork's threat model covers the *external* forged
signal (CN-1); this is the *internal* one, and the emergence thesis cannot
pre-forbid it without contradicting itself.

Two guards, mostly inherited:

- **The record path is deterministic and not agent-writable (SE-1 / CN-2).** The
  fork already forbids a language model in the evidence and commit paths — reaction
  harvest and inbox-commit are deterministic, hook-gated code, and the gate runs no
  model. The emergence layer inherits this: **an agent can act, but it cannot write
  its own ledger.** Observability is recorded *about* the agents by code they do
  not control, so an agent cannot quietly stop being observed.
- **Evasion is itself a flagged pattern.** "An agent's observability is dropping,"
  "actions increasingly cluster just under a harm-policy threshold," "trails
  reshaped to skirt the detector" — these are exactly the boring, compounding
  patterns the harm detector (§7) exists to surface. Evasion of the detector falls
  inside the detector's own remit; a falling observability metric is a first-class
  candidate.

Residual, honest: a guard detector can be evaded the way any detector can (recall
< 1). The deterministic, non-agent record path is the **hard floor**; the evasion
detector is best-effort on top. This threat is **bounded and watched, not
eliminated** — stated so it is on the record rather than assumed away.

---

This doc is the record of the direction. It drives no work until a separate,
explicit scoping decision promotes a piece of it into the build order.
