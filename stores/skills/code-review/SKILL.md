---
description: Review a diff or PR for correctness bugs, security issues, and convention violations; report findings ranked by severity with file:line and a concrete failure scenario.
allowed-tools: Read, Grep, Glob, Bash(git diff:*)
---

# Code review

A specialized, shared skill. Given a diff or PR:

1. Read the changed files and the surrounding code they touch.
2. Look for correctness bugs (wrong output, crash, edge case), security issues
   (injection, secret exposure, unsafe input), and convention violations against
   the team corpus.
3. Report each finding with `file:line`, a one-line summary, and a concrete
   failure scenario (inputs → wrong result). Rank by severity; skip nits.

Promote improvements through the shared-skills gate so every teammate's agent
inherits them.
