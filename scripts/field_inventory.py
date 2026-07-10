"""FR1 denominator: the field inventory, generated MECHANICALLY from docs/schemas/.

Rule (stated once, applied uniformly): a field is every leaf property path
declared in a schema file's `properties` / `$defs` trees, recursing through
nested objects and array `items`. Fields shared via $ref (the ledger-common
envelope) are counted once, in the file that declares them. The inventory is
never hand-edited — it is regenerated on every run and compared in CI.

Output: JSON list of "file#/path/to/field" strings on stdout.
"""

import json
import sys

from schema_registry import load_schemas


def _walk(node, prefix, out):
    if not isinstance(node, dict):
        return
    props = node.get("properties", {})
    for name, sub in sorted(props.items()):
        path = f"{prefix}/{name}"
        child_props = sub.get("properties")
        items = sub.get("items", {})
        items_props = items.get("properties") if isinstance(items, dict) else None
        if child_props:
            _walk(sub, path, out)
        elif items_props:
            _walk(items, path + "[]", out)
        else:
            out.append(path)


def inventory():
    out = []
    for name, schema in load_schemas().items():
        _walk(schema, f"{name}#", out)
        for def_name, def_schema in sorted(schema.get("$defs", {}).items()):
            _walk(def_schema, f"{name}#$defs/{def_name}", out)
    return sorted(out)


if __name__ == "__main__":
    json.dump(inventory(), sys.stdout, indent=2)
    print()
