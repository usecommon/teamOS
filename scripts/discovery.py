"""Discovery sub-agent + scout (FK8) — low volume, post-gates only. Idle-time
miners surface patterns and emit them as PROPOSALS into the inbox (never direct
writes; the gate processor commits). Bounded to <=2 proposals per run.

Guards:
- texture guard (§8.4): automate TOIL, never TEXTURE — creative/judgment work is
  excluded, only repetitive toil is proposed.
- proposals go through the same door -> inbox -> gate processor path as any other
  write (gated files).
- A-D3-lite: acceptance rate is computed only after >=9 proposals; below that
  floor it is inconclusive (directional), never reported as a rate.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import door  # noqa: E402

MAX_PROPOSALS_PER_RUN = 2   # low volume (<=2/week cadence, one run/day tolerant)
ACCEPTANCE_FLOOR = 9        # compute the rate only after >=9 proposals
# leading determiners stripped so a sentence-initial "The Cache Layer" and a
# mid-sentence "the Cache Layer" resolve to one entity (entity resolution, §3.3.6)
_LEAD_STOPWORDS = {"The", "A", "An", "This", "That", "Our", "Their", "These",
                   "Those", "Its"}


def _canonical_entity(ent):
    words = ent.split()
    if words and words[0] in _LEAD_STOPWORDS:
        words = words[1:]
    return " ".join(words) if len(words) >= 2 else None


def corpus_scout(items, min_docs=2):
    """Unlinked-reference detection (the scout's cheapest trick, §3.3.3):
    multi-word proper entities appearing across >= min_docs with no linking
    entry -> candidate observations."""
    entity_docs = {}
    for it in items:
        raw = set(re.findall(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)+)\b", it["content"]))
        for ent in {c for c in (_canonical_entity(e) for e in raw) if c}:
            entity_docs.setdefault(ent, set()).add(it["path"])
    obs = []
    for ent, docs in sorted(entity_docs.items()):
        if len(docs) >= min_docs:
            obs.append({"pattern_id": f"entity:{ent}", "kind": "corpus_entry",
                        "toil": True, "title": ent, "evidence": sorted(docs)})
    return obs


def mine(observations, inbox_dir, seen=None, max_proposals=MAX_PROPOSALS_PER_RUN):
    """Emit <= max_proposals inbox proposals from observations, skipping texture
    and already-seen patterns. Returns the list of emitted pattern_ids."""
    seen = set(seen or [])
    emitted = []
    for obs in observations:
        if len(emitted) >= max_proposals:
            break                                   # rate limit
        if not obs.get("toil", True):
            continue                                # texture guard
        if obs["pattern_id"] in seen:
            continue
        door.propose_corpus_entry(
            inbox_dir, obs["title"],
            [f"scout: recurring pattern across {len(obs['evidence'])} sources"],
            source="scout", confidence="low")
        emitted.append(obs["pattern_id"])
        seen.add(obs["pattern_id"])
    return emitted


def acceptance_rate(n_proposals, n_accepted, floor=ACCEPTANCE_FLOOR):
    """A-D3-lite: below the floor => inconclusive; at/above => measured rate,
    meets_floor if >= 1-in-3."""
    if n_proposals < floor:
        return {"result": "inconclusive", "n": n_proposals}
    rate = n_accepted / n_proposals
    return {"result": "measured", "rate": round(rate, 3),
            "meets_floor": rate >= 1 / 3}
