#!/usr/bin/env python3
"""Patch a chart subpanel so it links to a table subpanel."""

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


def find_subpanel(panel: dict[str, Any], subpanel_id: str | None, subpanel_name: str | None) -> dict[str, Any]:
    for subpanel in panel.get("subPanels", []):
        if subpanel_id and subpanel.get("id") == subpanel_id:
            return subpanel
        if subpanel_name and subpanel.get("name") == subpanel_name:
            return subpanel
    raise ValueError("Subpanel not found")


def main() -> int:
    parser = argparse.ArgumentParser(description="Link a chart subpanel to a table subpanel.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--panel-id")
    parser.add_argument("--panel-name")
    parser.add_argument("--table-id")
    parser.add_argument("--table-name")
    parser.add_argument("--chart-id")
    parser.add_argument("--chart-name")
    parser.add_argument("--chart-index", type=int)
    parser.add_argument("--table-index", type=int)
    args = parser.parse_args()

    doc = load_json(Path(args.input))
    project_body = resolve_project_body(doc)
    panel = find_panel(project_body, args.panel_id, args.panel_name)
    table = find_subpanel(panel, args.table_id, args.table_name)
    chart = find_subpanel(panel, args.chart_id, args.chart_name)

    table["linkedSourceId"] = ""
    chart["linkedSourceId"] = table.get("id", "")
    if args.table_index is not None:
        table["visualizationIndex"] = args.table_index
    if args.chart_index is not None:
        chart["visualizationIndex"] = args.chart_index

    save_json(Path(args.output), doc)
    print(f"Linked chart '{chart.get('name')}' to table '{table.get('name')}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
