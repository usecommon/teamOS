**`v0.1 — 2026-07-10`** *(FK1 Step 0 — schema extraction; STATUS: PENDING HUMAN REVIEW)*

# docs/schemas/ — the canonical store-model contracts

One-time transcription of the architecture's prose schemas into machine-readable
JSON Schema (draft 2020-12), per FK1 Step 0 (fork validation plan, R-02).
**After human review, these files are the contract** — the prose is the rationale.
Post-review edits require human review; these files are never hand-curated silently.

| Schema file | Extracted from | What it defines |
|---|---|---|
| `ledger-common.schema.json` | arch §5.2 (practitioner bar), fork FK2 (hash-chaining) | Shared ledger-record envelope: identity, UTC timestamp, agent identity, hash chain |
| `ledger-l1-execution-trace.schema.json` | arch §5 L1 (OTel GenAI/MCP semantic conventions; content external by reference) | Execution-trace span records |
| `ledger-l2-gate.schema.json` | arch §5 L2, §7.3 action manifest; mainline S1 (distinct gate-passed vs posture-narrowed outcomes) | Decision/gate records |
| `ledger-l3-memory-write.schema.json` | arch §5 L3 (MemLineage pattern), §3.2.1 | Memory-write lineage records (the load-bearing lineage set) |
| `ledger-l4-knowledge-exchange.schema.json` | arch §5 L4 | Inter-agent transfer records (fork: written only at FK7+, schema extracted now) |
| `ledger-l5-delegation.schema.json` | arch §5 L5 | Delegation/identity chain records |
| `ledger-l6-version.schema.json` | arch §5 L6 (git-backed) | Version-history records |
| `ledger-l7-eval.schema.json` | arch §5 L7 (keyed to L6) | Per-invocation evaluation scores |
| `ledger-l8-human-signal.schema.json` | arch §5 L8 + §5 minimization (V3); fork SE-2 (content-by-reference in erasable side-store), CN-1 (principal-authenticated) | Human-signal records |
| `ledger-l9-deletion.schema.json` | arch §5 L9, §5.3 (tombstones, derivation severing, third-party entry) | Retention/deletion records |
| `ledger-l10-environment.schema.json` | arch §5 L10 | Environment-state records |
| `corpus-entry.schema.json` | arch §3.3.2 (block atomicity), §3.3.4 (typed entries), §3.3.1 (links computed, never stored) | Typed corpus entry (frontmatter + blocks) |
| `lineage-sidecar.schema.json` | mainline plan F1 (PROV-lite JSON), arch §3.2.1, §5.1 (W3C PROV core classes) | Per-entity lineage sidecar carried by corpus/skill/profile files |
| `skill.schema.json` | arch §10.2 store 2 (SKILL.md pattern + capability manifest), §5 L6/L7 keys | Skill registry entry |
| `scope.schema.json` | arch §3.1 (five scopes × three object types) | Scope node in the cascade |
| `stores.schema.json` | arch §10.2 (the five stores) | The store manifest (which stores exist, owner, format, portability) |

Conventions: snake_case field names; all timestamps ISO-8601 **UTC**; content that is
sensitive or third-party is stored **by reference** (`*_ref` fields), never inline
(L1/L4/L8 minimization rules); `additionalProperties` left open for forward
compatibility — `required` carries the prose field list.

The FR1 field inventory (the isomorphism denominator) is generated mechanically from
these files by `scripts/field_inventory.py`; the adapter's mapping annotations live in
`adapter/mapping.yaml`.
