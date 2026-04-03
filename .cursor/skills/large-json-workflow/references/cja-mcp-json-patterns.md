# CJA MCP JSON Patterns

Use this reference when the JSON comes from CJA MCP calls or CJA workspace/project definitions.

## Common high-value branches

- `projectBody.definition`
- `projectBody.definition.workspaces`
- `projectBody.definition.workspaces[0].panels`
- `projectBody.definition.workspaces[0].panels[n].subPanels`
- `segmentBody`
- `audienceBody`
- `metricBody`
- `definition`

## Common low-value or noisy branches

- Root-level generated IDs
- Nested `id` fields used only as internal object identifiers
- `modified*`, `updated*`, `created*`, `timestamp`, `generatedAt`
- Wrapper fields like `expansions` when the real question is about behavior
- Wrapper-only project metadata like `projectId`, `projectBody.name`, and `projectBody.description`

## CJA project preset

Use `--cja-project-noise` when comparing `upsertProject` payloads and the goal is to isolate behavior-changing definition edits.

This preset currently ignores:

- Common volatile metadata keys from `--ignore-common-noise`
- `expansions`
- `projectId`
- `projectBody.name`
- `projectBody.description`

It intentionally does not ignore:

- `linkedSourceId`
- `sort.columnId`
- `dataId`
- panel, subpanel, reportlet, dimension, metric, segment, and date-range structure

## Suggested workflow for `upsertProject` payloads

1. Run `summary` on the whole file.
2. Extract `projectBody.definition`.
3. Diff the two files with `--ignore-common-noise`.
4. If still broad, add `--focus-path-prefix projectBody.definition.workspaces`.
5. If the question is panel-specific, focus to the exact panel path.
6. If the diff is still noisy, use `--summary-only` first.

## Ready-to-copy commands

Compare two CJA project payloads while hiding common ID churn:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff old.json new.json --ignore-common-noise
```

Compare two CJA project payloads while hiding wrapper-only project metadata too:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff old.json new.json --cja-project-noise
```

Summarize only the paths that changed under one panel:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff old.json new.json --ignore-common-noise --focus-path-prefix projectBody.definition.workspaces[0].panels[1] --summary-only
```

Compare only the actual project definition, not the wrapper envelope:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff old.json new.json --path-a projectBody.definition --path-b projectBody.definition --ignore-common-noise
```

Compare segment logic while ignoring wrapper metadata:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff before.json after.json --path-a segmentBody --path-b segmentBody --ignore-common-noise --summary-only
```

## Ready-to-copy prompt patterns

- "Use $large-json-workflow to tell me whether these two `upsertProject` payloads differ in behavior or only in generated IDs."
- "Use $large-json-workflow to compare only `projectBody.definition` across these files and summarize the important changed paths."
- "Use $large-json-workflow to inspect this CJA MCP payload and identify the smallest subtree I should edit."
- "Use $large-json-workflow to diff these two segment definitions and ignore wrapper noise."

## Interpretation tips

- Changes to reportlet `type`, freeform dimensions, metrics, sort settings, date ranges, filters, breakdowns, and panel composition are usually semantic.
- Changes to internal IDs are often non-semantic unless another branch references those IDs by value.
- A changed `sort.columnId` can still matter even if IDs are otherwise noisy, because it may point sorting at a different metric column.
- `linkedSourceId` can matter because it controls linkage between source tables and visualizations.
