#!/usr/bin/env python3
"""Patch CJA Workspace project JSON with targeted, repeatable operations.

This helper is intended for quick iterative fixes to large project definitions
before re-upserting them through MCP. It works on local JSON files, so the
typical flow is:

1. Save a projectBody or describeProject definition payload locally.
2. Write a small operations JSON file.
3. Run this script to apply the patch.
4. Upsert the patched project body back through MCP.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


Json = dict[str, Any] | list[Any] | str | int | float | bool | None


def load_json(path: Path) -> Json:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Json) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def walk(node: Json):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for item in node:
            yield from walk(item)


def parse_path(path: str) -> list[str]:
    return [part for part in path.split(".") if part]


def set_path(target: Json, path: str, value: Any) -> int:
    parts = parse_path(path)
    if not parts:
        raise ValueError("set_value path cannot be empty")
    return _set_path_recursive(target, parts, value)


def _set_path_recursive(node: Json, parts: list[str], value: Any) -> int:
    if not parts:
        return 0
    head, *tail = parts
    count = 0

    if isinstance(node, dict):
        if head == "*":
            for child in node.values():
                count += _set_path_recursive(child, tail, value)
            return count
        if head not in node:
            return 0
        if not tail:
            node[head] = deepcopy(value)
            return 1
        return _set_path_recursive(node[head], tail, value)

    if isinstance(node, list):
        if head == "*":
            for child in node:
                count += _set_path_recursive(child, tail, value)
            return count
        if head.isdigit():
            index = int(head)
            if 0 <= index < len(node):
                if not tail:
                    node[index] = deepcopy(value)
                    return 1
                return _set_path_recursive(node[index], tail, value)
        return 0

    return 0


def replace_component_id(target: Json, op: dict[str, Any]) -> int:
    old_id = op["from"]
    new_id = op["to"]
    new_name = op.get("new_name")
    count = 0
    for item in walk(target):
        if not isinstance(item, dict):
            continue
        if item.get("id") != old_id:
            continue
        if item.get("__entity__") is not True:
            continue
        item["id"] = new_id
        meta = item.get("__metaData__")
        if new_name and isinstance(meta, dict):
            meta["name"] = new_name
        count += 1
    return count


def replace_inline_date_range(target: Json, op: dict[str, Any]) -> int:
    definition = op["definition"]
    target_panel_ids = set(op.get("panel_ids", []))
    target_panel_names = set(op.get("panel_names", []))
    count = 0

    panels = []
    for item in walk(target):
        if isinstance(item, dict) and item.get("type") == "panel":
            panels.append(item)

    for panel in panels:
        panel_id = panel.get("id")
        panel_name = panel.get("name")
        if target_panel_ids and panel_id not in target_panel_ids:
            continue
        if target_panel_names and panel_name not in target_panel_names:
            continue
        panel["dateRange"] = {
            "__entity__": True,
            "type": "DateRange",
            "__metaData__": {
                "definition": definition,
            },
        }
        count += 1
    return count


def rename_panel(target: Json, op: dict[str, Any]) -> int:
    count = 0
    old_name = op.get("from")
    panel_id = op.get("panel_id")
    new_name = op["to"]
    for item in walk(target):
        if not isinstance(item, dict):
            continue
        if item.get("type") != "panel":
            continue
        if old_name is not None and item.get("name") != old_name:
            continue
        if panel_id is not None and item.get("id") != panel_id:
            continue
        item["name"] = new_name
        count += 1
    return count


def apply_operations(target: Json, operations: list[dict[str, Any]]) -> list[str]:
    summaries: list[str] = []
    for index, op in enumerate(operations, start=1):
        op_type = op["type"]
        if op_type == "replace_component_id":
            count = replace_component_id(target, op)
        elif op_type == "replace_inline_date_range":
            count = replace_inline_date_range(target, op)
        elif op_type == "set_value":
            count = set_path(target, op["path"], op["value"])
        elif op_type == "rename_panel":
            count = rename_panel(target, op)
        else:
            raise ValueError(f"Unsupported operation type: {op_type}")
        summaries.append(f"{index}. {op_type}: {count} change(s)")
    return summaries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Patch a local CJA project JSON file with repeatable operations."
    )
    parser.add_argument("--input", required=True, help="Path to source project JSON")
    parser.add_argument("--ops", required=True, help="Path to operations JSON")
    parser.add_argument("--output", required=True, help="Path to patched project JSON")
    parser.add_argument(
        "--root-key",
        choices=["projectBody", "definition", "auto"],
        default="auto",
        help=(
            "Patch only a nested root. 'projectBody' patches input['projectBody']; "
            "'definition' patches input['definition']; 'auto' uses input['projectBody'] "
            "when present, otherwise patches the whole JSON object."
        ),
    )
    return parser


def resolve_root(document: Json, root_key: str) -> Json:
    if not isinstance(document, dict):
        raise ValueError("Input JSON must be an object")
    if root_key == "projectBody":
        return document["projectBody"]
    if root_key == "definition":
        return document["definition"]
    if "projectBody" in document:
        return document["projectBody"]
    return document


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    ops_path = Path(args.ops)
    output_path = Path(args.output)

    document = load_json(input_path)
    operations_doc = load_json(ops_path)
    if not isinstance(operations_doc, dict) or not isinstance(operations_doc.get("operations"), list):
        raise ValueError("Operations JSON must be an object with an 'operations' array")

    root = resolve_root(document, args.root_key)
    summaries = apply_operations(root, operations_doc["operations"])
    save_json(output_path, document)

    print(f"Wrote patched JSON to {output_path}")
    for summary in summaries:
        print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
