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


# ---- REALISTIC footprint (the fidelity fix, per the 2026-07-20 audit) --------
# De-labeled (no deliverable_type frontmatter), opaque varied filenames (type NOT
# in the stem), noised/irregular cadence, and junk at a realistic ratio. This is
# what a real footprint looks like — and it deliberately denies the deterministic
# compiler the clean signals (labels, type-in-filename, regular dated stems) that
# the clean generator hands it. Expect compile to struggle: that IS the finding.

def _hex(*parts, n=6):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:n]

# realistic content per type — the type is INFERABLE from phrasing, never labeled
_CONTENT = {
    "standup": ["Yesterday: closed the {o}. Today: pick up the {o2}. Blockers: none.",
                "Y'day wrapped {o}. Today {o2}. No blockers, will sync w/ team."],
    "pr-summary": ["Merged the {o} change. Reviewed by a teammate, CI green, deploying today.",
                   "PR for {o} is in — squashed 3 commits, tests pass."],
    "release-notes": ["This release: {o} landed, {o2} fixed. Upgrade notes in the doc.",
                      "Shipping {o}. Breaking: none. Highlights: {o2}."],
    "status-update": ["This week: progressed {o}; {o2} at risk, need a decision.",
                      "Update: {o} on track, {o2} slipping to next sprint."],
    "meeting-summary": ["Discussed {o}. Decision: proceed. Owner: me. Follow-up: {o2}.",
                        "Sync notes: {o} agreed, {o2} parked."],
    "stakeholder-update": ["For leadership: {o} shipped, {o2} in progress, no red flags.",
                           "Exec summary: {o} done; watching {o2}."],
    "incident-note": ["SEV2 on the {o}. Impact ~12m. Mitigated by rollback; RCA to follow.",
                      "Page: {o} degraded. Contained, monitoring {o2}."],
    "oncall-handoff": ["Handoff: {o} noisy overnight, {o2} stable. Nothing open.",
                       "Passing on-call: watch the {o}, {o2} resolved."],
    "postmortem": ["RCA for the {o} outage: cause was {o2}. Action items filed.",
                   "Postmortem: {o} failed under load; adding backpressure."],
    "experiment-log": ["Ran the {o} sweep. {o2} looks promising, rerunning to confirm.",
                       "Log: {o} experiment, mixed results on {o2}."],
    "lit-review": ["Read three papers on {o}. Relevant to {o2}; notes attached.",
                   "Survey of {o}: consensus is unclear, {o2} worth trying."],
    "weekly-digest": ["This week across the repo: {o} merged, {o2} discussed.",
                      "Digest: activity centered on {o} and {o2}."],
    "investor-update": ["MRR up, {o} shipped, hiring for {o2}. Ask: intros.",
                        "Monthly: {o} traction, {o2} is the focus."],
    "hiring-note": ["Interviewed for {o}. Strong on {o2}; moving to onsite.",
                    "Candidate for the {o} role — good {o2}, some gaps."],
    "strategy-memo": ["Proposal: lean into {o}, deprioritize {o2}. Rationale inside.",
                      "Memo: our edge is {o}; {o2} is a distraction."],
}
_OBJ = ["cache layer", "auth flow", "ingest job", "billing bug", "dashboard", "retry logic",
        "schema migration", "rate limiter", "search index", "webhook"]
_JUNK = [
    ("reply", ["Thanks!", "+1", "Sounds good, will do.", "lgtm", "ok ship it"]),
    ("notify", ["[GitHub] pushed 2 commits to main", "Calendar: standup at 9:00",
                "[CI] build #4821 passed", "You were mentioned in a thread"]),
    ("offtopic", ["Anyone up for lunch at 12?", "Who has the wifi password?",
                  "Reminder: office closed Monday", "Coffee machine is broken again"]),
    ("newsletter", ["This week in tech: three things you missed…",
                    "Weekly roundup: funding, launches, and drama"]),
]


def _fname(seed, persona_id, i, iso):
    """Opaque, varied filename — type NEVER in the stem, date only sometimes."""
    style = int(rnd(seed, persona_id, i, "fname") * 6)
    hx = _hex(seed, persona_id, i)
    slug = _OBJ[int(rnd(seed, persona_id, i, "slug") * len(_OBJ))].split()[0]
    return [f"msg-{hx}.md", f"{iso}-{hx[:4]}.md", f"thread-{hx}.md",
            f"Re-{slug}.md", f"note-{iso}.md", f"export-{i}.md"][style]


def generate_realistic_footprint(persona_id, out_dir, weeks=6, junk_ratio=4, seed="synthetic"):
    """Realistic footprint: de-labeled, opaque names, noised cadence, + junk.
    Returns the list of paths. NO deliverable_type frontmatter anywhere."""
    if persona_id not in PERSONAS:
        raise KeyError(f"unknown persona '{persona_id}' (have: {', '.join(PERSONAS)})")
    p = PERSONAS[persona_id]
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    written = []
    span = weeks * 7
    idx = 0
    for d in p["deliverables"]:
        day = 0
        while day < span:
            r = rnd(seed, persona_id, d["type"], idx)
            if r < 0.2:                          # ~20% missed occurrences (skips)
                day += d["cadence_days"]; idx += 1; continue
            n_here = 3 if r > 0.93 else 1        # occasional burst (multiple same day)
            for k in range(n_here):
                jit = int(rnd(seed, idx, k, "jit") * 5) - 2      # ±2 day jitter
                dt = BASE_DATE + timedelta(days=max(0, min(span - 1, day + jit)))
                tmpl = _CONTENT.get(d["type"], ["Notes on {o}."])
                body = tmpl[int(rnd(seed, idx, k) * len(tmpl))]
                o = _OBJ[int(rnd(seed, idx, k, "o") * len(_OBJ))]
                o2 = _OBJ[int(rnd(seed, idx, k, "o2") * len(_OBJ))]
                fn = _fname(seed, persona_id, idx * 10 + k, dt.isoformat())
                (out / fn).write_text(body.format(o=o, o2=o2) + "\n")   # NO frontmatter
                written.append(out / fn)
            day += d["cadence_days"]; idx += 1
    # junk at junk_ratio × the deliverable volume
    n_junk = int(len(written) * junk_ratio)
    for j in range(n_junk):
        kind, msgs = _JUNK[int(rnd(seed, persona_id, j, "jk") * len(_JUNK))]
        dt = BASE_DATE + timedelta(days=int(rnd(seed, persona_id, j, "jd") * span))
        fn = _fname(seed, persona_id, 100000 + j, dt.isoformat())
        (out / fn).write_text(msgs[int(rnd(seed, persona_id, j) * len(msgs))] + "\n")
        written.append(out / fn)
    return written


def decision(persona_id, turn, seed="synthetic"):
    """UNREALISTIC baseline (2/10, per the 07-20 audit): a coin flip DECOUPLED
    from draft quality. Kept for the A-A4 experiment as the null model — it
    correctly yields NO proxy<->use correlation. Use realistic_decision instead."""
    p = PERSONAS.get(persona_id) or {"accept": 0.6, "edit_style": "mixed"}
    roll = rnd(seed, persona_id, turn, "decide")
    if roll < p["accept"]:
        lo, hi = EDIT_DISTANCE[p["edit_style"]]
        dist = round(lo + rnd(seed, persona_id, turn, "dist") * (hi - lo), 4)
        return {"action": "accept", "edit_distance": dist}
    if roll < p["accept"] + 0.22:
        return {"action": "reject", "edit_distance": None}
    return {"action": "ignore", "edit_distance": None}


# ---- REALISTIC behavior model (the fidelity fix for A-A4) --------------------
# Real acceptance is COUPLED to draft quality and NON-STATIONARY (trust ramps
# with success, drops on rejection). And A-A4's headline needs a downstream-USE
# signal (ME-1) that is separate from the acceptance proxy. All three modeled
# here so A-A4 (does the proxy correlate with real use?) is actually testable.

def draft_quality(persona_id, turn, seed="synthetic"):
    """Latent ground-truth quality [0,1] of the agent's draft this turn — with
    real variance and a trust-ramp trend (the agent improves over ~40 turns)."""
    ramp = 0.35 + 0.40 * min(1.0, turn / 40.0)
    noise = (rnd(seed, persona_id, turn, "q") - 0.5) * 0.5
    return max(0.0, min(1.0, ramp + noise))


def downstream_use(quality, persona_id, turn, seed="synthetic"):
    """ME-1 primary behavior: was the deliverable actually USED (forwarded /
    clicked / referenced later)? Quality-coupled + independent noise — the
    SECOND series A-A4 correlates the acceptance proxy against."""
    return 1 if rnd(seed, persona_id, turn, "use") < (0.1 + 0.8 * quality) else 0


def realistic_decision(persona_id, turn, quality, trust=0.5, seed="synthetic"):
    """Accept/reject/ignore COUPLED to draft quality and modulated by trust.
    Edit distance is content-tied (worse draft -> bigger edit). Returns the same
    shape as decision() plus the latent quality."""
    p_acc = min(0.98, max(0.02, 0.15 + 0.65 * quality + 0.20 * (trust - 0.5)))
    roll = rnd(seed, persona_id, turn, "racc")
    if roll < p_acc:
        dist = round(max(0.0, (1.0 - quality) * 0.4) * rnd(seed, persona_id, turn, "rd"), 4)
        return {"action": "accept", "edit_distance": dist, "quality": quality}
    if rnd(seed, persona_id, turn, "rrej") < 0.5:
        return {"action": "reject", "edit_distance": None, "quality": quality}
    return {"action": "ignore", "edit_distance": None, "quality": quality}


def update_trust(trust, action):
    """Non-stationary trust: earned slowly on acceptance, dropped fast on
    rejection (OB-1 asymmetry) — so the envelope tracks a MOVING level."""
    if action == "accept":
        return min(1.0, trust + 0.03)
    if action == "reject":
        return max(0.0, trust - 0.08)
    return trust
