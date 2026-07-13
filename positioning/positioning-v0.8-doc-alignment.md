# v0.8 Positioning ↔ Architecture Docs — Alignment Review

- **Date:** 2026-07-12
- **Reviewed:** `docs/team-os-architecture.md` (§1, frozen mainline), `docs/team-os-emergence-architecture.md` (v0.6 vision) + `…-emergence-summary.md`, and `README.md` (the GitHub landing). Against `positioning-v0.8.md`.
- **TL;DR:** The **machinery is fully consistent** across all docs — same substrate, same gate, same guarantees. The **lead framing is not.** Four docs lead with four different nouns and two different entry-scales. v0.8 leads with **control + solo**; the committed/GitHub docs lead with **initiative, emergence, and team**. This is a strategic choice to make explicit, not a bug to fix — plus two concrete assets in the vision docs that v0.8 should absorb.

---

## The four framings (what each doc leads with)

| Source | Lead noun | Primary value | Entry scale | Stance on "control" |
|---|---|---|---|---|
| **`README.md`** (GitHub landing) | "**agent fabric**" | team's connective knowledge tissue | **team** | neutral |
| **`architecture.md` §1** (frozen) | "**proactive, action-driven system**" | initiative — *it originates, unasked* | org / fleet | gates *enable* initiative |
| **`emergence-architecture.md`** (vision) | "**a lab, not a cage**" | emergence you can see, bound, unwind | **density** (many agents × people) | **anti-control-as-headline** |
| **`positioning-v0.8.md`** | "**control plane**" | govern what *can* happen | **solo** | **pro-control** |

Same product underneath; four different front doors.

---

## Where they deeply agree (the shared bedrock — this is the control plane's substrate)

Every doc, including v0.8, rests on the identical machinery. **No divergence here:**
- Files + git + lineage = system of record; owned; **exit = clone**.
- Every action **gated + on a tamper-evident record**.
- **No language model in the gate / evidence path** (SE-1/CN-2) — deterministic.
- **Deny-by-default** (default-deny sharing / empty allowlist).
- **Proactive agents** (initiative) + measured **skill sharing across the fleet**.
- **No individuation** — measure agents/skills, never people.
- **Authenticated-consent** for autonomy widening (CN-1).

→ v0.8's control plane is **architecturally faithful** to the frozen spec. The disagreement is purely about *what to put first*, not *what it does*.

---

## The three real divergences

### 1. Lead value: control (v0.8) vs initiative (mainline identity)
`architecture.md:11` opens with an explicit warning: *"read this before filing the product in a category… Team OS is a proactive, action-driven system — it works on its principal's behalf without being asked… request-response systems can only answer; Team OS **originates**."* The identity is the **engine**, and CLAUDE.md makes it an invariant: **"Initiative before interface."**

v0.8 leads with the **brakes** ("the control plane… governs what can happen"). That is the market-recognized, analyst-named category — but it is the exact framing the identity claim tells you *not* to file the product under. **Tension is real:** v0.8 sells the governance layer; the constitution says the governance layer exists to make the *initiative* safe, and the initiative is the identity.

### 2. Control rhetoric: v0.8 pro-control vs emergence anti-cage
`emergence-architecture.md:32` : *"Most agent systems try to prevent emergence… that kills the upside with the downside. A system that can't surprise you can't discover anything."* Its category is *"a lab, not a cage."* v0.8's "**govern what can happen**" is rhetorically the cage. The *mechanisms* reconcile (see assets below); the *sell* is opposed.

### 3. Entry scale: v0.8 solo vs README team vs emergence density
v0.8 is deliberately **solo-first** (the adoption law — [[adoption-single-user-first]], resolved). But the **GitHub landing README leads team-first** ("Human teams. Agent fabric… the unit is a person, and the payoff is the team getting better together"), and the emergence payoff is **density-gated** (`emergence-summary.md:75` — "needs many agents × many people × a dense corpus"). So the public front door (README) and the vision both lead at a scale v0.8 says *not* to lead with.

---

## Two assets in the vision docs v0.8 should absorb (these make the control plane *better*)

### A. The reversible / irreversible split (`emergence §3, §5`)
v0.8's gate governs **every action by class, uniformly**. The emergence doc sharpens this: **gate hard only at the irreversible boundary (deny-by-default); let the reversible interior run free and observe** ("brake irreversible cost, never reversible outcome," `§5:193`). This is a *stronger, more differentiated* control-plane story — and it dissolves divergence #2: **"control where it's irreversible, freedom where it's recoverable"** is both a control plane *and* "not a cage."

### B. The one falsifiable guarantee (`emergence §8`)
> *"No irreversible action ever occurs without either an allow-policy match or a human confirmation — and every one has a pre-act record. A deployment where one did is a falsifying bug, not a tolerable residual."*

v0.8 has **no line this sharp.** It is deterministic, model-free, ownable, and *falsifiable* — the strongest single claim in any doc. The solo control plane should carry it as its promise. Pairs with "no LM in the gate" (already shared bedrock) into a crisp differentiator vs the market's semantic-classifier gates (Cursor, Gemini semantic governance).

---

## Recommendation — reconcile, don't pick

The control-plane anchor is the right **market wedge** (analyst-named, solo lane open). Keep it — but bridge it to the identity instead of replacing it:

1. **Reframe the value the noun delivers.** Control plane is *how you enter and what the market recognizes*; the value it delivers is **unleashing initiative safely** — "the control plane that lets you let a proactive agent off the leash." This satisfies the market (control) *and* the identity claim (initiative). v0.8 §9 already holds "initiative = engine, trust-stack = brakes" — pull that into the anchor, don't bury it in §9.
2. **Adopt the reversible/irreversible split** (asset A) into §5–§6. Turns "govern everything" into "control the irreversible boundary hard, run the reversible interior free" — kills the anti-cage tension.
3. **Adopt the falsifiable guarantee** (asset B) as the anchor's promise line (§3/§13).
4. **Keep emergence as the v2 / density chapter**, explicitly. It is *status: vision, drives no build*, and its payoff is density-gated — it **must not** become the solo hook. Its two buildable primitives (deny-by-default boundary + guarantee; autocatalytic trails) feed the control plane *now*; the Observatory earns its keep later.
5. **Decide the README (GitHub front door).** It currently leads "Human teams. Agent fabric" — inconsistent with solo-first. Either (a) reland it solo-first with fabric as the destination, or (b) consciously keep it as the "what it becomes" story. **This is a live inconsistency on the public repo landing — pick one.**

**Net:** v0.8 is not *wrong* against the architecture — it's *narrow*. It leads with one true face (control, solo) of a product the frozen docs describe as initiative-first and team-bound. The fix is additive: bridge control→initiative, scope gating to irreversible, adopt the guarantee, and reconcile the README's scale. Do that and all four framings become one story with different emphasis by audience, instead of four different nouns.

---

## Full-read addenda — what the section review missed (both docs read end-to-end)

Reading `architecture.md` (760 lines) and `emergence-architecture.md` (545) in full surfaced four items. Two are framing; **two are substantive corrections to v0.8.**

### ADDENDUM 1 (correction) — the door is *secondary*; v0.8 over-centers it
`architecture.md:271–274` defines two **connection planes**, and the priority is the opposite of v0.8's emphasis:
- **Plane A — Team OS → services (PRIMARY).** Team OS is itself an **MCP client** holding its *own* OAuth connections to Slack/Gmail/Jira/Drive/GitHub, acting *as* the user, ambiently, with **no Claude/ChatGPT client in the loop**. *"The proactive identity claim requires this plane — a digest that only runs during an open chat session is a chatbot, not a background agent."*
- **Plane B — Claude (and ChatGPT) → Team OS (SECONDARY).** Team OS exposes an MCP **server**; a client toggles it on to query. *"'Claude as the door' (B) is an addition to direct connection (A), never the mechanism for it."*

v0.8 §6–§7 build the whole harness-agnostic story on **the door (Plane B) as the central chokepoint.** The architecture says the door is the *secondary* path; the *primary* is Team OS holding its own credentials and originating action. **Implication:** v0.8's "govern the seam" is right, but it privileges the wrong seam. The load-bearing seam is Team OS-as-MCP-client acting ambiently (Plane A, where the gate fires locally on Team OS's own actions), not Team OS-as-gateway-for-other-harnesses (Plane B). The multi-model/portfolio story (§8) still holds — but it should be framed as *Team OS orchestrating the portfolio as the client*, not *other harnesses reaching through Team OS's door*. Fix v0.8 §6–§8 to lead Plane A.

### ADDENDUM 2 (correction) — inference is *not* cleanly orthogonal to trust
v0.8 §4 says the inference-source axis is "orthogonal to trust." `architecture.md:607–609` (§14.4) agrees it's a separate axis **but names "one non-orthogonal seam":** the **Routing×disclosure invariant** — *"every endpoint carries a residency/attestation label; a task may only route to an endpoint whose label satisfies the active tier's disclosure sentence… the router enforces the tier, not just the capability match."* I.e., you **cannot** route a task touching the vendor-blind personal layer to a non-attested endpoint just because it's cheaper. **Implication:** v0.8's clean "hooks fire locally, not who bills the tokens" is *mostly* true but needs the caveat — **inference routing is trust-relevant when the data's residency/disclosure tier constrains which endpoints are eligible.** Add the routing×disclosure seam to §4.

### ADDENDUM 3 (reinforcement) — reversible/irreversible is already in the *frozen* architecture
The reversible/irreversible split isn't only an emergence-vision idea. `architecture.md:245` (§7.3 action manifest): *"Classify every possible action by **severity × reversibility**; assign approval requirements before orchestration."* So **asset A is doubly grounded** — mainline *and* vision. Adopting "control the irreversible boundary hard, run the reversible interior free" into v0.8 is consistent with the frozen spec, not just the vision. Strengthens the recommendation.

### ADDENDUM 4 (framing) — v0.8's trust tiers ≠ the architecture's deployment tiers
v0.8's tiers (**B full-trust hooked / A door-scoped / C hookless**) are an *execution-locus × hook-availability* taxonomy. The architecture's **T0–T3** (`§14.7`: on-demand / serverless-self-custody / managed / daemon-local) are a *custody × residence* taxonomy. They're compatible but **different axes** — v0.8 is inventing a new tier vocabulary. Not wrong, but note it, and don't let readers conflate v0.8's "Tier A/B" with the architecture's "T0–T3." Consider renaming v0.8's tiers to avoid the collision.

### Net change to the verdict
The core finding stands (machinery consistent; framing divergent). The full read **hardens** the recommendation and adds two concrete corrections: **lead Plane A over the door (Addendum 1)** and **caveat inference-orthogonality with the routing×disclosure seam (Addendum 2)**. Both are v0.8 edits, not doc conflicts.

---

## Decisions — RESOLVED by user (2026-07-12)

- **D1 → BOTH.** Control-plane AND initiative, not either/or. The control plane is what lets you *unleash* the proactive agent; brakes exist to press the gas. Anchor holds both.
- **Human-centric, NOT agent-focused (new, overrides v0.8's framing).** The unit is the *person*; the payoff is the *team getting better together*. Agents are the fabric, not the point. v0.8's "control plane for your *agent* fleet" over-centered agents — rewrite to center humans. It is a team product for humans throughout; solo is the *entry*, not the identity.
- **Govern AND free — both, and adjustable.** "Control the irreversible boundary hard, run the reversible interior free" delivers both at once. BOTH zones are user-adjustable: interior dial = the autonomy envelope (WO-1); exterior dial = the user-owned allow-policy + auto-approve modes (WO-4). **Ships cage-shaped (tight/safe default) but every bar is a dial the human owns → becomes a lab at the user's discretion.** Tagline shape: *"command-and-control you can loosen to a lab."* The work order (WO-1/WO-3/WO-4) already builds exactly this adjustability.
- **Adoption:** ships to **solo** as command-and-control of their agents (wedge) → grows to **team** → but is a human-centric team product the whole way.

## Still open
- **D2.** Fold reversible/irreversible + the falsifiable guarantee into the next positioning version (→ v0.9)?
- **D3.** README (GitHub landing) currently leads "Human teams. Agent fabric" — which is *already* human-centric and team-framed. Given the human-centric resolution, the README lead may be *more* right than v0.8's agent-centric anchor. Decide: reland v0.9 to match the README's human-centric lead (solo as entry), rather than relanding the README to match v0.8.
- **D4.** Re-lead §6–§8 on **Plane A** (Team OS as ambient MCP client), door secondary?
- **D5.** Add the **routing×disclosure seam** caveat to §4?
