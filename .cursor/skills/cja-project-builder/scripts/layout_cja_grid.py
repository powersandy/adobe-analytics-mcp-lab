#!/usr/bin/env python3
"""Apply simple grid layouts to subpanels in a local CJA project JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve_project_body(doc: Any) -> dict[str, Any]:
    if isinstance(doc, dict) and "projectBody" in doc:
        return doc["projectBody"]
    if isinstance(doc, dict):
        return doc
    raise ValueError("Input JSON must be an object")


def find_panel(project_body: dict[str, Any], panel_id: str | None, panel_name: str | None) -> dict[str, Any]:
    for workspace in project_body["definition"]["workspaces"]:
        for panel in workspace.get("panels", []):
            if panel_id and panel.get("id") == panel_id:
                return panel
            if panel_name and panel.get("name") == panel_name:
                return panel
    raise ValueError("Panel not found")


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a row or grid layout to subpanels in a panel.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--panel-id")
    parser.add_argument("--panel-name")
    parser.add_argument("--mode", choices=["row", "grid"], default="row")
    parser.add_argument("--columns", type=int, default=2)
    parser.add_argument("--height", type=int, default=358)
    parser.add_argument("--start-y", type=int, default=0)
    args = parser.parse_args()

    doc = load_json(Path(args.input))
    project_body = resolve_project_body(doc)
    panel = find_panel(project_body, args.panel_id, args.panel_name)
    subpanels = panel.get("subPanels", [])
    if not subpanels:
        raise ValueError("Panel has no subpanels")

    columns = len(subpanels) if args.mode == "row" else max(1, args.columns)
    width = int(100 / columns)

    for index, subpanel in enumerate(subpanels):
        row = 0 if args.mode == "row" else index // columns
        col = index if args.mode == "row" else index % columns
        position = {
            "width": width,
            "x": col * width,
            "y": args.start_y + row,
        }
        if args.height is None:
            position["autoSize"] = True
            position.pop("fixedHeight", None)
        else:
            position["autoSize"] = False
            position["fixedHeight"] = args.height
        subpanel["position"] = position

    save_json(Path(args.output), doc)
    print(f"Wrote patched layout to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
