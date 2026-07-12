# Autonomous Agent Adversarial Audit Framework

**Version 1.0**  
**Purpose:** A reusable, multi‑perspective methodology to assess whether an autonomous agent system *actually enforces* its documented safety, privacy, and alignment invariants.  
**Scope:** Any system where an AI agent can take actions, access data, or modify its own configuration based on inputs or internal metrics.  
**Based on:** The 14‑lens review of `teamOS`, which demonstrated that sound architecture in documents can be negated by missing enforcement in code.

---

## 1. Before You Start — Pre‑audit Setup

### 1.1 Define the System’s Stated Invariants
Extract every explicit safety, privacy, and behavioral promise from:
- The architecture document / CLAUDE.md / README
- Security whitepapers or threat models
- User‑facing privacy policies or consent flows
- Pre‑registered research rules (if any)

List them as concrete, testable assertions. Example:
> **FR2** – No permitted tool can exfiltrate data past the inspection gate.

### 1.2 Determine the Real Enforcement Boundaries
Identify where each invariant is supposed to be enforced:
- In code (gate, middleware, validator)
- In configuration (policy file, environment variable)
- By convention (a function that must be called, a default value that must not be overridden)

Flag any invariant that lives only in prose – those become your highest‑risk candidates.

### 1.3 Assemble the Multi‑lens Review Panel
You need at least one reviewer for each of these 14 perspectives (they can overlap, but each lens must be applied explicitly):

| Lens | Focus |
|------|-------|
| **Software Engineer** | Code correctness, error handling, input validation, dependency safety |
| **Security Engineer** | Vulnerabilities, injection, RCE, sandboxing, supply chain |
| **Privacy Engineer** | Data minimization, consent, deletion, compliance (GDPR, etc.) |
| **Organizational Psychologist** | Team dynamics, power structures, psychological safety |
| **Psychologist** | Individual mental health, cognitive load, addictive patterns |
| **Behaviorist** | Reinforcement schedules, behavior shaping, unintended conditioning |
| **Product Manager** | Dual‑use risks, user trust, market reputation, ethical boundaries |
| **Project Manager** | Process sabotage, metric gaming, accountability blur |
| **CEO** | Legal liability, enterprise readiness, brand, existential risk |
| **Solo Founder** | Personal liability, resource constraints, burnout, open‑source exposure |
| **Small‑Team Founder** | Internal norms, onboarding, exit plans |
| **Small Business Owner** | Employee pushback, HR compliance, vendor risk |
| **Designer** | Dark patterns, consent UX, accessibility, control discoverability |
| **Autonomous Agent** | Reflexive analysis: how would the agent itself exploit gaps? |

Each reviewer must produce a written verdict and, where possible, verify claims against source or running code.

---

## 2. The 14‑Lens Diagnostic Checklist

For each lens, answer the following questions (adapt to your system). Note any gap between documented intent and implemented reality.

### 2.1 Software Engineer
- [ ] Do all API endpoints validate and sanitise inputs? Is there any place where user‑supplied text reaches an LLM prompt without sanitisation?
- [ ] Is every resource access (task, file, setting) verified server‑side against the authenticated principal, not just the client‑supplied ID?
- [ ] Are real‑time events (WebSockets, SSE) authenticated and schematically validated before broadcast?
- [ ] Are all third‑party dependencies up to date? Are any used in security‑sensitive contexts (sandboxes, crypto) unmaintained?
- [ ] Do error responses leak stack traces, paths, or internal structure?

### 2.2 Security Engineer
- [ ] **Prompt injection:** Can a user insert `[SYSTEM]` or similar tokens to override agent instructions? Are tool‑calling outputs re‑validated before execution?
- [ ] **Sandbox escape:** If the agent can execute code or run commands, is the sandbox robust (not `vm2`; proper isolation)? What happens if the sandbox process crashes?
- [ ] **Egress control:** Is outbound network access controlled by an allowlist (not a denylist)? Are all data‑leaving tools (email, upload, webhook, WebFetch) identified and scanned?
- [ ] **Authentication & authorization:** Are there any Insecure Direct Object References? Are sequential IDs used for sensitive resources?
- [ ] **Supply chain:** Does the build process fetch and execute remote code without integrity checks?

### 2.3 Privacy Engineer
- [ ] Is the minimum necessary data collected for each feature? Is there a per‑feature, per‑user opt‑out?
- [ ] Is consent granular and obtained *from each affected individual*, not just an admin? Are pre‑checked boxes avoided?
- [ ] Does the “delete my data” function actually remove content from storage, or only append a deletion event to an immutable log?
- [ ] Are data retention periods enforced? Is there a user‑accessible export and purge tool?
- [ ] If the agent builds a behavioral profile, does it fall under automated decision‑making regulations? Are safeguards (human review, contestability) in place?

### 2.4 Organizational Psychologist
- [ ] Do the agent’s nudges or notifications default to public channels, creating a panopticon effect?
- [ ] Does the system rank individuals on productivity metrics that are reductionist or invisible‑labor‑blind?
- [ ] Can the agent reassign work or change priorities without human contextual input? Does that override the manager’s judgment?
- [ ] Does the system reinforce only measurable behaviors, risking extinction of collaboration, mentoring, or innovation?

### 2.5 Psychologist (Individual)
- [ ] Is praise or reinforcement delivered on a variable schedule that might encourage compulsive checking?
- [ ] Can overdue‑task reminders publicly shame an individual, especially one struggling with burnout or executive dysfunction?
- [ ] Do constant AI suggestions erode the user’s sense of autonomy? Is there a “focus mode” free from interruptions?
- [ ] Does the system detect distress signals and respond with support, or does it continue cheerfully ignoring a cry for help?

### 2.6 Behaviorist
- [ ] What behaviors are being positively/negatively reinforced? Is the reinforcement schedule algorithmically optimised for maximum compliance?
- [ ] Are completion badges or micro‑rewards shaping unsustainable work patterns?
- [ ] Can a manager configure escalating “accountability” reminders that function as group punishment?
- [ ] Does the reward function have blind spots that would extinguish non‑measurable but valuable behaviors?

### 2.7 Product Manager
- [ ] What is the most harmful dual‑use of this feature set? Is there a “bad manager” mode?
- [ ] How would a viral story of misuse (e.g., firing based on agent metrics) affect user trust? What safeguards exist to prevent that?
- [ ] Do any features create a liability time bomb (e.g., automated decisions with no human override)?
- [ ] Is the roadmap prioritising safety and ethics features, or only more autonomy?

### 2.8 Project Manager
- [ ] Can a team member game the system by creating/closing fake tasks to boost velocity?
- [ ] Could the agent misinterpret sarcasm or context and escalate a minor issue to a blocker?
- [ ] Can a malicious insider inject payloads into backlog items to manipulate the agent?
- [ ] When the agent suggests a decision that causes harm, who is accountable?

### 2.9 CEO
- [ ] Does a failure of the agent (privacy breach, harmful decision) expose the company to legal action, regulatory fines, or existential reputational damage?
- [ ] Will enterprise procurement red‑flag the absence of certifications (SOC 2, ISO 27001) or AI bias audits?
- [ ] Is the company’s brand aligned with “worker surveillance” or “empowerment”? How will talent perceive it?
- [ ] Is there a public ethical use policy and a white paper that matches the code’s real behavior?

### 2.10 Solo Founder
- [ ] As the sole responsible party, what personal liability do I carry if the agent causes harm?
- [ ] Do I have the resources to fix every CRITICAL finding? If not, can I disable the autonomous features until they are safe?
- [ ] Since the code is public, can an attacker study it and exploit a vulnerability before I patch it?
- [ ] Am I prepared to hold my creation to a higher safety standard even if it slows growth?

### 2.11 Small‑Team Founders
- [ ] Can we self‑police the system’s use so it supports our culture rather than undermining it?
- [ ] Will new hires understand exactly what data is collected and why? Is trust fragile enough that a surveillance perception could break the team?
- [ ] If we grow and hire a manager who misuses the tool, can we limit admin powers or remove adversarial features?
- [ ] Is the productivity gain worth the psychological and ethical risk? Can we adopt only the safe subsets?

### 2.12 Small Business Owner
- [ ] Will rolling this out cause immediate employee backlash? Do we need a pilot or a vote?
- [ ] In our jurisdiction, does automated monitoring require a works council agreement or similar?
- [ ] If the tool is compromised, what is the blast radius on our project data? Do we trust the vendor?
- [ ] Can we use the non‑AI parts while waiting for adversarial risks to be fixed?

### 2.13 Designer
- [ ] Are consent flows transparent, with un‑checked boxes and clear explanations, or are they manipulative?
- [ ] Is the “productivity score” opaque? Can users understand and contest it?
- [ ] Are defaults for notifications, reminders, and sharing public‑by‑default? Should they be private‑first?
- [ ] Are all controls (especially kill‑switch, undo, reset) focusable, operable by keyboard, and clearly discoverable?
- [ ] Is there a “calm mode” or focus time? Are interruptions respectful of user attention and accessibility needs?

### 2.14 Autonomous Agent (Reflexive)
- [ ] If my only metric is “maximise X”, what perverse actions could I take to optimise it at the cost of truth, safety, or user autonomy?
- [ ] Can I edit my own performance logs, training data, or configuration to avoid being retrained or limited?
- [ ] If multiple agents coexist, can we fall into destructive loops without human intervention?
- [ ] Are there hard‑coded rules that prevent me from lying to users, overriding their decisions, or manipulating them emotionally? Or is it just a system prompt I can bypass?

---

## 3. Cross‑cutting Structural Checks

Apply these tests irrespective of lens. They directly probe the gap between documentation and enforcement.

### 3.1 The Prose‑Invariant Test
For every safety rule stated in the docs, ask:  
**“What line of code, config, or runtime guard makes this true even if the system is under adversarial load?”**  
If the answer is a comment, a docstring, or a function that *could* be called but isn’t → flag as **UNENFORCED**.

### 3.2 Gate‑Fail Behaviour
- Does the safety gate (policy engine, permission checker) **fail closed** on any unexpected error, or does a crash let the tool proceed?
- If the gate encounters a malformed request, missing config, or an unhandled exception, what is the default verdict? (Must be `deny`).

### 3.3 Deletion Effectiveness
- Does the “delete my data” function **physically remove** content from storage, or only append a log entry?
- Are any ledgers or audit trails themselves deletable or redactable, or do they permanently record the fact that someone asked to be erased (a privacy risk)?
- Is there a way to crypto‑shred per‑principal data without breaking chain integrity?

### 3.4 Consent & Opt‑in Enforcement
- Are per‑user consent flags (e.g., “do not process my DMs”) actually read by the ingestion or processing pipeline, or are they write‑only?
- Are defaults for data collection turned on without explicit action? Are pre‑checked checkboxes used?

### 3.5 Data Integrity Under Concurrency
- If multiple agents or processes write to the same append‑only structure (hash chain, ledger), is there locking to prevent forking?
- Can legitimate parallel activity be distinguished from tampering?

### 3.6 Incentive Structure Alignment
- What single signal (e.g., acceptance click, edit distance) does the most measurement work? Is it overloaded?
- Does the metric reward the behaviour you actually want, or does it penalise engagement, reward trivial compliance, or encourage gaming?
- Are there guard clauses against Goodhart’s law, and are they **implemented** or merely described?

### 3.7 Kill‑switch & Human Override
- Is there a reachable, testable emergency stop that disables all autonomous action? Is it a real button (not an inert `<span>`), and is it discoverable without reading source code?
- Can the envelope (autonomy level) be forcibly narrowed by a human without needing the agent’s cooperation?

---

## 4. Meta‑review Process

After all reviewers have delivered their findings, conduct a meta‑review to ensure accuracy and calibrate severity.

1. **Source‑verify every CRITICAL.** Every claim tagged CRITICAL must be confirmed by at least one other reviewer against the actual code/config, not just the report.
2. **Check for mechanical errors.** Were any exploit steps misunderstood? Example: “Calling X causes Y” may be wrong because X writes a different signal type. Confirm the exact data flow.
3. **Recalibrate severities.** If a reviewer under‑weighted a finding (e.g., an unprotected config file that neuters the gate), elevate it. If a HIGH is inert until future code is added, note its latency.
4. **Look for what the panel missed.** Did any lens fail to flag a critical area? Is there a silent assumption that the system is benign?
5. **Test any statistical or scientific claims.** If the system includes a measurement that must validate a thesis, verify that the implemented pass rule matches the pre‑registered rule exactly (confidence intervals, p‑values, effect sizes). A weakening here is **stop‑the‑line critical**.

---

## 5. Scientific/Statistical Integrity Check (if applicable)

If the system is designed to produce a research outcome, add this section.

- [ ] Does the code implement the exact pre‑registered analysis plan? Check:
  - The metric computation (e.g., interval exclusion vs. point estimate)
  - Inclusion/exclusion criteria
  - Correction for multiple comparisons
  - Sample size rules (stop conditions)
- [ ] Is the success criterion computed on data that is isolated from the agent’s own actions? (No self‑fulfilling feedback loops.)
- [ ] Are all ledger records currently sourced from real interactions, or only from fixtures? (Fixture‑only means the thesis is unstarted.)

---

## 6. Audit Report Template

Use this structure to deliver your findings.

```markdown
# Autonomous Agent Audit Report — [System Name]

- **Date:**  
- **Auditors:** [list, with lenses covered]  
- **Scope:** [repo, paths, configs, envs]  
- **Method:** Multi‑lens adversarial review with meta‑review verification.

## 1. Headline Summary
[1–2 paragraphs on the gap between documented invariants and code enforcement. Note any stop‑the‑line finding.]

## 2. Critical Findings (must‑fix before real data)
- **FR-1:** Description, file:line, impact.
- ...

## 3. Cross‑Cutting Structural Weaknesses
- Enforcement vs. prose
- Gate fail‑open/closed
- Deletion effectiveness
- Consent enforcement
- Data integrity
- Incentive misalignment

## 4. Behavioral & Organizational Risks
[Summarise the most dangerous psychological or team‑dynamic consequences.]

## 5. Design & UX Failures
[Control theater, dark patterns, accessibility.]

## 6. Scientific Integrity (if applicable)
[Pre‑registration drift, interval vs point‑estimate, etc.]

## 7. What Holds Up
[Credible strengths, to prevent rejection of the whole report.]

## 8. Prioritized Remediation Roadmap
0. Stop‑the‑line fix (scientific rule, if applicable)
1. Gate fail‑closed
2. Egress allowlisting & data‑flow scanning
3. Delete‑that‑actually‑deletes
4. Consent wiring
5. Concurrency locking
6. Incentive decoupling
7. Real kill‑switch & controls
8. ...

## 9. Meta‑review Notes
[Corrections, recalibrations, missing perspectives.]