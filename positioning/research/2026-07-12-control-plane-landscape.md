# Agent control-plane competitive landscape (2026-07-12)

**Verdict:** The space is contested and richly funded — but almost entirely as **enterprise admin consoles**, **security-vendor firewalls**, and **harness-locked dev tooling**. The specific quadrant Team OS occupies — an **owned (exit=clone), harness-agnostic, action-level payload-inspecting** gate a **solo** principal runs over their own agents — has adjacent occupants on every side but **no direct competitor holding all four properties at once.** Real whitespace; the risk is incumbents pushing down-market, not saturation.

## The definitional split (why "control plane" is loose)
Three different things hide under "control plane": (a) **orchestrate/monitor** (run N agents, watch them); (b) **task/PR-level gate** (approve whole outputs, restrict branches); (c) **action-level gate** (inspect an individual tool call's *payload* and allow/deny before it executes). Almost everyone claims (c); very few ship it.

## 1. Coding-agent fleet managers (solo/dev)
Dominant model = **isolate + review the diff** (task-level, post-hoc), not per-action gating.
- **Devin / Agent Command Center** — action-level gating via Devin CLI (Deny→Ask→Allow, Read/Write/Exec/Fetch matchers, org denials). Solo; SaaS/local hybrid, not self-hostable. ([docs.devin.ai/cli/reference/permissions](https://docs.devin.ai/cli/reference/permissions))
- **Cursor 3.x** — "Agents Window" mission control; Auto-review routes each tool call through allowlist→sandbox→classifier→human. Action-level but gate is a classifier (taint surface). SaaS, not self-hostable.
- **GitHub Agent HQ** — assign/steer many agents; Enterprise control plane GA Feb 26 2026. Gates at **branch/PR/sandbox/policy** level, not tool calls. SaaS; paid Copilot.
- **Conductor** (conductor.build) — Mac app, parallel Claude Code/Codex/Cursor; **genuine action-level approvals** (shell/file/MCP/web before they run) — **but no sandbox, no payload/exfil inspection, runs at full user perms.** Local, solo, free (BYO sub). *Closest mainstream analog to a PreToolUse gate.*
- **HumanLayer/CodeLayer** — canonical action-level gate (`@require_approval`), OSS+SaaS. **Claude Code native** — subagents + per-tool-call PreToolUse hooks + `agent view`; the only mainstream tool with native per-tool-call gating *and* fleet monitoring. **Omnara** — relays approval to phone.
- Churned early 2026: Terragon, Vibe Kanban, Crystal, WhyLabs.
- *None inspects tool-call payloads for exfiltration; gates are prefix/allowlist/branch-based.*

## 2. Enterprise control planes (admin-facing, SaaS, mostly pre-GA on hardest features)
- **Microsoft Agent 365** — "the control plane for AI agents," $15/user/mo, GA ~May 2026; Entra Agent ID, shadow-agent quarantine, kill switch. **Foundry Control Plane** (preview) intervenes on tool calls/responses.
- **Google Gemini Enterprise** — Agent Gateway+Registry, IAM + **semantic governance** matching actions to intent, anomaly detection that "intervenes before the action completes." **Self-hostable via Google Distributed Cloud (air-gapped).** ~$21–50/user.
- **ServiceNow AI Control Tower** — broadest reach (30 systems); enforcement GA Aug 2026.
- **Glean Agent Access Policies** — deepest *runtime action-level* enforcement of any enterprise vendor: evaluates tool, user, **input arguments, returned payloads**, Block/Filter/Flag pre- and post-execution incl. remote MCP. **Self-hostable (cloud-prem).** But ~$60K+ ACV, enterprise-only.
- **AWS Bedrock AgentCore Policy** — "intercept every tool call before execution," Cedar-authored, framework-agnostic, consumption-priced, solo-usable — but AWS-SaaS, not self-hostable.
- Others: Salesforce Command Center (observability; gating in MuleSoft gateway), OpenAI Frontier (preview), SAP AI Agent Hub (no real-time action gating), Boomi (Bedrock-only kill switch). **Identity consolidating as a control layer** (Okta for AI Agents, Astrix→Cisco, Aembit, CyberArk) — governs *credentials*, not payloads.

## 3. AgentOps / observability
Canonical tools **observe, don't gate**: AgentOps.ai, Langfuse, LangSmith, Braintrust, Arize/Phoenix, Datadog LLM Obs — observe/eval/alert; only "gate" is offline CI merge-block. Exceptions: **Datadog AI Guard** (separate product) — genuine ALLOW/DENY/ABORT on every tool call, analyzes intent+arguments, blocks pre-execution; Preview, SaaS-only. Gateways (Helicone, Bifrost) block at LLM-request layer, not per-tool-call.

## 4. Runtime security / guardrails (closest to Team OS's gate)
Near-total M&A in 14 months: Invariant→Snyk, Lakera→Check Point, Prompt Security→SentinelOne, Protect AI+Portkey→Palo Alto, Robust Intelligence→Cisco.
- **True argument-level, OSS, self-hosted:** **Invariant Guardrails/MCP-scan** — DSL matching argument *values* + cross-call dataflow rules, runs locally — **but MCP-scoped** (gates MCP traffic, not bash/file/synced-paths). **Solo.io agentgateway** (CEL, Apache-2.0); **Obot**; **Docker MCP Gateway**; **Claude Code PreToolUse hooks** (tool_input → deny). The genuine "look inside the action" tools — overwhelmingly OSS.
- **Acquired incumbents** (Cisco AI Defense, Prisma AIRS, etc.) reach payloads but decide from **threat detectors** (injection/DLP), not declarative "deny if this action's target/recipient violates policy"; enterprise-only.
- Content-scanners (Lakera Guard, Pangea, Guardrails AI, NeMo) return a verdict your app enforces, prompt/output level.

## 5. Orchestration frameworks
**Builders, not control planes** — governance is a primitive you wire in. LangGraph `interrupt()`, OpenAI Agents SDK approvals — real action-level pause but enforcement lives in *your* code. CrewAI/n8n/Inngest/Temporal — HITL + RBAC at workflow/task level. None ships a fleet-level payload-inspecting gate over arbitrary agents.

## The four-corner test

| Product | Action-level (payload) | Self-hosted | Harness-agnostic | Solo-usable |
|---|---|---|---|---|
| Glean Access Policies | Yes | Yes (cloud-prem) | No | No (enterprise) |
| AWS AgentCore Policy | Yes | No (AWS) | Partial | Yes |
| Google Gemini Ent. | Yes | Yes (GDC) | Via registry | No |
| Conductor | **approvals only, no payload** | Yes (local) | Yes | Yes |
| Invariant MCP-scan | Yes (arg-value) | Yes (OSS) | **MCP-only** | Yes |
| Claude Code hooks | Yes | Yes | **No (CC only)** | Yes |
| Devin CLI perms | Yes | No | No | Yes |
| **Team OS (target)** | **Yes (full surface)** | **Yes** | **aspirational** | **Yes** |

Every commercial row misses ≥1 corner. OSS gateways hit a/b/d but are **MCP-scoped**. Conductor hits a/b/c/d but does **no payload inspection**. Claude Code hooks hit a/b/d but are **Claude-Code-locked**. **No product occupies all four with true payload inspection** (deny because a permitted tool's command/target/recipient would exfiltrate) for a solo self-hosting user.

## Implication for Team OS
- Team OS today ≈ **Claude Code PreToolUse hooks + a governance layer** (policy, tamper-evident ledger, envelope, provable deletion, lineage, transfer). That's 3/4 corners: action-level payload gating ✓, owned ✓, solo ✓ — **harness-agnostic ✗ (Claude-Code-locked)**.
- Differentiation vs the closest solo tools: vs **Conductor** — Team OS adds payload/exfil inspection + ledger + deletion; vs **Invariant** — Team OS gates the *full harness surface* (bash, file, synced-paths), not just MCP; vs **raw Claude Code hooks** — Team OS adds the record + bounded autonomy + deletion + transfer *above* the gate.
- **Whitespace = the full four-corner combination**, and Team OS is closer than anyone but must (a) build the harness-agnostic adapter (FR5 path), (b) move before Microsoft/Google/Glean push action-level gating down-market or an OSS MCP-gateway broadens past MCP.

*Caveats: several enterprise features pre-GA (announced ≠ shipping); some acquisition values reported not confirmed; a few official pages blocked automated fetch (quotes via press).*
