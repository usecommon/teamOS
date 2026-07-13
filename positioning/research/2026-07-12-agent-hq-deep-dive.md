# GitHub Agent HQ & Mission Control — deep dive (2026-07-12)

**Bottom line:** Agent HQ owns the **PR-boundary control plane** for coding agents inside GitHub, with strong *coarse-grained* governance. Its gaps — no action-level gating, thin in-run observability, GitHub-ecosystem lock, coding-only, hosted-not-owned, admin-centric — are precisely the whitespace for a fleet control plane that governs *every tool call/command* across surfaces beyond GitHub.

## What it is
GitHub's repositioning of its platform into a **neutral, multi-vendor control plane for coding agents.** Announced GitHub Universe Oct 28 2025; extends (doesn't replace) Copilot. Vision: "Agents shouldn't be bolted on. They should work the way you already work." Bundled into paid Copilot subscriptions. ([github.blog](https://github.blog/news-insights/company-news/welcome-home-agents/))

## Mission Control
"A single command center to assign, steer, and track the work of multiple agents from anywhere" — consistent interface across GitHub, VS Code, mobile, CLI (not one destination). Assign work / assign an Issue to Copilot, Claude, or Codex (or all three to compare); run agents in parallel; monitor async sessions producing draft PRs; manage branches/PRs with 1-click conflict resolution and granular CI control. **The control surface is fundamentally the PR + Issue + branch model** — a monitoring/steering dashboard on Git artifacts, not a live per-action console. ([github.blog — pick your agent](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/))

## Which agents
Native Copilot + third-party **Claude** and **Codex** (public preview); **Jules, Devin, xAI** "on the way" (GitHub projects 6+ by mid-2026). **Cursor not on the list** — the roster is frontier *labs*, not rival IDEs. Real orchestration on GitHub's rails but shallow on agent internals (can't tune reasoning; each agent's tool loop is opaque). ([Neowin](https://www.neowin.net/news/github-launches-agent-hq-uniting-coding-agents-from-the-worlds-leading-ai-labs/))

## Control/governance primitives (control plane GA Feb 26 2026)
- **Per-agent identity** — `actor_is_agent` flag + `agent_session.task` events in audit log
- **Agent/model allowlisting** — admins define permitted agents/models per org/repo
- **Branch controls** — agents commit only to `copilot/*` branches, **never `main`**; can't approve/merge own work; human PR review mandatory
- **Sandbox + egress firewall** — sandboxed Actions envs, allowlisted hosts
- **MCP allowlist** — centralized MCP registry URL governs external tools
- **Custom-agent governance** — version-controlled `.github/agents/*.md` guardrails; enterprise-wide definitions
- **AI admin role** + pre-merge scanning (secrets, code security, supply-chain)

**Critical granularity finding:** control is **branch/PR/repo/session-level and environment-level — NOT action-level.** No per-tool-call or per-shell-command approval gate; in-run observability is thin; HITL = PR review, not per-action confirmation. ([GitHub changelog, Feb 26 2026](https://github.blog/changelog/2026-02-26-enterprise-ai-controls-agent-control-plane-now-generally-available/))

## Solo vs enterprise
Bifurcated. The orchestration surface is solo-usable on paid Copilot (Pro $10 / Business $19 / Enterprise $39; **third-party agents need Pro+ $39**). But the **control-plane value is admin/org-centric** — AI-admin role, allowlists, enterprise audit, MCP registry all live in enterprise settings for IT governing many devs. Solo dev gets a "nice multi-agent launcher." VentureBeat framed it as solving "too many agents, no central control." ([VentureBeat](https://venturebeat.com/ai/githubs-agent-hq-aims-to-solve-enterprises-biggest-ai-coding-problem-too))

## Limitations
GitHub-ecosystem locked (repos/PRs/Actions; hosted by GitHub/MS, not user-owned); coding only; async draft-PR (not interactive); **rate limits** (top complaint, kills real parallel fleets); weak conflict handling; thin observability; capability gap vs standalone Claude Code.

## Implication for Team OS
Whitespace vs Agent HQ = **action-level gating (every tool call/command) + owned (exit=clone) + ecosystem-agnostic (any agent, beyond coding) + solo-usable.** Agent HQ validates the category and has none of those four together.
