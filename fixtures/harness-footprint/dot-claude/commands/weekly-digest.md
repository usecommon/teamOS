---
description: Draft the weekly project digest from recent commits and inbox items
allowed-tools: Bash(git log:*), Read, Write
---

# Weekly digest

Collect the last 7 days of activity and draft the digest in the team's format:

1. Summarize merged changes from `git log --since="7 days ago"`.
2. List open decisions from the inbox.
3. Write the draft to `drafts/weekly-digest-<date>.md` in the standard three-section layout (Shipped / Deciding / Next).
