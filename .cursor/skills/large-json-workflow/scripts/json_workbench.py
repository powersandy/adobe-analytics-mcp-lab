#!/usr/bin/env python3
"""Inspect, extract, and diff large JSON documents."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

COMMON_NOISE_KEYS = {
    "id",
    "_id",
    "guid",
    "uuid",
    "modified",
    "modifiedAt",
    "modifiedDate",
    "updated",
    "updatedAt",
    "updatedDate",
    "createdAt",
    "createdDate",
    "lastModified",
    "lastModifiedDate",
    "timestamp",
    "generatedAt",
}

CJA_PROJECT_NOISE_PATHS = {
    "expansions",
    "projectId",
    "projectBody.name",
    "projectBody.description",
}


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_path_tokens(path: str) -> list[Any]:
    if not path:
        return []

    tokens: list[Any] = []
    buffer = ""
    i = 0
    while i < len(path):
        char = path[i]
        if char == ".":
            if buffer:
                tokens.append(buffer)
                buffer = ""
            i += 1
            continue
        if char == "[":
            if buffer:
                tokens.append(buffer)
                buffer = ""
            end = path.find("]", i)
            if end == -1:
                raise ValueError(f"Unclosed '[' in path: {path}")
            index_text = path[i + 1 : end].strip()
            if not index_text.isdigit():
                raise ValueError(f"Invalid array index '{index_text}' in path: {path}")
            tokens.append(int(index_text))
            i = end + 1
            continue
        buffer += char
        i += 1

    if buffer:
        tokens.append(buffer)
    return tokens


def resolve_path(data: Any, path: str) -> Any:
    current = data
    for token in parse_path_tokens(path):
        if isinstance(token, int):
            if not isinstance(current, list):
                raise KeyError(f"Expected list before index [{token}]")
            current = current[token]
            continue
        if not isinstance(current, dict):
            raise KeyError(f"Expected object before key '{token}'")
        current = current[token]
    return current


def type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def make_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: make_json_safe(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [make_json_safe(item) for item in value]
    return value


def strip_ignored_values(
    value: Any,
    current_path: str,
    ignored_keys: set[str],
    ignored_paths: set[str],
) -> Any:
    normalized_path = current_path or "$"
    if normalized_path in ignored_paths:
        return "__IGNORED_PATH__"

    if isinstance(value, dict):
        cleaned = {}
        for key, child in value.items():
            child_path = f"{current_path}.{key}" if current_path else key
            if key in ignored_keys or child_path in ignored_paths:
                continue
            cleaned[key] = strip_ignored_values(child, child_path, ignored_keys, ignored_paths)
        return cleaned

    if isinstance(value, list):
        cleaned_items = []
        for index, item in enumerate(value):
            child_path = f"{current_path}[{index}]" if current_path else f"[{index}]"
            if child_path in ignored_paths:
                continue
            cleaned_items.append(strip_ignored_values(item, child_path, ignored_keys, ignored_paths))
        return cleaned_items

    return value


def preview_scalar(value: Any, max_length: int = 80) -> str:
    text = json.dumps(value, ensure_ascii=True)
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def infer_scalar_category(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    if re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", value):
        return "uuid"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}([T ][0-9:.+-Z]+)?", value):
        return "datetime_like"
    return None


def path_matches_prefix(path: str, prefixes: list[str]) -> bool:
    if not prefixes:
        return True
    normalized = path or "$"
    for prefix in prefixes:
        if normalized == prefix or normalized.startswith(prefix + ".") or normalized.startswith(prefix + "["):
            return True
    return False


def summarize_paths(changes: list[dict[str, Any]], limit: int) -> dict[str, list[str]]:
    by_type: dict[str, list[str]] = {}
    for change in changes:
        by_type.setdefault(change["change"], [])
        if len(by_type[change["change"]]) < limit:
            by_type[change["change"]].append(change["path"])
    return dict(sorted(by_type.items()))


def build_summary(node: Any, depth: int, max_depth: int, max_children: int) -> dict[str, Any]:
    summary: dict[str, Any] = {"type": type_name(node)}
    if isinstance(node, dict):
        keys = list(node.keys())
        summary["key_count"] = len(keys)
        summary["keys_preview"] = keys[:max_children]
        if depth < max_depth:
            children = {}
            for key in keys[:max_children]:
                children[key] = build_summary(node[key], depth + 1, max_depth, max_children)
            summary["children"] = children
        return summary
    if isinstance(node, list):
        summary["length"] = len(node)
        element_types = Counter(type_name(item) for item in node)
        summary["element_types"] = dict(sorted(element_types.items()))
        if depth < max_depth:
            summary["items_preview"] = [
                build_summary(item, depth + 1, max_depth, max_children)
                for item in node[:max_children]
            ]
        return summary
    summary["value_preview"] = preview_scalar(node)
    return summary


def normalize_for_compare(value: Any, ignore_array_order: bool) -> Any:
    if isinstance(value, dict):
        return {key: normalize_for_compare(value[key], ignore_array_order) for key in sorted(value)}
    if isinstance(value, list):
        items = [normalize_for_compare(item, ignore_array_order) for item in value]
        if ignore_array_order:
            return sorted(items, key=lambda item: json.dumps(item, sort_keys=True, ensure_ascii=True))
        return items
    return value


def diff_values(
    left: Any,
    right: Any,
    path: str,
    results: list[dict[str, Any]],
    ignore_array_order: bool,
    limit: int,
) -> None:
    if len(results) >= limit:
        return

    left_norm = normalize_for_compare(left, ignore_array_order)
    right_norm = normalize_for_compare(right, ignore_array_order)

    if type_name(left_norm) != type_name(right_norm):
        results.append(
            {
                "path": path or "$",
                "change": "type_changed",
                "before_type": type_name(left_norm),
                "after_type": type_name(right_norm),
            }
        )
        return

    if isinstance(left_norm, dict) and isinstance(right_norm, dict):
        all_keys = sorted(set(left_norm) | set(right_norm))
        for key in all_keys:
            if len(results) >= limit:
                return
            next_path = f"{path}.{key}" if path else key
            if key not in left_norm:
                results.append({"path": next_path, "change": "added", "after": right_norm[key]})
                continue
            if key not in right_norm:
                results.append({"path": next_path, "change": "removed", "before": left_norm[key]})
                continue
            diff_values(left_norm[key], right_norm[key], next_path, results, ignore_array_order, limit)
        return

    if isinstance(left_norm, list) and isinstance(right_norm, list):
        if len(left_norm) != len(right_norm):
            results.append(
                {
                    "path": path or "$",
                    "change": "array_length_changed",
                    "before_length": len(left_norm),
                    "after_length": len(right_norm),
                }
            )
        for index, (left_item, right_item) in enumerate(zip(left_norm, right_norm)):
            if len(results) >= limit:
                return
            next_path = f"{path}[{index}]" if path else f"[{index}]"
            diff_values(left_item, right_item, next_path, results, ignore_array_order, limit)
        if len(left_norm) == len(right_norm) and left_norm == right_norm:
            return
        return

    if left_norm != right_norm:
        results.append(
            {
                "path": path or "$",
                "change": "value_changed",
                "before": left_norm,
                "after": right_norm,
            }
        )


def command_summary(args: argparse.Namespace) -> None:
    data = load_json(args.file)
    target = resolve_path(data, args.path) if args.path else data
    output = {
        "file": args.file,
        "path": args.path or "$",
        "summary": build_summary(target, depth=0, max_depth=args.max_depth, max_children=args.max_children),
    }
    print(json.dumps(make_json_safe(output), indent=2, ensure_ascii=True))


def command_extract(args: argparse.Namespace) -> None:
    data = load_json(args.file)
    target = resolve_path(data, args.path) if args.path else data
    print(json.dumps(make_json_safe(target), indent=args.indent, ensure_ascii=True))


def command_diff(args: argparse.Namespace) -> None:
    left = load_json(args.file_a)
    right = load_json(args.file_b)
    left_target = resolve_path(left, args.path_a) if args.path_a else left
    right_target = resolve_path(right, args.path_b) if args.path_b else right

    ignored_keys = set(args.ignore_key or [])
    ignored_paths = set(args.ignore_path or [])
    if args.ignore_common_noise:
        ignored_keys.update(COMMON_NOISE_KEYS)
    if args.cja_project_noise:
        ignored_keys.update(COMMON_NOISE_KEYS)
        ignored_paths.update(CJA_PROJECT_NOISE_PATHS)

    left_target = strip_ignored_values(left_target, "", ignored_keys, ignored_paths)
    right_target = strip_ignored_values(right_target, "", ignored_keys, ignored_paths)

    changes: list[dict[str, Any]] = []
    diff_values(
        left_target,
        right_target,
        path="",
        results=changes,
        ignore_array_order=args.ignore_array_order,
        limit=args.max_diffs,
    )

    if args.focus_path_prefix:
        changes = [change for change in changes if path_matches_prefix(change["path"], args.focus_path_prefix)]

    counts = Counter(change["change"] for change in changes)
    output = {
        "file_a": args.file_a,
        "file_b": args.file_b,
        "path_a": args.path_a or "$",
        "path_b": args.path_b or "$",
        "ignore_array_order": args.ignore_array_order,
        "ignore_common_noise": args.ignore_common_noise,
        "cja_project_noise": args.cja_project_noise,
        "ignored_keys": sorted(ignored_keys),
        "ignored_paths": sorted(ignored_paths),
        "focus_path_prefixes": sorted(args.focus_path_prefix or []),
        "change_count": len(changes),
        "change_counts": dict(sorted(counts.items())),
        "changes": changes,
    }

    if args.classify_noise:
        for change in output["changes"]:
            category = None
            if change["change"] == "value_changed":
                category = infer_scalar_category(change.get("before")) or infer_scalar_category(change.get("after"))
            if category:
                change["value_category"] = category

    if args.summary_only:
        output["sample_paths"] = summarize_paths(output["changes"], args.summary_path_limit)
        del output["changes"]

    print(json.dumps(make_json_safe(output), indent=2, ensure_ascii=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect and compare large JSON files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary = subparsers.add_parser("summary", help="Summarize JSON shape.")
    summary.add_argument("file", help="Path to the JSON file.")
    summary.add_argument("--path", help="Optional subtree path.")
    summary.add_argument("--max-depth", type=int, default=3, help="Maximum summary depth.")
    summary.add_argument("--max-children", type=int, default=8, help="Maximum children to preview per node.")
    summary.set_defaults(func=command_summary)

    extract = subparsers.add_parser("extract", help="Extract a JSON subtree.")
    extract.add_argument("file", help="Path to the JSON file.")
    extract.add_argument("--path", help="Optional subtree path.")
    extract.add_argument("--indent", type=int, default=2, help="Indent size for output.")
    extract.set_defaults(func=command_extract)

    diff = subparsers.add_parser("diff", help="Compare two JSON files or subtrees.")
    diff.add_argument("file_a", help="Left-hand JSON file.")
    diff.add_argument("file_b", help="Right-hand JSON file.")
    diff.add_argument("--path-a", help="Optional subtree path in file A.")
    diff.add_argument("--path-b", help="Optional subtree path in file B.")
    diff.add_argument("--ignore-array-order", action="store_true", help="Normalize arrays before comparison.")
    diff.add_argument(
        "--ignore-common-noise",
        action="store_true",
        help="Ignore common volatile metadata keys like id and updatedAt.",
    )
    diff.add_argument(
        "--cja-project-noise",
        action="store_true",
        help="Apply a CJA project preset: common ID noise plus wrapper-only project metadata.",
    )
    diff.add_argument(
        "--ignore-key",
        action="append",
        help="Ignore any object field with this exact key. Repeatable.",
    )
    diff.add_argument(
        "--ignore-path",
        action="append",
        help="Ignore one exact dotted/indexed path. Repeatable.",
    )
    diff.add_argument(
        "--classify-noise",
        action="store_true",
        help="Label changed scalar values that look like UUIDs or datetime strings.",
    )
    diff.add_argument(
        "--focus-path-prefix",
        action="append",
        help="Keep only changes under this path prefix. Repeatable.",
    )
    diff.add_argument(
        "--summary-only",
        action="store_true",
        help="Return counts and sample changed paths without full change payloads.",
    )
    diff.add_argument(
        "--summary-path-limit",
        type=int,
        default=10,
        help="Maximum sample paths per change type when using --summary-only.",
    )
    diff.add_argument("--max-diffs", type=int, default=200, help="Maximum number of changes to record.")
    diff.set_defaults(func=command_diff)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
