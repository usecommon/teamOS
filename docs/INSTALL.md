# Team OS — Onboarding & Install (hand-assembled path)

This is the manual setup (NEW-1) a non-builder follows to run the compiler
(FK4), the Day One Brief (FK5), and the loops (FK6) **before** the FK6c kit
automates it. The kit later automates exactly this checklist.

Everything here runs on **your own footprint** — no collaborator data, no
account policy. Team OS dictates nothing about your sources; it reads only what
you configure and toggle on.

---

## 0. Prerequisites

- **Python 3.10+** and **git**.
- **Claude Code** (the harness) — the runtime of record is Claude Code Desktop +
  local scheduled tasks.
- **Owned inference for the loops (Plane A):** an API key **or** a local model.
  Team OS's own connectors run on owned inference so it can operate independent
  of — and excluding — your Claude account. (You can explore the compiler/brief
  without this; unattended loops need it.)
- A machine that **stays on** for scheduled runs.

## 1. Clone + install

```bash
git clone https://github.com/usecommon/teamOS.git
cd teamOS
python3 -m pip install -r requirements.txt
make test            # 138 tests + schema/mapping gates should pass
```

## 2. Review the hooks — this is YOUR security control (signing-lite, CN-3)

The gate hook runs with hook privilege on your machine. **You** verify it before
activating it — that review is your control over your own trusted computing base.

```bash
$EDITOR hooks/gate.py        # ~190 lines, readable in ~15 minutes
$EDITOR hooks/BEHAVIOR.md     # the one-page spec the code must match
```

Confirm the code matches the spec (the decision table, "no network / no language
model", reads only stdin + policy + the ledger it appends to). Only proceed if
you're satisfied.

## 3. Activate the gate

Merge the fragment into your project settings so every tool call is gated +
ledgered:

```bash
mkdir -p .claude
# merge hooks/settings-fragment.json into .claude/settings.json
# (it registers hooks/gate.py as a PreToolUse hook)
```

Verify:

```bash
python3 scripts/teamos.py doctor      # "gate activated: yes"
```

## 4. Configure your sources (opt-in, policy-neutral)

Edit `config/connectors.json`:

- Set `inference` to your backend (`owned` + `api_key` or `local_model`).
- Add your real sources; leave `enabled: false` until you want them read.
- Set the Slack DM `target` to your **own authenticated Slack user id** (this is
  the only identity whose ✓/✗ reactions count — CN-1).

Nothing is read until you toggle a source on. The optional `allowlist` (empty by
default) holds any rule you or your org want enforced; it ships empty of opinion.

## 5. Set up your encryption key (keys live OUTSIDE the repo)

Your personal store is encrypted with a key that must never be committable
(exit = clone invariant). Keep the key dir outside the repo, e.g.:

```bash
mkdir -p ~/.teamos/keys        # NOT inside the cloned repo
```

`scripts/crypto_store.py` refuses a key dir inside the repo by construction.

## 6. Compile your footprint (FK4)

```bash
python3 scripts/teamos.py compile \
    --footprint <dir-of-your-artifacts> \
    --cc ~/.claude \
    --out stores
```

You get a job graph (recurring work), imported skills from your Claude Code
commands, and a profile from your CLAUDE.md. Imperative/injected content in old
docs is quarantined, never compiled. Raw ingest is not retained (distill-then-
discard).

## 7. See your Day One Brief (FK5)

```bash
python3 scripts/teamos.py brief --out stores      # dry-run render
```

To deliver it live to Slack on a schedule, wire the brief into a local scheduled
task with your gate active and Slack target set. The send traverses the gate and
is ledgered; ✓/✗ reactions are harvested deterministically into L8.

## 8. Run the loops (FK6)

```bash
python3 scripts/teamos.py loop --out stores       # one pass, produces shadow drafts
```

For the real thing, register this as a **local scheduled task / cron** on your
always-on machine. The 14-day unattended streak and the 4-week A-A4 clock are
measured here. Each run is checkpointed (a kill mid-run resumes) and anchors its
chain heads off-box.

## 9. Verify integrity anytime

```bash
python3 scripts/teamos.py verify        # every ledger chain verifies
```

---

## For collaborators (before your data flows — FK7)

You will additionally: sign the one-page data notice
(`docs/fk4-pre-threat-and-basis.md` §6 — Claude Code + the builder's hooks on
your machine, the hook-diff review in step 2, your own inference, an always-on
machine; in return: the kit, your own Brief, your own loops), and receive shared
skills only through the promotion gate (PII scan + eval floor + signed review).
Your personal store is encrypted with your key; no one else can read it, and any
read of it lands in your own access feed.

## Troubleshooting

- `make test` fails on import → `pip install -r requirements.txt`.
- `doctor` says gate not activated → step 3.
- Brief has no content → run `compile` first (step 6); it needs `job_graph.json`.
- Harness version drift → re-run `make test`; the adapter halts on an unpinned
  surface by design (fix the pin only after the suite passes).
