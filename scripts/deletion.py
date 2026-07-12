"""Ledger 9 — deletion propagation (FK3 / C6). Unchanged from mainline §5.3.

Erasure = garbage collection over the L3 lineage DAG, deadline-bound (GDPR one
month). Tombstone at the origin; walk L3 derivation edges marking every
descendant. A descendant that is a promoted skill is NOT silently killed — it is
flagged for re-derivation. Content-traceable deletion (a memory quoting the
datum) is distinguished from statistical-influence deletion (a distilled pattern
that no longer contains it — may survive under curator review).

Durability: the request is a file; the walk is idempotent and resumable — a box
offline mid-purge completes on reconnect by re-running.

No language model anywhere here (deterministic, hook-gated code path).
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashchain  # noqa: E402
from fsutil import atomic_write_text  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEL_AGENT_ID = "teamos-deletion/0.1"
GDPR_DAYS = 30
PROMOTED_NAMESPACES = ("team/", "org/", "company/")
# transformation markers meaning "the datum was distilled out" (may survive)
STATISTICAL_MARKERS = ("distill", "compil", "aggregate", "pattern")
# node-id prefixes whose ids ARE store-relative content paths (erasable)
CONTENT_ROOTS = ("stores/", "inbox/", "job-graph/", "deliverables/", "schedules/")


def _now():
    return datetime.now(timezone.utc)


def load_l3_dag(ledger_dir):
    """Return (nodes, children) from l3.jsonl.

    nodes[target_id] = latest L3 record; children[parent_id] = [target_id, ...].
    Edges come from each record's parent_ids (target derived FROM parents).
    """
    path = Path(ledger_dir) / "l3.jsonl"
    nodes, children = {}, {}
    if not path.exists():
        return nodes, children
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        nodes[rec["target_id"]] = rec
        for parent in rec.get("parent_ids", []):
            children.setdefault(parent, []).append(rec["target_id"])
    return nodes, children


def _deletion_kind(record):
    if record is None:
        return "content_traceable"
    transformation = (record.get("transformation") or "").lower()
    if any(m in transformation for m in STATISTICAL_MARKERS):
        return "statistical_influence"
    return "content_traceable"


def _is_promoted_skill(node_id):
    return node_id.startswith(PROMOTED_NAMESPACES)


def _request_path(ledger_dir, request_id):
    d = Path(ledger_dir) / "deletion-requests"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{request_id}.json"


# --- content side-store (the L8 crypto-shred pattern, generalized to L3) ------
# Chains hash REFERENCES, never content. Node content lives in an erasable
# side-store (or as the store file the node id names); erasure unlinks it and
# the chain still verifies.

def l3_sidestore_path(ledger_dir, node_id):
    digest = hashchain.sha256_str(node_id).split(":")[1]
    return Path(ledger_dir) / "sidestore" / "l3" / f"{digest}.content"


def store_l3_content(node_id, content, ledger_dir):
    """Write node content into the redactable L3 side-store; return its ref
    (path + hash) for the chain. The chain must never inline this content."""
    path = l3_sidestore_path(ledger_dir, node_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return {"store": "l3-sidestore",
            "path": str(path.relative_to(Path(ledger_dir))),
            "content_hash": hashchain.sha256_str(content)}


def _shred_node_content(node_id, ledger_dir, store_root):
    """Remove the CONTENT behind a node: its side-store file and, when the
    node id names a store file, that file. Returns the paths removed."""
    removed = []
    side = l3_sidestore_path(ledger_dir, node_id)
    if side.exists():
        side.unlink()
        removed.append(str(side))
    if "/" in node_id and "#" not in node_id \
            and any(node_id.startswith(r) for r in CONTENT_ROOTS):
        target = (Path(store_root) / node_id).resolve()
        root = Path(store_root).resolve()
        if str(target).startswith(str(root) + os.sep) and target.is_file():
            target.unlink()
            removed.append(str(target))
    return removed


def request_erasure(origin_node, request_id, requester_type="principal",
                    ledger_dir=None, deadline=None, resume=True,
                    store_root=None):
    """Tombstone origin_node and propagate over descendants. Idempotent.
    Erasure REMOVES CONTENT (side-store + named store files), not just ledger
    events; the chain hashes references, so it still verifies afterward.

    Returns the request state dict. Re-invoking with the same request_id resumes
    an interrupted purge (durable-tombstone offline completion).
    """
    ledger_dir = Path(ledger_dir or REPO_ROOT / "ledgers")
    store_root = Path(store_root or REPO_ROOT)
    l9 = ledger_dir / "l9.jsonl"
    deadline = deadline or (_now() + timedelta(days=GDPR_DAYS)).isoformat().replace("+00:00", "Z")
    req_path = _request_path(ledger_dir, request_id)

    if resume and req_path.exists():
        state = json.loads(req_path.read_text())
    else:
        state = {
            "request_id": request_id,
            "requester_type": requester_type,
            "origin_node": origin_node,
            "deadline": deadline,
            "processed": [],
            "flagged_skills": [],
            "status": "pending",
        }
        atomic_write_text(req_path, json.dumps(state))
        # tombstone at origin
        hashchain.append(l9, {
            "request_id": request_id, "requester_type": requester_type,
            "event": "tombstone_written", "origin_node": origin_node,
            "affected_node": origin_node, "deletion_kind": "content_traceable",
            "deadline": deadline, "status": "in_progress",
        }, DEL_AGENT_ID)

    nodes, children = load_l3_dag(ledger_dir)
    processed = set(state["processed"])

    # BFS over descendants (origin included so its own node is marked)
    queue, seen = [origin_node], {origin_node}
    while queue:
        current = queue.pop(0)
        for child in children.get(current, []):
            if child not in seen:
                seen.add(child)
                queue.append(child)

    for node_id in seen:
        if node_id in processed:
            continue  # resumed run: already done, skip (idempotent)
        kind = _deletion_kind(nodes.get(node_id))
        if _is_promoted_skill(node_id):
            # derivation severing: flag, never silently kill
            hashchain.append(l9, {
                "request_id": request_id, "requester_type": requester_type,
                "event": "skill_flagged_for_rederivation", "origin_node": origin_node,
                "affected_node": node_id, "deletion_kind": kind,
                "deadline": deadline, "status": "in_progress",
            }, DEL_AGENT_ID)
            state["flagged_skills"].append(node_id)
        else:
            hashchain.append(l9, {
                "request_id": request_id, "requester_type": requester_type,
                "event": "descendant_marked", "origin_node": origin_node,
                "affected_node": node_id, "deletion_kind": kind,
                "deadline": deadline, "status": "in_progress",
            }, DEL_AGENT_ID)
            if kind == "content_traceable":
                # deletion touches CONTENT, not only the ledger (T4)
                for path in _shred_node_content(node_id, ledger_dir, store_root):
                    hashchain.append(l9, {
                        "request_id": request_id,
                        "requester_type": requester_type,
                        "event": "content_shredded", "origin_node": origin_node,
                        "affected_node": path, "deletion_kind": kind,
                        "deadline": deadline, "status": "in_progress",
                    }, DEL_AGENT_ID)
        processed.add(node_id)
        state["processed"] = sorted(processed)
        atomic_write_text(req_path, json.dumps(state))  # durable after every node

    state["status"] = "complete"
    atomic_write_text(req_path, json.dumps(state))
    hashchain.append(l9, {
        "request_id": request_id, "requester_type": requester_type,
        "event": "purge_completed", "origin_node": origin_node,
        "affected_node": origin_node, "deletion_kind": "content_traceable",
        "deadline": deadline, "status": "complete",
    }, DEL_AGENT_ID)
    return state


def shred_l8_content(match_substring, request_id, ledger_dir=None,
                     requester_type="third_party_dsar"):
    """Third-party DSAR reaching content inside L8 diffs (SE-2).

    Deletes the referenced side-store diff file(s) whose content matches; writes
    a content_shredded L9 event. The L8 chain hashes REFERENCES, so shredding
    the content does NOT break chain verification for adjacent records.
    """
    ledger_dir = Path(ledger_dir or REPO_ROOT / "ledgers")
    l8 = ledger_dir / "l8.jsonl"
    l9 = ledger_dir / "l9.jsonl"
    deadline = (_now() + timedelta(days=GDPR_DAYS)).isoformat().replace("+00:00", "Z")
    shredded = []
    if not l8.exists():
        return shredded
    for line in l8.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        ref = rec.get("diff_ref")
        if not ref:
            continue
        diff_path = ledger_dir / ref["path"]
        if diff_path.exists() and match_substring in diff_path.read_text():
            diff_path.unlink()  # crypto-shred stand-in: remove referenced content
            shredded.append(str(diff_path))
            hashchain.append(l9, {
                "request_id": request_id, "requester_type": requester_type,
                "event": "content_shredded", "origin_node": rec["record_id"],
                "affected_node": ref["path"], "deletion_kind": "content_traceable",
                "deadline": deadline, "status": "complete",
            }, DEL_AGENT_ID)
    return shredded


def deadline_report(ledger_dir=None, now=None):
    """Report open requests vs their one-month clock."""
    ledger_dir = Path(ledger_dir or REPO_ROOT / "ledgers")
    now = now or _now()
    d = ledger_dir / "deletion-requests"
    rows = []
    if d.exists():
        for f in sorted(d.glob("*.json")):
            state = json.loads(f.read_text())
            dl = datetime.fromisoformat(state["deadline"].replace("Z", "+00:00"))
            overdue = state["status"] != "complete" and now > dl
            rows.append({
                "request_id": state["request_id"],
                "status": "overdue" if overdue else state["status"],
                "deadline": state["deadline"],
                "flagged_skills": state.get("flagged_skills", []),
            })
    return rows


if __name__ == "__main__":
    for row in deadline_report():
        print(json.dumps(row))
