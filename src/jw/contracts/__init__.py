"""JSON Schema subset validator for the schemas shipped with this package.

Not a general-purpose JSON Schema implementation. Unknown keywords fail closed.
"""
import json
import math
from pathlib import Path


def schema(name):
    if name not in ("edit", "report"):
        raise ValueError("Unknown contract")
    return json.loads(Path(__file__).with_name(name + ".schema.json").read_text(encoding="utf-8"))


def validate(value, contract):
    supported = {"$schema", "title", "type", "additionalProperties", "required", "properties", "items", "maxItems", "maxLength", "minimum", "maximum", "const", "enum"}
    if set(contract) - supported:
        raise ValueError("Unsupported schema keyword")
    types = {"object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, (list, tuple)),
             "string": lambda x: isinstance(x, str), "integer": lambda x: type(x) is int,
             "number": lambda x: type(x) in (int, float) and math.isfinite(x), "boolean": lambda x: type(x) is bool}
    kind = contract.get("type")
    if kind and not any(types[t](value) for t in ([kind] if isinstance(kind, str) else kind)):
        raise ValueError("Contract type mismatch")
    if "const" in contract and (type(value) is not type(contract["const"]) or value != contract["const"]):
        raise ValueError("Contract constant mismatch")
    if "enum" in contract and value not in contract["enum"]:
        raise ValueError("Contract enum mismatch")
    for key, failed in (("minimum", lambda: value < contract[key]), ("maximum", lambda: value > contract[key]),
                        ("maxItems", lambda: len(value) > contract[key]), ("maxLength", lambda: len(value) > contract[key])):
        if key in contract and failed():
            raise ValueError("Contract bound violated")
    if isinstance(value, dict):
        if set(contract.get("required", ())) - value.keys():
            raise ValueError("Required contract field missing")
        properties = contract.get("properties", {})
        extra = contract.get("additionalProperties", True)
        for key, item in value.items():
            if key in properties:
                validate(item, properties[key])
            elif extra is False:
                raise ValueError("Unexpected contract field")
            elif isinstance(extra, dict):
                validate(item, extra)
    if isinstance(value, (list, tuple)) and "items" in contract:
        for item in value:
            validate(item, contract["items"])
