# CJA project builder - reference digest (v96)

**Purpose:** Where to look, in what order, without duplicating the PDF or schema. Keep this file short and high-signal.

---

## Division of Labor

| Asset | Role |
|--------|------|
| [SKILL.md](SKILL.md) | Workflow: intent -> spec -> MCP discovery -> build -> `upsertProject`. |
| **This digest** | Bootstrap routing, guide map, helper pointers, exception table, and failure handling shortcuts. |
| [CJA_PROJECT_PRE_UPSERT_CHECKLIST.md](CJA_PROJECT_PRE_UPSERT_CHECKLIST.md) | Final yes/no gate immediately before upsert. |
| `projectSchema_v96.json` | Allowed keys per type (`additionalProperties: false`). |
| `Project Definition Guidev96.pdf` | Examples, linking, KMS/Combo/Flow/cohort/Journey, and troubleshooting. |

---

## Bootstrap

1. Start with [SKILL.md](SKILL.md). Stay in lightweight mode unless a complexity trigger appears.
2. Use this digest as the first escalation step, not as mandatory front-loaded reading for every request.
3. Skim only the exception rows and helper notes relevant to today's build.
4. Run [CJA_PROJECT_PRE_UPSERT_CHECKLIST.md](CJA_PROJECT_PRE_UPSERT_CHECKLIST.md) immediately before `upsertProject`.
5. For triggered complex builds such as linked charts, KMS, Combo, Flow, cohort, Journey Canvas, or tight grids, read only the matching PDF sections before inventing structure.

Do not load full `describeProject` payloads or the whole schema into context. Copy minimal subtrees and validate.

Complexity triggers that justify using this digest:
- linked visualizations
- multiple panels or coordinated layout
- revising an existing project
- copying from a saved project payload
- calculated metric creation or reuse uncertainty
- unusual reportlet types
- payload-size retries or noisy JSON editing
- unclear v96 shape details

---

## Structure and Size Handling

If the request is simple, skip test upserts and go straight to the real payload.

Use this rule set:
- Do not run a preflight payload-size test before the first real `upsertProject` attempt.
- Try the intended MCP upsert first.
- If it fails for a clear size-related reason, reduce scope by approximately half using meaningful branches such as panels, subpanels, or reportlets, then retry.
- Stop after about 2 to 3 size-reduction retries and ask the user how to proceed.
- If you believe you must validate JSON shape with a direct API workaround, ask the user first instead of switching automatically.

Resolve IDs with MCP when unsure. For a generic smoke table on a known data view, these are common patterns:

| Role | Typical choice | Notes |
|------|----------------|-------|
| Metric | `metrics/occurrences` | Events / occurrences metric. |
| Row dimension | `variables/daterangeday` | Confirm with `findDimensions` if needed. |
| Segment | `All_Visits` | Common built-in all-data segment pattern. |
| Panel date | `last7days` or inline `td-6d/td+1d` | Use the shape that matches the build intent. |

If a smoke artifact was created, replace it in place or remove it when the real build is done.

---

## Versioning

- Target `definition.version` `"96"` with this folder's schema and PDF.
- MCP `upsertProject` descriptions may show older shapes. Resolve conflicts using `projectSchema_v96.json` and the PDF, not stale inline examples.
- When Adobe ships a newer UI definition version, update the schema, PDF, checklist, and this digest together.

---

## PDF Guide Map

| Need | Guide area |
|------|------------|
| Entities and date math | Section 6 entity pattern; Section 7 date ranges |
| Panels, subpanels, grid, Quill descriptions | Section 8 |
| Freeform tables | Section 9 |
| Charts reading a table | Section 11 linking |
| Specific visualization types | Section 10 reference table plus matching subsection |
| Recipes | Section 12 common patterns |
| Errors | Section 15 troubleshooting |

If the TOC is slow to navigate, search the PDF for the reportlet type name, for example `KeyMetricSummaryReportlet`.

---

## Schema Grep

Before inventing properties, locate the exact type definition:

- `FreeformReportlet`
- `FreeformTable`
- `FreeformTableDimensionSettings`
- `GenericSubPanel`
- `GridPosition`
- `TextReportlet`
- any visualization type such as `LineReportlet`, `BarReportlet`, or `KeyMetricSummaryReportlet`

---

## Helper Scripts

Patch helper:
- `scripts/patch_cja_project.py`
- `scripts/patch_ops.example.json`
- Best for stale component ID swaps, inline date-range fixes, panel renames, and repeated setting changes.

Other helpers:
- Highest-value helpers for agent workflows:
  `scripts/extract_cja_fragments.py` and `scripts/audit_cja_components.py`
- Convenience helpers:
  `scripts/layout_cja_grid.py` for equal-width row or grid normalization
  `scripts/link_cja_visualization.py` for linked table/chart repairs

When the payload is noisy or large, pair this skill with [$large-json-workflow](/C:/Users/apowers/OneDrive%20-%20Adobe/Apps/myCode/summit%20git/mcp-summit-lab/.cursor/skills/large-json-workflow/SKILL.md) instead of maintaining a separate project-specific diff helper.

---

## Mini-Recipes

- One-table project:
  one panel, one freeform table, one row dimension, one or more metrics, inline date range
- Vague demo request:
  start from [starter_project_v96.json](starter_project_v96.json), set the destination `dataId`, and keep the built-in `variables/daterangeday` row dimension unless the user asks for something else
- Table plus linked chart:
  build the table subpanel first, then link the chart subpanel to that table subpanel id
- Two-panel comparison:
  use separate panels only when the comparison question really differs by segment, date range, or analysis goal
- Metric summary:
  prefer a standard freeform table with real rows unless a known-good `KeyMetricSummaryReportlet` pattern is required
- Existing project revision:
  `describeProject`, revalidate copied IDs, patch the smallest subtree, then re-upsert the same `projectId`

---

## Failure Shortcuts

| Failure type | Default response |
|--------------|------------------|
| Schema / shape | Re-check the smallest affected subtree against the schema and PDF. |
| Invalid component ID | Re-run MCP discovery and validate the component in the destination data view. |
| Clear size-related failure | Retry with an approximately halved payload by meaningful branches. |
| Auth / permissions / tool missing | Stop and tell the user what is blocked. |
| Mixed or unclear failure | Do not guess; summarize the error and choose the narrowest safe next step. |

---

## Exception Table

| Topic | Rule |
|------|------|
| Freeform rows (v96) | Use `freeformTable.dimensionSettings[]` with `{ dimension, id }`, not legacy `dimension` alone. |
| Rich text | `TextReportlet.textContent` and subpanel `description` need stringified Quill Delta. Plain prose often renders blank. |
| Inline date range | For a true inline panel date range, omit `id` and use only `__entity__`, `type: "DateRange"`, and `__metaData__.definition`. |
| Density inheritance | `definition.viewDensity` is an explicit override. Omit it unless the user explicitly asks for a density override. |
| Subpanel height | Default subpanel `position` to `autoSize` unless the user explicitly asks for fixed heights. Avoid short fixed-height defaults for tables. |
| `describeDimension` id shape | `findDimensions` and report calls use full ids like `variables/daterangeday`, but `describeDimension` expects the id without the `variables/` prefix, such as `daterangeday`. |
| Copied component IDs | Any copied dimension, metric, segment, or date range must be revalidated in the destination data view or org context before reuse. |
| `projectBody` | Use the live MCP tool schema for field names such as `dataId` vs `rsid`. |
| Grid width scale | Treat `position.width` as a percentage-like 0-100 scale, not a 12-column layout. |
| Linked viz | Data table: `linkedSourceId: ""`. Chart: `linkedSourceId` equals the data subpanel `id`. |
| `lockedSelection` | Where used, include `"type": "FreeformBreakdownSelection"`. |
| Metrics as rows | Schema-valid metrics-as-rows snapshots may still render blank. Prefer normal freeform tables or known-good KMS patterns. |
| `describeProject` trust level | Use `describeProject` as a clue, not proof that a saved project is safe to copy. |
| Payload size | Do not pre-test size. Use the real first upsert, then iterative approximate halving only after a clear size-related failure. |
| Direct API fallback | Treat direct API usage as opt-in and ask the user first. |

---

## Error Examples

- Unknown property or invalid type:
  likely schema or shape problem; re-check the subtree
- Component not found:
  likely invalid or foreign ID; re-run discovery
- Request entity too large:
  keep MCP, trim by meaningful branches, retry
- Auth or entitlement error:
  stop and report the blocker

---

## Final Gate

-> [CJA_PROJECT_PRE_UPSERT_CHECKLIST.md](CJA_PROJECT_PRE_UPSERT_CHECKLIST.md)
