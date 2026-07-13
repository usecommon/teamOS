# Team OS — Positioning (working documents)

Versioned positioning statements for Team OS. Each version is a full, standalone snapshot so the thinking can be revised over time without losing the trail.

## Convention

- `positioning-vX.Y.md` — a complete positioning statement at a point in time.
- **Latest is the highest version number.** Older versions are kept, not overwritten.
- Bump **minor** (v0.1 → v0.2) for revisions from new evidence/feedback; bump **major** (v0.x → v1.0) when a positioning is adopted as the working default.
- Every version carries a header: version, date, status, what changed, and the open questions still gating it.

## Version log

| Version | Date | Status | One-line |
|---|---|---|---|
| [v0.9](positioning-v0.9.md) | 2026-07-12 | **Current — ANCHOR** | **Human-centric reland.** Same wedge (agent control plane), re-centered on the person (agents = fabric, not the point). Both/and: control-plane AND initiative; govern AND free. "Command-and-control you can loosen to a lab" — user owns interior + exterior dials. Leads Plane A; adopts the falsifiable guarantee. WO-1/WO-2 shipped → solo differentiators now tested. |
| [v0.8](positioning-v0.8.md) | 2026-07-12 | Superseded | **The solo agent control plane you own.** Analyst-named category (Gartner AMP / Forrester agent control plane), solo lane unclaimed. Pain = orchestrating a multi-model fleet, not coding. Two-axis posture model; govern-the-seam-not-the-server; door as nesting-parent + fan-in MCP chokepoint. Team demoted to secondary growth hook. |
| [v0.7](positioning-v0.7.md) | 2026-07-12 | Superseded | Layer, not harness: Team OS sits on top of both Claude Code and Hermes. Weld to Claude for distribution; harness-agnostic (MCP + FR5 adapter) for durability/subsumption-hedge. Hermes = substrate we ride, not just competitor. |
| [v0.6](positioning-v0.6.md) | 2026-07-12 | Superseded | Adds Hermes Agent reckoning: cede capability, compete on provable governance + team operation. Single-user wedge narrowed to the governance-conscious user ("autonomy you can answer for"). |
| [v0.5](positioning-v0.5.md) | 2026-07-12 | Superseded | Leads with the single-user wedge ("the agent you can let off the leash"); adoption path single-user→team→org; team category is the destination. The cold-start reason = the mechanism the review found broken (envelope). |
| [v0.4](positioning-v0.4.md) | 2026-07-12 | Superseded | Category reframe: "where your team runs its agents — together." Verified gap (agent-manager + agent-admin exist; team-operation doesn't); five concrete primitives Team OS already has. |
| [v0.3](positioning-v0.3.md) | 2026-07-12 | Superseded | Two-role buyer (worker champion → risk-owner approver); initiative=engine / trust-stack=brakes; transfer = share the skill, keep personalization local. |
| [v0.2](positioning-v0.2.md) | 2026-07-12 | Superseded | Staged (A wedge / B upsell / C bet); sell initiative, moat the transfer layer + ownership, upsell governance; buyer = org-side risk owner. |
| [v0.1](positioning-v0.1.md) | 2026-07-12 | Superseded | Shape-3 "sovereign cooperative"; race the substrate, moat the sovereignty. Four open questions out to research. |

## Open questions — resolved in v0.2

The four threads that gated v0.1 are answered (full sources in v0.2 §9):

1. **Demand / WTP** → Trust stack is a **painkiller at the regulated/enterprise boundary, a vitamin at small scale.** Lead with initiative; upsell governance.
2. **Substrate race** → Cross-human *learned* transfer shipped by no one; labs commoditize the *substrate* in 6–18mo. Durable edge = the **transfer/federation + measurement layer**, not a store.
3. **Does transfer work** → **Emerging, narrow.** Works for executable, task-general skill *artifacts*; flat-to-negative for personalized/"my-voice" work. Gate on artifact-skills; the two-different-users experiment is the cheapest differentiated evidence (= A-P3).
4. **Buyer / ICP** → **Yes, but it's the org-side risk owner** (security/platform/CISO at regulated/IP-sensitive orgs), plus EU works councils. Worker-sovereignty is a trust/retention asset, not a lead buy reason.

## Next open questions (gating v0.8 → v1.0)

The anchor is set (v0.8). Adopting it as the working default (→ v1.0) is gated on:

- ~~Product reconciliation~~ **DONE** (2026-07-12) → `positioning-v0.8-build-reconciliation.md`. Core anchor (gate+record+policy+deletion+ownership) is built & tested. Confirmed gaps: **envelope inert at the gate** (P0, the solo differentiator), **replayable L8 signature**, **door §7 topology unbuilt**. Fix order: envelope→gate, sign full L8 payload, then door topology.
- **Pricing / packaging** for a solo-self-serve control plane (owned, BYO-subscription/API), and the always-on-loop **unit cost**.
- **A-P3 experiment design** — the two-user, non-shared-task, artifact-skill transfer test with real collaborators (the §10 growth hook's proof).

## Prior open questions — resolved

- v0.1's four threads (demand/WTP, substrate race, does-transfer-work, buyer/ICP) → resolved in v0.2 §9.
- v0.3's category/landscape/sizing questions → resolved by research threads 7–14 (see `research/README.md`); the four-corner whitespace holds (v0.8 §9).
