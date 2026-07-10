"""Posture detection + upgrade ledgering (FK6c). Onboarding probes for a CLI
footprint (~/.claude). Ladder: app-only -> app+CLI -> cli-native. A CLI
appearing later upgrades the posture; the upgrade is itself ledgered."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402

POSTURE_AGENT_ID = "teamos-posture/0.1"
LADDER = ["app-only", "app+cli", "cli-native"]


def detect(home_dir):
    """Probe for a CLI footprint. Returns the detected posture."""
    home = Path(home_dir)
    has_cli = (home / ".claude").exists()
    return "cli-native" if has_cli else "app-only"


def record_posture(home_dir, state_path, ledger_dir):
    """Detect + persist; ledger an upgrade (L2) when the posture climbs."""
    state_path = Path(state_path)
    current = detect(home_dir)
    prev = None
    if state_path.exists():
        prev = json.loads(state_path.read_text()).get("posture")
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"posture": current}))
    if prev is not None and LADDER.index(current) > LADDER.index(prev):
        hashchain.append(Path(ledger_dir) / "l2.jsonl", {
            "proposed_action": {"tool": "posture", "action_class": "config",
                                "target": f"{prev}->{current}",
                                "payload_digest": hashchain.sha256_str(current)},
            "verdict": "permit", "policy_version": "posture:0.1",
            "rule_id": "posture-upgrade",
            "inspection": {"checks_run": ["cli-probe"], "findings": []},
            "outcome": "gate_passed",
        }, POSTURE_AGENT_ID)
    return {"posture": current, "upgraded_from": prev if prev != current else None}
