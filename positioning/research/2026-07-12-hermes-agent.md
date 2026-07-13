# Hermes Agent (Nous Research) — profile (2026-07-12)

**Disambiguation:** "Hermes agent" = **Hermes Agent**, the open-source autonomous agent from Nous Research ([github.com/nousresearch/hermes-agent](https://github.com/nousresearch/hermes-agent)) — distinct from the Hermes 3/4 *models* (same lab). A third, unrelated: SubQuery Hermes (a decentralized MCP networking layer).

## What it is
A **self-hosted, model-agnostic, autonomous personal agent** — a **harness/runtime**, not a model, not a chatbot wrapper. MIT-licensed, first released Feb 2026. Tagline "the agent that grows with you." Python + TypeScript; single-curl install. ([hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com/))

## Capabilities
- **Self-improving skill loop** (signature) — after a task, autonomously writes a reusable Markdown skill file; skills self-improve in later use. Positioned vs OpenClaw (where skills are human-authored). ([turingpost](https://www.turingpost.com/p/hermes))
- Persistent hierarchical memory (FTS5 search + LLM summarization; Honcho user-modeling; 6 backends).
- Proactivity: built-in cron scheduler firing tasks in fresh sessions; spawns isolated subagents; runs unattended on cloud infra.
- 40+ tools, MCP integration, web/browser automation, vision, image-gen, TTS, sandboxed code exec across 6 backends.
- Gateways: Telegram, Discord, Slack, WhatsApp, Signal, Email, TUI/CLI.

## Governance / trust
Markets "safer-by-default" but controls are **capability guardrails, not a governance layer**: command allowlist + approval flows, whitelist tool activation, per-backend permissions, DM pairing auth, container isolation, injection/context scanning, credential filtering (post v0.5 hardening). HITL is thin/interactive (Ctrl-C, `/retry` `/undo` `/stop`). **Absent:** audit-ledger of every action, payload-inspecting gate, proven deletion/erasure, lineage-on-writes, default-deny sharing. Privacy = self-hosting, not enforced envelope. Open-source + self-hostable; hosted option via Nous Portal. ([bitcoin.com](https://news.bitcoin.com/what-is-hermes-agent-nous-researchs-self-improving-ai-explained/))

## Team / multi-user
Weak. Per-user API keys, "allowed users" lists, `AGENTS.md` shared instructions. **Single-principal**; no cross-person skill transfer, no shared-scope promotion gate, no individuation controls.

## Positioning / brand
Proactive, self-improving, autonomous, "grows with you." Parent brand is explicitly **anti-restriction** — Hermes 4 "aligned to you, not corporate policy," minimizes refusals. The agent inherits this. ([VentureBeat](https://venturebeat.com/ai/nous-research-drops-hermes-4-ai-models-that-outperform-chatgpt-without-content-restrictions))

## Traction
Nous Research; CEO Jeffrey Quesnelle (Web3 DNA). **Series A April 2025: $50M led by Paradigm, ~$1B token valuation.** GitHub stars reportedly ~214k by July 2026 (directional; heavy SEO/marketing coverage — treat claims as approximate). NVIDIA + MiniMax partnership signals.

## Implication for Team OS
Hermes is a **harness** at the same layer as Claude Code — a substrate Team OS could sit *on top of*, not a peer to beat. As a runtime: ride its capability, add the trust+team layer it lacks (door-scoped via its MCP integration; full only if it exposes hooks). As an out-of-box product: competitor only for the user who wants *no* governance. Its anti-restriction brand is **disqualifying for the org-side risk owner** — it cannot pivot to Team OS's buyer.
