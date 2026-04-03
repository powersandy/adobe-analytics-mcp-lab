#!/usr/bin/env python3
"""Extract panels or subpanels from a local CJA project JSON file."""

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


def iter_panels(project_body: dict[str, Any]):
    for workspace in project_body["definition"]["workspaces"]:
        for panel in workspace.get("panels", []):
            yield workspace, panel


def find_panel(project_body: dict[str, Any], panel_id: str | None, panel_name: str | None):
    for workspace, panel in iter_panels(project_body):
        if panel_id and panel.get("id") == panel_id:
            return workspace, panel
        if panel_name and panel.get("name") == panel_name:
            return workspace, panel
    raise ValueError("Panel not found")


def find_subpanel(panel: dict[str, Any], subpanel_id: str | None, subpanel_name: str | None):
    for subpanel in panel.get("subPanels", []):
        if subpanel_id and subpanel.get("id") == subpanel_id:
            return subpanel
        if subpanel_name and subpanel.get("name") == subpanel_name:
            return subpanel
    raise ValueError("Subpanel not found")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a panel or subpanel from a local CJA project JSON file.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--kind", choices=["panel", "subpanel"], required=True)
    parser.add_argument("--panel-id")
    parser.add_argument("--panel-name")
    parser.add_argument("--subpanel-id")
    parser.add_argument("--subpanel-name")
    args = parser.parse_args()

    project_body = resolve_project_body(load_json(Path(args.input)))
    workspace, panel = find_panel(project_body, args.panel_id, args.panel_name)

    if args.kind == "panel":
        result = {
            "workspaceId": workspace.get("id"),
            "panel": panel,
        }
    else:
        subpanel = find_subpanel(panel, args.subpanel_id, args.subpanel_name)
        result = {
            "workspaceId": workspace.get("id"),
            "panelId": panel.get("id"),
            "panelName": panel.get("name"),
            "subpanel": subpanel,
        }

    save_json(Path(args.output), result)
    print(f"Wrote {args.kind} fragment to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
