# v0.8 Positioning ↔ Build Reconciliation

- **Date:** 2026-07-12
- **Method:** direct code inspection + `make test` (214 tests pass, 16 schemas clean, `verify_chains` green). Evidence cited as `file:line`.
- **Question:** does the anchored positioning (`positioning-v0.8.md`) stand on what's actually built?
- **Verdict in one line:** **The core anchor — "the solo control plane you own" (gate + record + policy + deletion + ownership) — is real and tested for a Claude Code user. Two positioning elements are ahead of the build (earned autonomy; harness-agnostic §7 door). One is stronger than v0.8 credited (multi-model via a hooked conductor).**

---

## The two load-bearing claims (the ones §12 flagged)

### 1. Envelope enforced at the gate → ❌ **INERT — confirmed in code (P0)**

The envelope computes, persists, and ledgers per-category autonomy *levels* on principal-attributed L8 signals (`scripts/envelope.py:76` `process_signal`, asymmetric widen/narrow, CN-1 gated). That machinery is real and correct.

**But nothing reads those levels to change a gate decision.** The gate's verdict (`hooks/gate.py:115` `inspect`) is computed entirely from `policy.yaml` + taint + secrets + paths — it never imports `envelope`, never reads `envelope-state.json`, never references an autonomy level (`grep envelope hooks/gate.py` → 0 in code; only two *protected-path* strings in `policy.yaml`). The **only** consumers of `levels` are `render_dashboard.py:277` (draws a bar) and the tests.

→ **The dial turns and is connected to nothing.** Autonomy is *static* (whatever `policy.yaml` fixes), not *earned*. The agent is gated — but not by a graduated envelope. This is exactly PM review §4 P0. **v0.8 §3 bullet "earned, calibrated autonomy" and §10 growth-primitive #4 are display-only today.**

### 2. Door §7 topology (nesting parent + fan-in + per-connection auth) → ❌ **UNBUILT**

`scripts/door.py` is the *minimal* door: read tools (`readOnlyHint`) + `propose_*` that append to the proposals inbox. **Single-writer is preserved and real** — the door never commits; the gate processor is the sole writer (`door.py:1-5`). Good.

But the three things §7 rests on are absent:
- **No MCP-proxy / parent nesting** — the door exposes 5 fixed tools; it does not front or forward to other MCP servers (`grep proxy|forward|upstream|parent door.py` → none).
- **No per-connection principal auth** — `door.py` has no principal/identity/auth at all. `principal_auth.py` exists and is solid (HMAC, keys outside repo) but is consumed by the *envelope*, not the door.
- **No fan-in attribution** — no multi-harness connection identity.

→ **v0.8 §7 is design-direction, not build.** The harness-agnostic corner (§9 corner c) is aspirational today. What's real: Tier B (Claude Code, full-trust) + a minimal read+propose door for MCP clients (a thin slice of Tier A).

---

## Foundational claims — verified ✅ BUILT & TESTED

| v0.8 claim | Verdict | Evidence |
|---|---|---|
| Payload-inspecting gate, **full surface** (§9 corner a) | ✅ **strong** | `gate.py:115` — bash-egress, sensitive-read, synced-path-as-send, param secret scan, base64 decode, taint, protected paths, mandatory outbound-content scan, unknown-tool→send default; fail-closed (`:268`); unconditional circuit breaker (`:41`, missing/corrupt = deny) |
| Owned / exit=clone / **per-principal encrypted** (§3, §11) | ✅ | `crypto_store.py` — Fernet AEAD; `_assert_key_outside_repo` (`:37`) hard-fails if keys are in the repo; per-principal keys 0o600; self-ledgered reads |
| **Tamper-evident** ledger w/ lineage (§1, §11) | ✅ | `hashchain.py` — `hash=sha256(prev_hash+canonical(body))` (`:31`), `verify()` catches prev-hash/hash breaks (`:144`); `verify_chains` green |
| **Provable deletion** (owned invariant) | ✅ | `deletion.py` — `_shred_node_content` *unlinks* side-store/target files (`:100`), emits `content_shredded` L9; chain hashes references so shred doesn't break it. Real erasure, not event-only |
| Principal auth (CN-1) | ✅ built, ⚠️ **replayable** | `principal_auth.py` HMAC under keydir-outside-repo. **But `signing_payload` (`:46`) binds only `signal_type\|path\|principal_id\|outcome` — no nonce/timestamp, and `edit_distance` is unsigned.** A captured endorsement sig is replayable and its edit-distance is malleable → the known HIGH-sev finding stands |
| No individuation surface | ✅ (guarded) | `audit_individuation_ci.py` in CI; dashboards render per-skill |

---

## Claims stronger OR weaker than v0.8 credited

**🟢 Stronger — Multi-model portfolio via a hooked conductor (§8).** v0.8 §12 marked this ⚠️ "not exercised as a named path." In fact the **mechanism already exists**: a locally-hooked Claude Code calling ChatGPT/DeepSeek via bash or an API call passes through `inspect()` — `bash-egress-scan` + mandatory `outbound-content-scan` (`gate.py:132,177`) already inspect the outbound payload and ledger it. So §8's "one gate over Claude + ChatGPT + DeepSeek, payload-inspected, on your record" is **supported by built code** for the conductor pattern — only the *named, tested* path is missing. **Upgrade ⚠️ → 🟡 mechanism-real.**

**🟡 Transfer (§10 / A-P3).** The *instrument* is built (`transfer.py` — cohorts, `receiver_delta`, `passes_preregistered_rule`, `pooled_interval`, byte-identical `restore_version`). Whether transfer *works* is unproven — needs real collaborators. Instrument ✅ / result ⚠️ (unchanged).

**❌ Team / joint operation (§10).** Single-user primitives exist; the multiplayer wiring (co-approval across N humans, live hand-off) is not built. Correctly a *growth hook*, not a present claim.

**❌ Harness-agnostic second adapter / MCP proxy (§7, §9c).** FR5 seam exists by design (`adapter/`), but the second adapter and the MCP-proxy path are unbuilt.

---

## What this means for the anchor

**The anchor survives — because it rests on the built core, not the two gaps.**

- "**The solo control plane you own — one gate, one record, one policy**" is **TRUE today** for a Claude Code user: the gate (full-surface payload inspection), the record (tamper-evident hash-chained ledgers), the policy (`policy.yaml`), ownership (per-principal crypto, exit=clone), and provable deletion are all built and pass 214 tests.
- Two claims must be marked **forward-looking** until built:
  1. **"Earned, calibrated autonomy"** (§3 bullet 3, §10 primitive 4) — the envelope is **display-only**; wire it into the gate or stop claiming *earned* autonomy. **This is the #1 fix** — it's the differentiator that separates the anchor from "Claude Code hooks + a policy file."
  2. **Harness-agnostic via the §7 door** (§9 corner c) — today it's "Claude Code full-trust + a minimal read/propose door." The parent-proxy/fan-in/per-connection-auth topology is the build that makes corner (c) real.
- One claim is **safer than we thought**: multi-model governance via a hooked conductor (§8) already works at the mechanism level.

**Fix order implied:** (1) envelope→gate enforcement [makes the solo differentiator real], (2) sign the full L8 payload incl. nonce+edit_distance [closes the replayable-sig hole that lets a forged reaction move autonomy], (3) door §7 topology [makes harness-agnostic real]. (1) and (2) are the *solo* anchor; (3) is the *portfolio/fleet* extension.

---

## Patch applied to v0.8 §12

The §12 table statuses are updated in `positioning-v0.8.md` to the verified verdicts above (⚠️→✅ where code confirms; ❌ where confirmed inert/unbuilt; 🟡 where the mechanism exists but the path is untested), each with a code citation.
