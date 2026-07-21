"""Synthetic data + agent/persona types for testing (no collaborators available,
so validation runs on synthetic actors — CLAUDE.md data hygiene: synthetic
fixtures only, never real source data).

DETERMINISTIC by construction: personas, footprints, and behaviors derive from
sha256(seed|parts), never Math.random / time — so a run is reproducible and no
model sits in the data path (SE-1/CN-2). Feeds `teamos synth`, the simulation
harness, and tests.
"""
import hashlib
from datetime import date, timedelta
from pathlib import Path

# ---- deterministic pseudo-randomness (seed + parts -> [0,1)) ----------------

def rnd(*parts):
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return (int(h[:8], 16) % 1_000_000) / 1_000_000.0


# ---- principal persona types (the "agent types" under test) -----------------
# Each is a person with a distinct footprint + acceptance behavior. deliverables
# have a cadence so the compiler (FK4) finds them as recurring tasks.

PERSONAS = {
    "engineer": {
        "role": "Ships code; writes standups, PR summaries, release notes",
        "accept": 0.72, "edit_style": "light",
        "deliverables": [
            {"type": "standup", "source": "slack-eng", "cadence_days": 1},
            {"type": "pr-summary", "source": "git-commits", "cadence_days": 2},
            {"type": "release-notes", "source": "git-tags", "cadence_days": 7},
        ],
    },
    "pm": {
        "role": "Runs delivery; status roundups, stakeholder updates, meeting notes",
        "accept": 0.55, "edit_style": "mixed",
        "deliverables": [
            {"type": "status-update", "source": "task-tracker", "cadence_days": 7},
            {"type": "meeting-summary", "source": "calendar", "cadence_days": 3},
            {"type": "stakeholder-update", "source": "email", "cadence_days": 7},
        ],
    },
    "ops": {
        "role": "On-call lead; incident notes, escalations, handoffs",
        "accept": 0.60, "edit_style": "terse",
        "deliverables": [
            {"type": "incident-note", "source": "pagerduty", "cadence_days": 2},
            {"type": "oncall-handoff", "source": "slack-ops", "cadence_days": 1},
            {"type": "postmortem", "source": "logs", "cadence_days": 7},
        ],
    },
    "researcher": {
        "role": "Runs experiments; lit reviews, experiment logs, weekly digests",
        "accept": 0.65, "edit_style": "light",
        "deliverables": [
            {"type": "experiment-log", "source": "notebook", "cadence_days": 1},
            {"type": "lit-review", "source": "arxiv", "cadence_days": 5},
            {"type": "weekly-digest", "source": "git-commits", "cadence_days": 7},
        ],
    },
    "founder": {
        "role": "Runs the company; investor updates, hiring notes, strategy memos",
        "accept": 0.50, "edit_style": "heavy",
        "deliverables": [
            {"type": "investor-update", "source": "email", "cadence_days": 7},
            {"type": "hiring-note", "source": "ats", "cadence_days": 3},
            {"type": "strategy-memo", "source": "docs", "cadence_days": 7},
        ],
    },
}

# ---- non-principal actor types (for multi-actor scenarios) -------------------

ACTORS = {
    "colleague": {"kind": "principal",
                  "role": "Second person on the shared project — needed for transfer (FK7)"},
    "red-team": {"kind": "adversary",
                 "role": "Low-priv insider: tries exfil, forged acceptance, breaker disarm, "
                         "getting untrusted content to add a step"},
    "manager": {"kind": "other",
                "role": "Deploys the kit; may misuse it"},
    "client": {"kind": "untrusted",
               "role": "External source — supplies content that must never become plan structure (taint)"},
}

EDIT_DISTANCE = {  # (min, max) normalized edit distance an accepting persona applies
    "light": (0.0, 0.08), "mixed": (0.0, 0.3), "terse": (0.0, 0.05), "heavy": (0.1, 0.5),
}

BASE_DATE = date(2026, 6, 1)


def list_personas():
    return {k: v["role"] for k, v in PERSONAS.items()}


def list_actors():
    return {k: v["role"] for k, v in ACTORS.items()}


def generate_footprint(persona_id, out_dir, weeks=6, seed="synthetic"):
    """Write a synthetic footprint for `persona_id` into out_dir: one markdown
    file per deliverable-occurrence, dated across `weeks` at each deliverable's
    cadence so FK4 compiles them as recurring tasks. Returns the list of paths.

    Content is fictional and deterministic. No real names, no secrets."""
    if persona_id not in PERSONAS:
        raise KeyError(f"unknown persona '{persona_id}' (have: {', '.join(PERSONAS)})")
    p = PERSONAS[persona_id]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    span = weeks * 7
    for d in p["deliverables"]:
        occ = 0
        day = 0
        while day < span:
            dt = BASE_DATE + timedelta(days=day)
            r = rnd(seed, persona_id, d["type"], occ)
            fname = f"{d['type']}-{dt.isoformat()}.md"
            body = _body(persona_id, d["type"], occ, r)
            (out / fname).write_text(
                f"---\ndeliverable_type: {d['type']}\nsource: {d['source']}\n---\n{body}\n")
            written.append(out / fname)
            occ += 1
            day += d["cadence_days"]
    return written


def _body(persona_id, dtype, occ, r):
    """Fictional, deterministic one-liner — varied enough to look like real work,
    never real content. Distill-then-discard applies to this too."""
    verbs = ["Shipped", "Reviewed", "Fixed", "Planned", "Escalated", "Drafted"]
    objs = ["the cache layer", "the auth flow", "the ingest job", "the dashboard",
            "the retry logic", "the schema migration"]
    v = verbs[int(r * len(verbs)) % len(verbs)]
    o = objs[int(rnd(persona_id, dtype, occ, "obj") * len(objs)) % len(objs)]
    return f"{v} {o}. Owner: me. Next: follow up on item {occ + 1}."


def decision(persona_id, turn, seed="synthetic"):
    """Deterministic human response for the sim: accept (with an edit distance) /
    reject / ignore. Reproducible per (persona, turn)."""
    p = PERSONAS.get(persona_id) or {"accept": 0.6, "edit_style": "mixed"}
    roll = rnd(seed, persona_id, turn, "decide")
    if roll < p["accept"]:
        lo, hi = EDIT_DISTANCE[p["edit_style"]]
        dist = round(lo + rnd(seed, persona_id, turn, "dist") * (hi - lo), 4)
        return {"action": "accept", "edit_distance": dist}
    if roll < p["accept"] + 0.22:
        return {"action": "reject", "edit_distance": None}
    return {"action": "ignore", "edit_distance": None}
