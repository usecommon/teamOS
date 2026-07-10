"""A-FK1 (FR1) gate instrument: joins the mechanical field inventory against
adapter/mapping.yaml and enforces:

  1. completeness — every inventory field annotated exactly once (no field can
     be quietly dropped from the denominator);
  2. percentage — mapped (harness-mapped + fork-native) / total >= 90%;
  3. must-map — every load-bearing field (L3 lineage set, gate-verdict fields,
     skill version/evidence links) is mapped, regardless of the percentage.

Prints the report; exits non-zero on any gate failure. Unmapped fields are
emitted as ready-to-PR divergence-log entries (class: field-miss).
"""

import sys
from pathlib import Path

import yaml

from field_inventory import inventory

REPO_ROOT = Path(__file__).resolve().parent.parent
MAPPING_PATH = REPO_ROOT / "adapter" / "mapping.yaml"
THRESHOLD = 0.90  # arbitrary-pending-baseline, per the validation plan
MAPPED_STATUSES = {"harness-mapped", "fork-native"}


def main():
    mapping = yaml.safe_load(MAPPING_PATH.read_text())
    fields = inventory()
    annotated = {}  # field -> (group_name, status)
    duplicates = []
    for group in mapping["groups"]:
        for field in group["fields"]:
            if field in annotated:
                duplicates.append(field)
            annotated[field] = (group["name"], group["status"])

    missing = [f for f in fields if f not in annotated]
    stale = [f for f in annotated if f not in fields]

    failures = []
    if duplicates:
        failures.append(f"fields annotated more than once: {duplicates}")
    if missing:
        failures.append(f"inventory fields missing from mapping.yaml: {missing}")
    if stale:
        failures.append(f"mapping.yaml annotates fields not in the inventory: {stale}")

    mapped = [f for f in fields if annotated.get(f, ("", ""))[1] in MAPPED_STATUSES]
    unmapped = [f for f in fields if annotated.get(f, ("", ""))[1] == "unmapped"]
    pct = len(mapped) / len(fields) if fields else 0.0

    must_map = mapping.get("must_map", [])
    must_map_misses = [
        f for f in must_map if annotated.get(f, ("", "unmapped"))[1] not in MAPPED_STATUSES
    ]
    unknown_must_map = [f for f in must_map if f not in fields]
    if unknown_must_map:
        failures.append(f"must_map entries not in the inventory: {unknown_must_map}")

    print("# FR1 / A-FK1 mapping report")
    print(f"inventory fields (denominator): {len(fields)}")
    print(f"mapped: {len(mapped)}  (harness-mapped + fork-native)")
    print(f"unmapped (field-miss): {len(unmapped)}")
    print(f"percentage: {pct:.1%}  (gate: >= {THRESHOLD:.0%})")
    print(f"must-map fields: {len(must_map)}, misses: {len(must_map_misses)}")

    if unmapped:
        print("\n## Divergence-log entries (class: field-miss) — propose via PR")
        for f in unmapped:
            group_name, _ = annotated[f]
            src = next(g for g in mapping["groups"] if g["name"] == group_name)
            reason = " ".join(str(src.get("source", "")).split())
            print(f"- **field-miss** `{f}` — {reason}")

    if pct < THRESHOLD:
        failures.append(f"mapping percentage {pct:.1%} below gate {THRESHOLD:.0%}")
    if must_map_misses:
        failures.append(
            f"LOAD-BEARING MISS (gate fails regardless of percentage): {must_map_misses}"
        )

    if failures:
        print("\nGATE: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nGATE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
