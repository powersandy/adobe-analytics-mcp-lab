#!/usr/bin/env python3
"""Extract component references from a local CJA project JSON file for MCP revalidation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def walk(node: Any):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for item in node:
            yield from walk(item)


def resolve_project_body(doc: Any) -> dict[str, Any]:
    if isinstance(doc, dict) and "projectBody" in doc:
        return doc["projectBody"]
    if isinstance(doc, dict):
        return doc
    raise ValueError("Input JSON must be an object")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract referenced entities from a local CJA project JSON file.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    project_body = resolve_project_body(load_json(Path(args.input)))
    buckets: dict[str, dict[str, str]] = {
        "Dimension": {},
        "Metric": {},
        "Segment": {},
        "DateRange": {},
        "ReportSuite": {},
    }

    for item in walk(project_body):
        if not isinstance(item, dict):
            continue
        if item.get("__entity__") is not True:
            continue
        entity_type = item.get("type")
        entity_id = item.get("id")
        if entity_type not in buckets or not entity_id:
            continue
        name = ""
        meta = item.get("__metaData__")
        if isinstance(meta, dict):
            name = meta.get("name", "")
        buckets[entity_type][entity_id] = name

    output = {
        "dataId": project_body.get("dataId"),
        "components": {
            key: [{"id": entity_id, "name": name} for entity_id, name in sorted(value.items())]
            for key, value in buckets.items()
        },
    }
    save_json(Path(args.output), output)
    print(f"Wrote component audit to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
