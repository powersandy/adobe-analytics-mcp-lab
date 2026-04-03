---
name: cja-project-builder
description: >
  Canonical CJA Workspace project creation via MCP using the bundled v96 schema and guide. Use when Codex needs to build or revise Adobe Customer Journey Analytics Workspace projects, especially for repeatable patterns like top-N freeform tables, side-by-side comparison grids, inline date-range panels, linked charts, multi-panel layouts, or metric-summary tables. Prefer this skill for most CJA Workspace work because it combines the flexible base workflow with newer execution patterns, helper scripts, and v96 guardrails.
  When the task also involves inspecting, diffing, or patching large CJA JSON payloads such as `upsertProject` args or `projectBody.definition`, use it alongside `large-json-workflow`.
metadata:
  short-description: Canonical CJA Workspace project creation
---

# CJA Workspace Project Builder

## Overview

Build CJA Workspace projects quickly and accurately by combining MCP component discovery with a small set of proven v96 definition patterns. Prefer known-good project fragments over inventing raw JSON, keep date ranges inline by default, and optimize for a single accurate upsert whenever possible.

This is the canonical builder skill. Use it as the shared foundation for downstream CJA project-building skills.

Use progressive disclosure. Stay in lightweight mode by default and escalate only when explicit complexity triggers appear. Do not front-load PDF or schema reading when the build can be completed safely from the core workflow and known patterns.

## Core Execution Rules

- MCP is the default execution path.
- Do not switch to direct Adobe API calls automatically just because a payload is large, the JSON is awkward, or an MCP example looks incomplete.
- If a direct API workaround seems useful, pause and ask the user first. Explain briefly why you want to use the API instead of MCP, especially when the reason is payload size, tool-shape friction, or repeatability limits.
- Do not preflight-test `upsertProject` payload size before the first real attempt. Send the intended MCP upsert first.
- Only if the first MCP upsert fails for a clear size-related reason should you reduce scope and retry.
- When trimming for size, prefer an approximate halving strategy by meaningful branches such as panels, subpanels, or reportlets. Do not make random fine-grained cuts.
- Stop the size-retry loop after about 2 to 3 reductions. Then tell the user what was removed and ask whether to continue with a reduced project or use an approved workaround.

## Escalation Model

Start in lightweight mode. Escalate only when specific complexity triggers appear.

Complexity triggers:
- more than one panel, or several subpanels with coordinated layout
- linked visualizations
- revising an existing project instead of creating a fresh one
- copying from `describeProject` or another saved payload
- creating or validating a calculated metric
- unusual or less-familiar reportlet types
- payload-size risk, size-related retry handling, or noisy wrapper churn
- uncertainty about v96 shape details, linking, or layout behavior
- more than one plausible data view, target project, or metric interpretation

Lightweight mode:
- use the core workflow in this file
- do not open the PDF or schema unless a concrete uncertainty appears
- avoid helper scripts unless the task is a revision or payload-isolation problem

Escalated mode:
- open only the exact reference material needed for the triggered problem
- prefer the digest first, then a specific schema type or PDF section, not broad reading
- use helper scripts only when they materially reduce risk or context load

The skill exists to improve reliability and speed, not to make simple work feel ceremonial.

## Workflow

1. Bootstrap once per thread.
- In lightweight mode, rely on this file first and defer opening references until needed.
- When one or more complexity triggers appear, read [REFERENCE_DIGEST.md](REFERENCE_DIGEST.md) and skim only the exception rows relevant to the current build.
- Use [CJA_PROJECT_PRE_UPSERT_CHECKLIST.md](CJA_PROJECT_PRE_UPSERT_CHECKLIST.md) immediately before `upsertProject`.

2. Turn the request into a concrete build spec.
Capture:
- data view
- create vs update intent
- date handling: inline panel date range by default; only create saved date ranges if the user asks
- dimensions, metrics, calculated metrics, and segments
- layout: number of panels, tables, charts, grid arrangement, linked visualizations
- limits and sort intent: top 5, alphabetical, by Events, etc.
The user's requested project shape always wins. Use the fallback starter pattern only when the request does not already imply a clearer layout.

3. Confirm only when needed.
Do not force a confirm-first workflow for every request.
- If the user already gave a clear, actionable spec, proceed directly.
- If choices are ambiguous or have meaningful tradeoffs, give a short recap and confirm before upsert.
- Default to creating a new Workspace project, not updating an existing one.
- Only update an existing project when that intent is already clear from the thread context, or the user explicitly permits or requests modifying a specific existing project.
- Treat prior discovery of a similar project as reference material, not permission to overwrite it.

4. Resolve IDs with MCP.
Use `findDataViews`, `findDimensions`, `findMetrics`, `findCalculatedMetrics`, `findSegments`, then validate ambiguous picks with `describeDimension`, `describeMetric`, or `describeCalculatedMetric`. Never guess IDs.
For dimensions, remember the tool-shape mismatch: `findDimensions`, `runReport`, and related report calls use full ids like `variables/daterangeday`, but `describeDimension` expects the id without the `variables/` prefix, such as `daterangeday`.
Any component copied from `describeProject`, a saved payload, or another project must be revalidated in the target data view before reuse. Saved projects can contain stale, foreign, or non-rendering component IDs, so always confirm copied dimensions and metrics with `findDimensions`, `findMetrics`, `describeDimension`, or `describeMetric` against the destination data view.

5. Stop discovery when the decision surface is complete.
Discovery is done when you have:
- one chosen data view
- the intended create or update target
- the row dimensions, metrics, and segments needed for the build
- the layout shape needed for `projectBody.definition`
Do not keep exploring similar projects or extra components once those decisions are settled unless a specific unresolved pattern gap remains.

Reference-reading is also done when the immediate uncertainty is resolved. Do not keep browsing the PDF, schema, or similar projects after you have the one answer you needed.

6. Prefer reusable build patterns.
For common requests, use these defaults unless the user asks otherwise:
- Top-N dimension table: one dimension in `freeformTable.dimensionSettings`, one or more metrics in `columnTree.nodes`, `pagination.viewBy = N`, sort by the lead metric descending.
- Side-by-side table grid: separate subpanels with explicit `position.x`, `position.y`, and equal widths when the user asks for a dashboard row or grid. Treat `position.width` as a percentage-like value on a 0-100 scale, not a 12-column grid. For tables, avoid narrow layouts by default; keep them at roughly 20 or above, and usually much wider.
- Metric summary table: prefer a standard freeform table with a real row dimension; only use `advancedSettings.rows` or `KeyMetricSummaryReportlet` when copying a known-good fragment or following the PDF KMS/data-table pattern exactly, when the user asks for metrics as rows.
- For quick default builds, use a single panel with one table and one bar chart only as a fallback starter pattern when the user has not already asked for a different layout.
- Linked chart: keep the data table subpanel first with `linkedSourceId: ""`, then point the chart subpanel `linkedSourceId` at that table's subpanel id.
- Date scope: embed inline date definitions in the panel `dateRange` unless a reusable named date range is explicitly requested.
- Inline date range shape: for a truly inline panel date range, omit `id` entirely and use only `{"__entity__": true, "type": "DateRange", "__metaData__": {"definition": "START/END"}}`. Use `id` only for OOTB or saved date ranges that actually exist in CJA.

7. Reuse known-good fragments whenever possible.
If there is a nearby project in the target data view that already demonstrates the needed pattern, inspect it with `describeProject` and copy the smallest valid subtree. Revalidate against [projectSchema_v96.json](projectSchema_v96.json).
Important: treat `describeProject` as a clue, not as proof that a project is Workspace-safe. Some saved CJA projects can be persisted even though they are not fully valid for UI load, so a `describeProject` payload may itself contain broken patterns. Prefer fragments from projects that have been verified to open in Workspace, and favor the bundled known-good skill fragments when there is any doubt. Even when the structure is useful, revalidate every copied component ID in the target data view before upsert.

8. Make layout and naming user-facing.
Give every panel, subpanel, and reportlet a content-aware name. Avoid generic labels like only `Freeform Table` or `Panel` when the purpose is obvious.
When setting subpanel `position`, remember that Workspace width behaves like a percentage of 100. Do not assume dashboard-grid fractions like `12` means full width.
Default subpanel height behavior to `autoSize` unless the user explicitly asks for a fixed-height layout.
Use subpanel `description` when a caption truly helps, but do not force decorative text into every build.

9. Upsert once when the request is straightforward.
Avoid smoke projects for simple work. Only do a structure probe if the JSON shape is genuinely uncertain.
- Unless the user has already made an update path clear, this should mean one clean create of a new project rather than reusing an existing `projectId`.
- For fresh builds, prefer a small canonical payload over improvised large JSON, but only as a fallback when the user's request does not already define the shape: one panel with a freeform table and a bar chart using the same analysis, with an inline last-30-days date range unless the user asks for something else.
- If the request needs more structure than that simple pattern, explicitly consider [$large-json-workflow](/C:/Users/apowers/OneDrive%20-%20Adobe/Apps/myCode/summit%20git/mcp-summit-lab/.cursor/skills/large-json-workflow/SKILL.md) before hand-editing a large `definition`.
- Do not test payload size ahead of time. Try the intended `upsertProject` first.
- If the first MCP upsert fails for a clear size-related reason, trim the payload approximately in half by meaningful structure and retry iteratively.
- If MCP appears likely to fail because of payload size or tool-shape friction, do not silently fall back to direct API calls. Ask the user whether they want to stay MCP-only or explicitly approve an API workaround.

10. Use the patch helper for quick iterative edits.
When the user wants a small revision to an existing project, do not hand-rebuild a large payload unless you have to. Save the current project JSON locally, patch only the targeted subtree, then upsert the same `projectId`.
- Do not switch into this update workflow just because you found a related or duplicate-looking project. Use it only when the existing project is the obvious target from context, or the user has explicitly allowed editing it.
- Helper: [scripts/patch_cja_project.py](scripts/patch_cja_project.py)
- Example ops file: [scripts/patch_ops.example.json](scripts/patch_ops.example.json)
- Best for: stale component ID swaps, inline date-range replacement, panel renames, display-setting tweaks, and repeated branch-level edits across a large definition.
- Safe workflow:
  1. `describeProject` the current project.
  2. Revalidate any replacement component IDs in the destination data view.
  3. Save the payload locally.
  4. Patch it with the helper.
  5. Re-upsert the same `projectId`.
When the payload is large or the change is uncertain, use [$large-json-workflow](/C:/Users/apowers/OneDrive%20-%20Adobe/Apps/myCode/summit%20git/mcp-summit-lab/.cursor/skills/large-json-workflow/SKILL.md) first to isolate the exact branch to edit, compare pre/post payloads, or suppress noisy wrapper changes.

11. Use the helper scripts for common project-edit jobs.
- Highest-value helpers for large existing projects:
  [scripts/patch_cja_project.py](scripts/patch_cja_project.py), [scripts/extract_cja_fragments.py](scripts/extract_cja_fragments.py), and [scripts/audit_cja_components.py](scripts/audit_cja_components.py).
- Extract fragments: [scripts/extract_cja_fragments.py](scripts/extract_cja_fragments.py)
  Use when you want a clean panel or subpanel fragment from a larger project before reuse.
- Component audit for revalidation: [scripts/audit_cja_components.py](scripts/audit_cja_components.py)
  Use before copying or re-upserting a saved project so you can revalidate all referenced entities with MCP.
- Layout or grid normalize: [scripts/layout_cja_grid.py](scripts/layout_cja_grid.py)
  Keep as a convenience helper for simple equal-width rows or grids, not as a required step.
- Linked viz repair or build: [scripts/link_cja_visualization.py](scripts/link_cja_visualization.py)
  Keep as a narrow convenience helper when a chart should read from a specific table subpanel.
- Large JSON diffing and branch isolation: [$large-json-workflow](/C:/Users/apowers/OneDrive%20-%20Adobe/Apps/myCode/summit%20git/mcp-summit-lab/.cursor/skills/large-json-workflow/SKILL.md)
  Prefer this over a project-specific diff script when comparing saved payloads, isolating `projectBody.definition` changes, filtering ID churn, or narrowing review to one panel or reportlet branch before patching.

## Ask the User When

Ask before proceeding when:
- more than one data view is a plausible match
- more than one existing project could be the update target
- a requested KPI could reasonably map to multiple metrics or calculated metrics
- the user asked for something that implies a destructive overwrite or substantial project reduction
- you want to use a direct API workaround
- the size-retry ceiling has been reached and the next step would materially change scope

## Failure Classification

Classify `upsertProject` failures before deciding what to do next:

- Schema or shape failure:
  Re-check `projectSchema_v96.json`, the PDF, and the smallest affected subtree. Patch the shape and retry.
- Invalid component or data-view mismatch:
  Re-run MCP discovery and revalidate the relevant IDs in the destination data view.
- Clear size-related failure:
  Retry with an approximately halved payload by meaningful branches. Stop after about 2 to 3 retries and ask the user how to proceed.
- Auth, permission, or tool-availability failure:
  Stop and tell the user what is blocked.
- Ambiguous or mixed failure:
  Do not guess. Summarize the error and the likely causes, then choose the narrowest safe next step or ask the user if the tradeoff matters.

## Reference Access Rules

Use the least material necessary:
- Default: do not open the schema or PDF preemptively.
- First escalation step: open [REFERENCE_DIGEST.md](REFERENCE_DIGEST.md), not the PDF.
- Schema escalation: inspect only the exact type definition you need, not the whole schema.
- PDF escalation: open only the exact section or example that matches the current reportlet, linking rule, or layout problem.
- Payload escalation: use [$large-json-workflow](/C:/Users/apowers/OneDrive%20-%20Adobe/Apps/myCode/summit%20git/mcp-summit-lab/.cursor/skills/large-json-workflow/SKILL.md) instead of loading large raw JSON into context.
- Saved-project escalation: inspect only the smallest relevant subtree from `describeProject`.

## Accuracy Defaults

- Use `definition.version` `96`.
- Treat [projectSchema_v96.json](projectSchema_v96.json) and [Project Definition Guidev96.pdf](Project%20Definition%20Guidev96.pdf) as the source of truth over stale tool examples.
- Stay MCP-first. Treat direct API calls as an opt-in workaround that requires explicit user approval, not as an automatic fallback.
- Do not run payload-size probes before the first upsert. Use a first real attempt, then iterative approximate halving only after a clear size-related failure.
- Use inline panel date ranges by default.
- Omit `definition.viewDensity` unless the user explicitly asks to override Workspace density. When omitted, the project can inherit the user's or product's default row height behavior instead of forcing a table density such as `comfortable`.
- For v96 freeform rows, use `dimensionSettings`; do not fall back to legacy `dimension`-only row configs.
- Keep copied payloads minimal.
- For conversion-style metrics, remember common CJA keyword synonyms when resolving components: `visits` maps to Sessions, `visitors` maps to People, and `occurrences` can map to Events or Hits depending on the view.
- If a user-created calculated metric already exists, prefer its exact ID from `findCalculatedMetrics` when building a project instead of trying to recreate the same formula during project assembly.
- When resolving formula inputs for a calculated metric, prefer the exact component IDs confirmed by `describeMetric` or the exact IDs already present in a known-working calculated metric definition. Switch to reserved reporting identities only when you are intentionally copying a known-working formula that already uses them.
- When creating a new calculated metric with `upsertCalculatedMetric`, include the destination `dataId` inside `metricBody`. `Orders / Visits` using `metrics/commerce.purchases.value` over `metrics/visits` is a known-good pattern when `dataId` is present, and can fail without it even when the metric IDs are valid in reports.
- If the user asks for interesting dimensions or metrics, prefer broadly interpretable web/app and business components over obscure technical fields unless the data view strongly suggests otherwise.

## Anti-Patterns

Avoid these unless the user explicitly asks for them:
- reusing an existing `projectId` when update intent is not clear
- trusting `describeProject` payloads blindly
- inventing component IDs
- using plain prose for Quill-backed fields
- setting `definition.viewDensity` without being asked
- pre-testing payload size before the first upsert
- using direct API calls because they feel easier than MCP
- continuing discovery after the necessary decisions are already resolved

## Deep Links

When returning CJA component links, treat editor URLs as derived values, not MCP output:
- `findSegments` and `findCalculatedMetrics` do not return direct UI links. Build links separately from validated route patterns plus tenant context.
- Keep the tenant slug used in the URL path after `#/@` separate from the component ID. Do not assume the tenant slug equals the org ID embedded in a component ID.
- Prefer only route patterns that have been validated in the current org or from a known-working example.

Validated editor patterns:
- Segments: `https://experience.adobe.com/#/@<tenant>/platform/analytics/#/components/segments/edit/<segmentId>`
- Segment legacy fallback when needed: `https://experience.adobe.com/#/@<tenant>/platform/analytics/#/components/filters/edit/<segmentId>`
- Calculated metrics: `https://experience.adobe.com/#/@<tenant>/platform/analytics/#/components/calculatedMetrics/edit/<calculatedMetricId>`

If the tenant slug is unknown, return the component ID and say the link must be derived from a known-working tenant context rather than guessing.

## Density Inheritance

Workspace project definitions can include `definition.viewDensity`, which acts as an explicit density override. If agents set this field, table row height may stop inheriting the user's compact or product-default preference.

Default rule:
- Do not set `definition.viewDensity` for normal project creation or patching.
- Only include it when the user explicitly asks for a density override such as comfortable.

When revising an existing project:
- If the goal is to restore inherited density behavior, remove `definition.viewDensity` rather than changing it from one explicit value to another.

## Calculated Metrics

Use this mini-workflow whenever the project depends on a conversion rate or other derived KPI:
- Discover first with `findCalculatedMetrics` and reuse an existing metric when it already matches the request.
- If a matching metric exists, validate it with `describeCalculatedMetric` and use that exact ID in the project.
- If no matching metric exists, create one with `upsertCalculatedMetric` and include `dataId` inside `metricBody`.
- After creation, validate it with `describeCalculatedMetric` or a small `runReport` before wiring it into `upsertProject`.
- If creation fails but the base metrics work in `runReport`, check whether `dataId` is missing before assuming the formula itself is invalid.

Working example for `Orders / Visits`:

```json
{
  "dataId": "dv_...",
  "name": "Orders per Session Conversion Rate",
  "description": "Orders divided by visits.",
  "polarity": "positive",
  "precision": 2,
  "type": "percent",
  "definition": {
    "formula": {
      "func": "divide",
      "col1": {
        "func": "metric",
        "name": "metrics/commerce.purchases.value",
        "description": "Orders [multi]"
      },
      "col2": {
        "func": "metric",
        "name": "metrics/visits",
        "description": "Sessions"
      }
    },
    "func": "calc-metric",
    "version": [1, 0, 0]
  }
}
```

## Minimal Patterns

Use these as the fallback starting point for new builds when the user has not already specified a clearer structure:
- New single-panel starter dashboard:
  1. one panel with an inline last-30-days date range by default
  2. one freeform table with one row dimension and the metrics `Events` and `People`
  3. one bar chart subpanel based on that same table analysis
- New project flow:
  1. resolve all component IDs
  2. create or select any needed calculated metric
  3. build a minimal `projectBody.definition`
  4. `upsertProject` once
  5. only reach for copied fragments or [$large-json-workflow](/C:/Users/apowers/OneDrive%20-%20Adobe/Apps/myCode/summit%20git/mcp-summit-lab/.cursor/skills/large-json-workflow/SKILL.md) if the straightforward shape stops being simple

Literal fallback starter definition:

Use this only for vague or demo-oriented requests such as "make me a project" when the user has not already implied a clearer structure. Start from [starter_project_v96.json](starter_project_v96.json).
- Replace the destination `dataId` in the final `projectBody`.
- The starter fixes the row dimension to `variables/daterangeday`, the starter metrics to `metrics/occurrences` and `metrics/visitors`, and the date range to inline last 30 days.
- The starter defaults subpanel `position` to `autoSize` rather than fixed heights.
- The included workspace, panel, and subpanel ids only need to stay internally consistent within the project definition. They do not need to be globally unique across different projects.

## Canonical Mini-Recipes

- One-table project:
  one panel, one freeform table, one row dimension, one or more metrics, inline date range, lead metric sort descending
- Table plus linked chart:
  create the table subpanel first, then add a linked chart subpanel that points to the table subpanel id
- Two-panel comparison:
  use two panels only when the analyses differ meaningfully by date range, segment, or question being answered
- Metric summary panel:
  prefer a standard freeform table with real rows; only use `KeyMetricSummaryReportlet` when you are following a known-good pattern
- Existing-project branch edit:
  `describeProject`, revalidate component IDs, patch only the intended subtree, use [$large-json-workflow](/C:/Users/apowers/OneDrive%20-%20Adobe/Apps/myCode/summit%20git/mcp-summit-lab/.cursor/skills/large-json-workflow/SKILL.md) if the payload is noisy, then re-upsert the same `projectId`

## JSON Helper

This skill already recommends the JSON helper skill: [$large-json-workflow](/C:/Users/apowers/OneDrive%20-%20Adobe/Apps/myCode/summit%20git/mcp-summit-lab/.cursor/skills/large-json-workflow/SKILL.md).
Use it when:
- a project `definition` is large enough that branch isolation matters
- you are patching one panel or reportlet inside a noisy payload
- you need pre/post diffs that suppress wrapper churn and ID noise
- a direct hand-edit feels riskier than isolating the exact subtree first

## Fast Selection Heuristics

When the user asks for a quick exploratory project without naming exact components:
- Prefer dimensions that are understandable in a demo: page name, channel, referrer, session type, product category, campaign, device, geography.
- Prefer metrics that are broadly meaningful: Events, People, Page Views, Orders, Revenue, Product Views, Sessions.
- Validate the final shortlist with `describe*` calls before building.
- If one candidate is noisy or odd-looking, swap it for a cleaner alternative rather than forcing it into the project.

## Error Examples

- Error suggests unknown property or invalid type:
  Treat it as a schema or shape problem. Re-check the exact subtree against the schema and PDF.
- Error suggests component not found or invalid metric or dimension:
  Re-run MCP discovery and confirm the component belongs to the selected data view.
- Error clearly indicates request entity too large or payload too large:
  Keep MCP, reduce the payload by approximately half using meaningful branches, and retry.
- Error suggests auth, entitlement, or tool availability:
  Stop and report the blocker instead of improvising a workaround.

## Output Contract

Before the first upsert, give a short build summary that includes:
- chosen data view
- create vs update intent
- the high-level layout shape
- the main dimensions, metrics, segments, and date policy

After the upsert or final failure, report:
- whether it was create or update
- whether MCP succeeded directly or needed iterative size reduction
- any compromises made, such as removed panels or deferred visualizations
- any user decision still needed

## Repeatability Mode

Bias toward repeatable, teachable patterns:
- prefer MCP-only approaches by default
- avoid org-specific hacks unless the user explicitly allows them
- if you use a workaround, label it clearly as environment-specific
- prefer solutions that another lab author can reproduce with the same skill and MCP tools

## References

- [REFERENCE_DIGEST.md](REFERENCE_DIGEST.md): bootstrap routing, guide map, exception table, helper script pointers, and common failure handling
- [CJA_PROJECT_PRE_UPSERT_CHECKLIST.md](CJA_PROJECT_PRE_UPSERT_CHECKLIST.md): final gate before `upsertProject`
- [projectSchema_v96.json](projectSchema_v96.json): v96 schema authority
- [Project Definition Guidev96.pdf](Project%20Definition%20Guidev96.pdf): reportlet and layout reference
