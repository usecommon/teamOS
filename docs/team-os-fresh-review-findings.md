<!-- VERSION: v1.2 | 2026-07-10 | audit trail — fresh-context review rounds 1+2+3 (R-01..R-16, H-1..H-4, CN-1..CN-12, AT-1..AT-9), REMEDIATED at v3.1/v3.2 -->
**`v1.2 — 2026-07-10`** *(audit trail — fresh-context review rounds 1–3; applied at v3.1 / v3.2 / v3.3)*

# Fresh-Context Review — Findings + Application Record
*Independent reviewer, no prior context, full 9-file set. Verdict: "nearly ready to start FK1, and not ready to finish it" — two blockers on the FK1/FK2 critical path, both fixed same day. Application map:*

| ID | Fix applied (v3.1) |
|---|---|
| R-01 | L3 lineage writer added to SPEC §6 FK2 (precedence trap closed) |
| R-02 | FK1 Step-0 schema extraction: prose → docs/schemas/, human-reviewed once, then canonical; "never hand-curated" scoped to post-extraction |
| R-03 | A-C4 denominator unified: job-graph nodes in both plans |
| R-04 | A-A4 fork-scale rule pre-registered; FK-2 may exit on existence proof with A-A4 inconclusive — stated |
| R-05 | Three path-(b) surface tests added to FK6c (real cloud run, missed-run, caps) |
| R-06 | m2/m3/m8 actually landed; fork-council register re-stamped v2.1 with the overclaim correction |
| R-07 | Round-2 register cited inline where F13/NEW-1 appear (file: team-os-fork-council-round2.md) |
| R-08 | CLAUDE.md invariant carries the path-(b) scope parenthetical |
| R-09 | Divergence entry classes defined; R18 counts architectural deviations only |
| R-10 | Emoji-poll = path-(a) primary; webhook moves to FK6c with the relay |
| R-11 | "Lightly edited" = normalized edit distance ≤0.2 (arbitrary-pending-baseline), both plans |
| R-12 | 3-item rubric (voice/sources/structure) + builder as second rater on collaborator artifact, kappa |
| R-13 | Validation-run posture declared before the A-A4 clock, logged in L2 |
| R-14 | FK8: ≥9 proposals before the acceptance rate computes |
| R-15 | FK-0 table reordered; FK3b deps += FK2; §C1 relabeled |
| R-16 | (Consistency clean — no action) |
| H-1 | Harness-update cadence now includes the FK2 headless-hook re-test |
| H-2 | Thin-history acknowledgment added to SPEC |
| H-3 | FK-3 exit reworded: merge-back activates, formative, demand effects unblindable at this n |
| H-4 | Carried by R-05's tests |

*The reviewer's full findings register and hostile read are preserved in the conversation record; this file is the finding→fix map.*


---
# Round 2 (council + adversarial, incl. attacks on round-1 register) — Application map (v3.2)

| ID | Fix applied |
|---|---|
| CN-1 (blocker) | L8 writer counts ✓ only from principal's authenticated identity; envelope consumes principal-attributed signals only; planted-third-party-✓ F-test added; CLAUDE.md carries the rule |
| CN-2 | Gate processor = deterministic code; LLM steps over proposals read-only/quarantined, never in commit path |
| CN-3 | signing-lite fully defined (signed commits + reproducible build + collaborator hook-diff review) and moved to FK6c exit criterion |
| CN-4 + AT-3 | A-A4 instrument = per-deliverable micro-pulse (≥40 points); FK-2 close restated as decision point (proceed/densify/re-sequence), never statistical pass/fail |
| CN-5 | Candidate transfer skill named: daily shared-repo activity summary (daily cadence, low person-specificity); FK6 exit += daily-cadence candidate exists |
| CN-6 | FK6 builds ≥3 recurring deliverables (designed capacity 4+ vs floor 3 — slack > 0) |
| CN-7 | Install-cost/ops paragraph added to the FK4-pre collaborator notice |
| CN-8 | FK6 pre-flight: loop volume vs usage limits; clock runs on API key if tight |
| CN-9 | Mainline kernel column closed (C3 added) |
| CN-10 | Does-not-validate += Class C / pillar 1 (green A-P3 supports pillars 2/3 only) |
| CN-11 | V1 third-party-notice deferral stated in FK4-pre with pilot mitigation |
| CN-12 | Lineage-rejection F-test added to FK2 (invariant now tested, not just stated) |
| AT-1/AT-5 | R-01 escalation and R-05 confirmed — both already fixed at v3.1; CN-12 closes AT-1's untested-component half |
| AT-4 | R-10 stands as revised (emoji poll primary; Socket Mode noted as requiring a resident listener path (a) doesn't have) |
| AT-6 | Outbound-content scan on sends = MANDATORY; residual reserved for what the scan provably can't catch |
| AT-7 | FK-1 attribution rewritten executably: adapter lossiness audit vs docs/schemas, not a counterfactual rerun |
| AT-8 | R18 green labeled formative (builder-classified instrument) |
| AT-9 | Survivors recorded: loops-before-doors, credential domains, inbox topology (with CN-2), taint plan-structure rule, exit=clone scoping, A-FK1 denominator design |

**Round-2 verdict honored:** the remediation-layer components (envelope-on-evidence, inbox topology, attribution, outbound scan) now carry the F-tests and adversary analysis the original components had. FK1 remains gated on R-01/R-02 only — both closed at v3.1.


---
# Round 3 (four-discipline councils + attacks on round-2 fixes) — Application map (v3.3)

| ID | Fix applied |
|---|---|
| SE-1 (blocker) | Deterministic reaction harvest (`reactions.get`, hook-gated); NO LLM in the evidence path; forged-textual-report F-test; CLAUDE.md carries the extended rule |
| SE-2 (blocker) | L8 = content-by-reference (per mainline V3 minimization) in an erasable side-store, chain hashes references; FK3 F-test: erasure reaches third-party content inside an L8 diff without breaking adjacent chain verification |
| SE-3 | Proposal-parser probe set: traversal / symlink / normalization / YAML-abuse, ≥2 independently authored |
| SE-4 | Path-(b) mitigations offered in setup: dedicated account (no other connectors) + summary-tier door views |
| SE-5 | Auto-update mid-streak = HALT + streak PAUSED, resume after suites; pinning-vs-patches tension named |
| SE-6 | Chain heads pushed to shared repo each loop run (evidence anchored off-box before A-P3 depends on it) |
| ME-1 | A-A4 headline = proxy↔downstream-use behavior (L1/L6-harvested); micro-pulse secondary; shared-method-variance honesty stated |
| ME-2 | CN-5↔NEW-2 contradiction resolved explicitly: NEW-2 waived for FK7 and recorded; independent-subject transfer deferred to confirmatory |
| ME-3 | Non-updated control skill per receiver (within-person diff-in-diff); edit distance normalized by input volume |
| ME-4 | Floor ≥25 (arithmetic honest); densify-at-week-2 = the PLANNED path |
| ME-5 | Floor activates week 3; trigger = two consecutive weeks <3 → review |
| EC-1 | **FR8 added:** weekly fork-overhead ledger + pre-registered abort threshold (>40% for 3 weeks → reassess vehicle) |
| EC-2 | Mechanism-not-market cap on A-P3, CN-10-style |
| EC-3 | Over-recruit 4–5; pre-registered dropout rule; collaborator benefit named in the notice |
| OB-1 | Narrowing automated (severity-class rejection → auto-step-down), widening slow |
| OB-2 | Fatigue check pre-registered (week-4 variance < half week-1 = satisficing flag) |
| OB-3 | Builder-footprint handicap: higher widening threshold during FK6 |
| OB-4 | Qualitative check folded into weekly pulse + ledgered; reaction-removal = point-in-time, no retract, ledgered |
| X-1 | First-install review made feasible: hook line budget + one-page behavior spec + reproducible build |
| X-2 | Scan honesty stated: verbatim only; paraphrase-exfil carried by taint + send gate, said out loud |
| X-3 | Compromised-principal-surface persona added; FK6b ceilings = blast-radius bound |

**Round-3 survivors:** loops-before-doors (4th consecutive hostile round), credential domains, deterministic commit path (concept), executable attribution, §3a, thin-history, decision-point framing. FK1 was never gated by this round; FK5 and FK3 must not close without SE-1/SE-2 — both now dispositioned.
