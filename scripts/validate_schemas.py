"""CI check: every file in docs/schemas/ is a valid 2020-12 JSON Schema and all
local $refs resolve. Exit non-zero on any failure."""

import sys

from jsonschema import Draft202012Validator

from schema_registry import load_schemas, validator_for


def main():
    schemas = load_schemas()
    if not schemas:
        print("FAIL: no schemas found in docs/schemas/")
        return 1
    failures = 0
    for name, schema in schemas.items():
        try:
            Draft202012Validator.check_schema(schema)
            # Force $ref resolution by validating a trivially-wrong instance.
            validator = validator_for(name, schemas)
            list(validator.iter_errors({"__probe__": True}))
            print(f"ok: {name}")
        except Exception as exc:  # noqa: BLE001 — report every schema's failure
            failures += 1
            print(f"FAIL: {name}: {exc}")
    print(f"{len(schemas)} schemas checked, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
