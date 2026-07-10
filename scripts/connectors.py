"""Connector config + policy surfaces (FK3b). Policy-neutral (fork §3a): enforce
whatever the config holds; hold no opinion; never refuse a configured source nor
add one that isn't.

Two ingestion gates:
  1. enabled (per source, default false) — always active; off => returns nothing.
  2. allowlist (global) — empty means no constraint; populated means only listed
     sources may ingest, even when enabled.

Every ingested item carries workspace provenance; toggles ledger to L2; ingest
provenance ledgers to L3. No language model in this path.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402
from jsonschema import Draft202012Validator  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "connectors.json"
SCHEMA_PATH = REPO_ROOT / "config" / "connector-config.schema.json"
CONN_AGENT_ID = "teamos-connectors/0.1"


def load_config(path=None):
    path = Path(path or CONFIG_PATH)
    config = json.loads(path.read_text())
    Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(config)
    return config


def save_config(config, path=None):
    path = Path(path or CONFIG_PATH)
    Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(config)
    path.write_text(json.dumps(config, indent=2) + "\n")


def _source(config, source_id):
    for s in config["sources"]:
        if s["source_id"] == source_id:
            return s
    return None


def eligibility(config, source_id):
    """Return (eligible, rule_id). Pure policy evaluation, no side effects."""
    source = _source(config, source_id)
    if source is None:
        return False, "unknown-source"
    allowlist = config.get("allowlist", [])
    if allowlist and source_id not in allowlist and source["workspace"] not in allowlist:
        return False, "allowlist-block"
    if not source.get("enabled", False):
        return False, "off-by-default"
    return True, "eligible"


def _policy_version(config):
    return hashchain.sha256_str(hashchain.canonical(config))


def toggle(source_id, enabled, config=None, config_path=None, ledger_dir=None,
           field="enabled"):
    """Flip a source's opt-in (or dm_email) toggle. Persist + ledger to L2."""
    ledger_dir = Path(ledger_dir or REPO_ROOT / "ledgers")
    config = config or load_config(config_path)
    source = _source(config, source_id)
    if source is None:
        raise ValueError(f"policy-neutral: cannot toggle unconfigured source {source_id!r}")
    source[field] = bool(enabled)
    save_config(config, config_path)
    hashchain.append(ledger_dir / "l2.jsonl", {
        "proposed_action": {
            "tool": "connector_toggle",
            "action_class": "config",
            "target": f"{source_id}.{field}={enabled}",
            "payload_digest": hashchain.sha256_str(f"{source_id}:{field}:{enabled}"),
        },
        "verdict": "permit",
        "policy_version": _policy_version(config),
        "rule_id": "source-toggle",
        "inspection": {"checks_run": ["config-schema-validate"], "findings": []},
        "outcome": "gate_passed",
    }, CONN_AGENT_ID)
    return config


def ingest(source_id, items, config=None, config_path=None, ledger_dir=None):
    """Return items tagged with provenance IF the source is eligible, else [].

    Ineligible sources provably return nothing (F-test). Eligible ingestion
    stamps every item with {source_id, type, workspace} and ledgers L3
    provenance.
    """
    ledger_dir = Path(ledger_dir or REPO_ROOT / "ledgers")
    config = config or load_config(config_path)
    eligible, rule_id = eligibility(config, source_id)
    if not eligible:
        return []
    source = _source(config, source_id)
    provenance = {
        "source_id": source_id,
        "type": source["type"],
        "workspace": source["workspace"],
    }
    tagged = []
    for i, item in enumerate(items):
        stamped = dict(item)
        stamped["provenance"] = provenance
        tagged.append(stamped)
        hashchain.append(ledger_dir / "l3.jsonl", {
            "target_id": f"{source_id}#ingest-{i}",
            "source_type": f"connector:{source['type']}",
            "authoring_agent": CONN_AGENT_ID,
            "evidence": [{
                "store": source["type"],
                "path": source["workspace"],
                "content_hash": hashchain.sha256_str(hashchain.canonical(item)),
            }],
            "transformation": "connector-ingest",
            "confidence": "high",
            "update_history_ref": {"store": source["type"], "path": source["workspace"],
                                   "content_hash": hashchain.sha256_str(hashchain.canonical(item))},
            "parent_ids": [],
        }, CONN_AGENT_ID)
    return tagged


def notification_channel(config=None, config_path=None):
    """Return the first enabled notification channel, or None (FK5 uses this)."""
    config = config or load_config(config_path)
    for ch in config["notification_channels"]:
        if ch.get("enabled"):
            return ch
    return None
