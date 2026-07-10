**`v0.1 — 2026-07-10`** *(FK4-pre — threat model lite + lawful-basis note; gates FK4 ingestion. DRAFT — pilot-source decision + collaborator notice sign-off pending principal)*

# FK4-pre — Threat Model (lite) + Lawful-Basis Note

Scope: n≤3 pilot on the runtime of record (path (a)). Gates FK4 (first real-footprint ingestion). No real data flows until: this doc exists, every FK item maps to ≥1 persona, the pilot-source decision is recorded, and collaborators sign the data notice.

---

## 1. Composition & trust boundaries (STRIDE-lite over the fork)

Components: harness (Claude Code) · gate hooks · ledgers (on-disk, hash-chained) · stores (corpus/skills/profile) · connectors (read MCPs + Slack DM out) · scheduled loops (path a) · the door + proposals inbox (FK6c, later).

Trust boundaries:
- **B1** external input sources → the agent (untrusted content; taint §7.7).
- **B2** harness → hooks/ledgers (self-attestation residual — see §3).
- **B3** principal ↔ agent (principal-authenticated signals only, CN-1).
- **B4** local runtime ↔ cloud path (b) (fenced door only; out of FK4 scope).
- **B5** principal ↔ collaborator scope (per-principal encryption, FK7-pre; no data crosses until FK7).

## 2. Personas → controls (every FK item maps to ≥1)

| # | Persona | Attack | Control | FK item |
|---|---|---|---|---|
| P1 | External attacker via input sources | Injection in ingested content adds a plan step / changes a recipient / triggers a tool | Taint: untrusted content supplies values, never plan structure; compilation-injection quarantine | FK2 gate, FK4 quarantine |
| P2 | Compromised harness update | Malicious harness defeats hooks by construction | **Accepted undefended residual** (§3); mitigation = version+surface pin + update review; re-run FK1 adapter + FK2 headless suites every update | FK1 pin, FK2 |
| P3 | Builder-as-malicious-principal | Principal exfiltrates own+others' data | Payload inspection on sends (verbatim scan); default-deny sharing; per-principal encryption bounds blast radius | FK2, FK7-pre |
| P4 | Malicious/compromised collaborator | Installs kit, PRs a poisoned skill | FK7 CI (PII scan + eval floor) + human hook-diff review (signing-lite, m8) | FK7 |
| P5 | Compromised-principal-surface (X-3) | One hijacked Slack session forges acceptances → widened autonomy | Single-factor accepted at pilot scale; FK6b ceiling categories bound blast radius; L8 counts only principal-authenticated ✓ | FK6b |

## 3. Accepted residual (chosen, not overlooked — council F13)

The trust substrate (hooks, gates, ledgers) executes **inside** the harness; a compromised harness update defeats them by construction — a component cannot attest to its own integrity. **Accepted undefended at pilot scale.** Mitigation: pin version+surface; review harness updates before adopting; auto-update mid-streak = HALT + streak paused (SE-5). **Mandatory revisit before any managed tier or merge-back.**

**Scan honesty (X-2):** the outbound scan catches **verbatim** secrets/identifiers only. Exfiltration-by-paraphrase through a sanctioned send is invisible to any pattern pass by construction — carried entirely by the taint rule + the send gate. Said out loud, not hidden in a residual clause.

**V1 deferral (CN-11):** the third-party notice/DSAR surface is mainline scope. Pilot mitigation = shared-space-default sources + the LIA names third-party exposure; erasure itself works (FK3).

## 4. Lawful-basis note (DPIA/LIA lite, n≤3)

- **Basis = consent** (genuinely free — pilot volunteers, no employment power-asymmetry). Recorded per collaborator; **revocable**; revocation reaches downstream copies via Ledger-9 propagation (FK3, proven).
- **Special-category data** (health etc.) appearing incidentally: **detect-and-exclude by default**, regardless of tier.
- **LIA coverage:** own footprint + collaborators' shared spaces. Names third-party exposure in shared spaces as a known, bounded risk (mitigated by shared-space-default sourcing + working erasure).
- **Objection/erasure rights:** any subject may object; FK3 deletion is the mechanism.

## 5. Pilot-source decision (PRINCIPAL'S CHOICE — pending, §3a)

The tool is policy-neutral; this is the responsible party exercising policy, not a product gate. **To be recorded here with rationale before FK4 runs.** See the choices posed to the principal alongside this draft. Default framing (fork §3a precedent): personal accounts + side-project workspaces eligible; employer workspaces excluded by the pilot user's own decision (personal-risk position + evidence portability — data you're not entitled to process yields results you can't demo or cite). **A-C2 scope limit (F11):** a green A-C2 on this source set validates compilability of *non-employment* footprints only.

## 6. Collaborator data notice (sign-off pending)

Before any collaborator footprint flows, each signs a one-page notice including the **install-cost/ops paragraph (CN-7):** Claude Code + the builder's hooks running on your machine, a hook-diff review you perform, your own subscription/inference, a machine that stays on for scheduled runs. What you GET is named: the kit, your own Day One Brief, your own loops. Consent is free and revocable.

---

**Exit (FK4-pre):** document exists ✅ · every FK item maps to ≥1 persona ✅ · pilot-source decision recorded ⛔ (pending principal) · collaborators sign the notice ⛔ (pending recruitment). **FK4 must not ingest real data until the two ⛔ close.**
