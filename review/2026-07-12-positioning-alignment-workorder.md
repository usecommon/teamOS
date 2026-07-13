# Positioning ↔ Architecture Alignment — Work Order

- **Date:** 2026-07-12
- **Sources:** `positioning/positioning-v0.8.md` (anchor), `…-v0.8-build-reconciliation.md` (what's built), `…-v0.8-doc-alignment.md` (positioning vs docs), `docs/team-os-architecture.md` (frozen), `docs/team-os-emergence-architecture.md` (vision).
- **Purpose:** turn the alignment findings into buildable items. Everything here **refines an existing FK-built mechanism** (gate, envelope, principal_auth, connectors) — no new subsystem, nothing from the vision doc's out-of-scope surfaces (Observatory, autocatalytic trails, model router, fleet learning). Those stay vision.

---

## Part 1 — The comparison, restated

Every doc rests on the **same substrate** (files+git+lineage, gated+on-record, no LM in the gate, deny-by-default, no individuation, authenticated-consent). They diverge only in **what leads** and in **three mechanisms the positioning claims but the build doesn't yet enforce.**

| Claim in v0.8 | Frozen architecture says | Vision says | Build today | Gap → item |
|---|---|---|---|---|
| "Earned, calibrated autonomy" | §7.4 "envelope expands as a function of Ledger 8; no product ships this" | envelope widens only on authenticated ✓ (§8) | envelope computes levels **nothing reads** (display-only) | **WO-1** |
| Autonomy can't be forged | §15.2 non-repudiable principal accountability (CN-1) | §8 "only the principal's authenticated ✓ executes" a wider envelope | signature **replayable** (no nonce; edit_distance unsigned) | **WO-2** |
| "Control plane governs what can happen" | §7.3 classify every action by **severity × reversibility** | §3/§5 reversible interior runs free; irreversible boundary denies | gate classifies by action-class only, **no reversibility dimension** | **WO-3** |
| The control-plane promise | §7.3 action manifest = deny-by-default gate | §8 **the one falsifiable guarantee** + user-owned allow-policy | no allow-policy file; guarantee not a tested invariant | **WO-4** |
| Harness-agnostic via the **door** (§6–§8) | §7.5 **the door is SECONDARY (Plane B); Team OS-as-MCP-client is PRIMARY (Plane A)** | — | loops/connectors act as client (Plane A); door propose-only | **WO-5** (verify + reframe) |
| Inference "orthogonal to trust" | §14.4 **routing×disclosure seam** — endpoints carry residency labels | — | no model router in fork | **deferred** (log constraint) |

**Editorial, not build** (decide, don't code): the anchor noun (control plane vs initiative-led), and the GitHub README's team-first lead vs solo-first. Tracked as D1/D3 in the alignment doc.

---

## Part 2 — Where we align (the convergence — safe to build)

The strongest items are where **positioning + frozen architecture + vision all agree**:

- **Reversible/irreversible gating** — positioning ("control plane"), frozen §7.3 ("severity × reversibility"), vision §3/§5. Triple-grounded. → WO-3.
- **Deny-by-default at the irreversible boundary + a falsifiable guarantee** — frozen §7.3/§14 (policy-neutral gate), vision §8, positioning promise. → WO-4.
- **Authenticated-consent for autonomy** — frozen §15.2, vision §8, positioning §3, and it's the fork's one named attack chain (CN-1). → WO-2.
- **Envelope driven by Ledger 8** — frozen §7.4, positioning §3, fork FK6b. → WO-1.

**Scope fence (CLAUDE.md):** each item refines a mechanism the fork already built. Explicitly OUT: the Observatory + curiosity/concern detectors, autocatalytic trails, the model router, Tier-3 fleet learning — those are mainline/vision and need a separate scoping decision. WO-3/WO-4 build **only** the deterministic deny-by-default boundary (which the vision doc itself, §11, calls "the near-term, buildable safety primitive… what ships day one"), never the discovery half.

---

## Part 3 — The work order

**Rules of engagement:** protected paths (`hooks/`, `hooks/policy.yaml`, `config/envelope-policy.json`, new `config/allow-policy.md`, CLAUDE.md) need human approval — marked 🔒, propose the diff via PR, never auto-merge. Test alongside code; no item is done until its named test is written and `make test` is green. One item per commit; branch off `main`. Log any divergence append-only via PR.

### WO-1 — Wire the envelope into the gate (make "earned autonomy" real) 🔒
- **Closes:** reconciliation fix #1; positioning §3 differentiator; frozen §7.4.
- **Why:** `envelope.py` computes principal-attributed per-category levels, persists + ledgers them — but `gate.py:inspect()` never reads them; only `render_dashboard.py` does. The dial turns, connected to nothing. This is the single feature separating the anchor from "hooks + a policy file."
- **Files:** `hooks/gate.py` 🔒, `hooks/policy.yaml` 🔒 (map action-class → envelope category), `scripts/envelope.py` (read-only accessor for current level), `config/envelope-policy.json` 🔒 (levels already declared).
- **Do:** in `inspect()`, load the current envelope level for the action's category (from `envelope-state.json`, already a protected path the agent can't write). Level modulates the verdict *within* what policy already allows: level 0 = ask always for that category; higher levels permit progressively (never above the category ceiling, never overriding a taint/secret/protected-path/breaker deny). The gate **reads** the level; it never writes it.
- **Proof:** `tests/test_gate.py` — after N principal-attributed light-edit acceptances raise the `send` level (drive via `envelope.process_signal`), a previously-`ask` clean send returns `permit`; a subsequent principal-attributed rejection narrows it back to `ask`. Assert an unattributed signal moves nothing.
- **Invariant:** the envelope script can never touch its own ceiling; the gate reads the level, never widens it; a hard finding (secret/taint/protected/breaker) always outranks the level.

### WO-2 — Sign the full L8 payload; reject replay (close the forgeable-autonomy chain)
- **Closes:** reconciliation fix #2; CN-1 / frozen §15.2 / vision §8 second boundary.
- **Why:** `principal_auth.signing_payload` binds only `signal_type|path|principal_id|outcome` — **no nonce, no timestamp, and `edit_distance_normalized` is unsigned.** A captured valid endorsement signature is replayable, and its edit-distance (which decides `is_acceptance`) is malleable → a forged/replayed reaction can widen the envelope. This is the one third-party attack chain the fork exists to close.
- **Files:** `scripts/principal_auth.py` (`signing_payload`, `verified`), `scripts/l8_capture.py` (add nonce+timestamp at capture), a small seen-nonce store under the ledger dir.
- **Do:** extend `signing_payload` to bind `edit_distance_normalized`, a per-record `nonce`, and `harvested_at`. `verified()` rejects (a) a nonce already seen, (b) a timestamp outside a configurable freshness window. Keep the formative-posture fallback (no keydir → field trusted) intact.
- **Proof:** `tests/test_principal_auth.py` — a valid endorsement sig replayed with a tampered `edit_distance` fails; a replayed nonce fails; a stale timestamp fails; a fresh correctly-signed record verifies.
- **Invariant:** the envelope/floor consume only principal-authenticated, non-replayed signals; no autonomy widening on a forged, replayed, or unattributed signal.

### WO-3 — Add a reversibility dimension to the action manifest 🔒
- **Closes:** doc-alignment asset A; frozen §7.3; reconciles the anti-cage tension.
- **Why:** the gate classifies by action-class only. Frozen §7.3 mandates classification by **severity × reversibility**; the positioning's differentiated story is "control the irreversible boundary hard, run the reversible interior free." Reversibility is the missing axis.
- **Files:** `hooks/policy.yaml` 🔒 (tag each action-class + tool with a reversibility label), `hooks/gate.py` 🔒 (`classify`/`inspect` carry the label into the verdict + L2 record), `hooks/BEHAVIOR.md` (document the two zones).
- **Do:** label the surface: **irreversible** = external send, external-mutating exec, delete/overwrite-without-history, disclosure, spend; **reversible** = interior write/edit/corpus-draft/skill-fork. The gate treats irreversible as boundary (feeds WO-4); reversible interior actions are permitted-and-recorded subject to existing taint/protected-path/secret checks. Record the reversibility label in the L2 body. **Scope fence:** this item builds the *classification + boundary handling only* — not the Observatory, not autocatalytic trails, not "observe the interior" tooling.
- **Proof:** `tests/test_gate.py` — an external send is classed irreversible → routed to the WO-4 boundary; an interior corpus draft is classed reversible → permits (absent taint/secret/protected hit). Reversibility appears in the L2 record.
- **Invariant:** brake irreversible cost, never reversible outcome; classification is deterministic, model-free.

### WO-4 — The allow-policy + the one falsifiable guarantee 🔒
- **Closes:** doc-alignment asset B; vision §8; positioning promise line.
- **Why:** the sharpest ownable claim in any doc, currently unbuilt: *no irreversible action without an allow-match or human confirmation, each with a pre-act record.* Needs a user-owned allow-policy and a tested gate invariant. Depends on WO-3's reversibility label.
- **Files:** `config/allow-policy.md` 🔒 (new; user-owned; **default empty**), `hooks/gate.py` 🔒, `hooks/policy.yaml` 🔒, `hooks/BEHAVIOR.md`.
- **Do:** an action classed **irreversible** (WO-3) passes only on (i) a match in `allow-policy.md` **or** (ii) a human confirmation (verdict `ask`), and in every case a **pre-act L2 record** is written before the decision returns. Allowlist is deterministic string/rule match — no model. Default empty = every irreversible act asks. The allow-policy is a protected path (agent can't widen it).
- **Proof:** `tests/test_gate.py` — a property/fuzz test over irreversible actions: **no input yields `permit` without an allow-policy match**, and **every irreversible decision emits a pre-act L2 record**. A matching allow entry → `permit`; empty policy → `ask`. This test *is* the falsifiable guarantee; a failing case is a falsifying bug.
- **Invariant:** the one falsifiable guarantee. Everything else is best-effort; this is not.

### WO-5 — Verify Plane A primacy; reframe positioning §6–§8 off the door
- **Closes:** doc-alignment Addendum 1.
- **Why:** the architecture makes **Plane A (Team OS as its own MCP client, acting ambiently) primary** and the door (Plane B) secondary; positioning §6–§8 over-center the door. Confirm the build already matches the architecture, then fix the *positioning*, not the code.
- **Files:** verify `scripts/loop.py`, `scripts/connectors.py` (Plane-A outbound actions hit the gate), `scripts/door.py` (stays propose-only); **positioning edit** in `positioning/` (re-lead §6–§8 on Plane A).
- **Do:** add/confirm a test that a Class-A loop's outbound action is gated by the local hook (Plane A = full-trust), and that the door only writes proposals (Plane B = secondary). This is **verify + a divergence-log note + a positioning edit** — no new mechanism.
- **Proof:** `tests/` — loop outbound action produces an L2 gate record; door call produces only an inbox proposal, never a corpus/gate commit.
- **Invariant:** the door writes to the proposals inbox, never the corpus; the gate processor at the runtime of record is the sole writer.

### Deferred — routing×disclosure seam
No model router exists in the fork (Plane-A owned inference is noted; the LiteLLM-class router is mainline §14.4). **Do not build now.** Log the constraint so that *when* routing is built, every endpoint carries a residency/attestation label and a task may route only to an endpoint whose label satisfies its data's disclosure tier. Add one line to the divergence log; update positioning §4 to caveat "inference orthogonal to trust" with this seam.

---

## Suggested order & why
1. **WO-2** (signing) — small, security-critical, independent; closes the live attack chain.
2. **WO-1** (envelope→gate) — the solo differentiator; makes the anchor true.
3. **WO-3 → WO-4** (reversibility label → allow-policy + guarantee) — coupled; the control-plane differentiation and the falsifiable promise; the triple-grounded convergence.
4. **WO-5** (Plane A verify + positioning reframe) — alignment hygiene; mostly verify + edit.

WO-1/WO-2 make the **solo** anchor real and safe. WO-3/WO-4 make the **control-plane** claim differentiated and provable. WO-5 aligns the harness-agnostic story with the architecture's actual priority. After all five, v0.8's load-bearing claims are either built-and-tested or consciously deferred with a logged constraint.
