"""teamOS adapter — the ONLY code that touches harness internals (FR5 insulation).

Translates harness paths/formats into the docs/schemas/ contracts:
  commands  -> skill registry entries      (skill.schema.json)
  CLAUDE.md -> scope nodes + corpus entries (scope / corpus-entry / lineage-sidecar)
  transcripts (JSONL) -> L1 execution-trace spans (ledger-l1)

When the harness API drifts, fix this module, not the callers.
"""

from .adapter import (
    HarnessPinError,
    assert_harness,
    load_pin,
    commands_to_skills,
    skill_to_command_md,
    claude_md_to_scopes,
    transcript_to_l1_spans,
)
