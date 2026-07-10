"""Shared loader: docs/schemas/ as a resolvable JSON Schema registry."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "docs" / "schemas"


def load_schemas():
    """Return {filename: schema_dict} for every *.schema.json file."""
    return {
        p.name: json.loads(p.read_text())
        for p in sorted(SCHEMAS_DIR.glob("*.schema.json"))
    }


def build_registry(schemas=None):
    schemas = schemas or load_schemas()
    resources = [
        (schema.get("$id", name), Resource.from_contents(schema))
        for name, schema in schemas.items()
    ]
    return Registry().with_resources(resources)


def validator_for(schema_name, schemas=None):
    schemas = schemas or load_schemas()
    return Draft202012Validator(schemas[schema_name], registry=build_registry(schemas))
