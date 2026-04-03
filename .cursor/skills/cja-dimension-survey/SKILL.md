---
name: cja-dimension-survey
description: >
  CJA dimension coverage and survey-grid analysis. Use when the user asks which dimensions have data, wants a broad dimension survey project, requests a multi-panel grid of dimension tables, or wants a data-view exploration or audit focused on dimensions. Produces either an audit-style coverage project or a faster survey-grid project. Use cja-project-builder as the canonical project-structure foundation; this skill adds dimension-selection, qualification, and coverage-specific workflow.
---

# CJA Dimension Coverage

Build a CJA project that shows which dimensions have usable data in a data view. This skill now supports two related but distinct modes:

- `survey grid`: fast exploratory Workspace project with many dimension tables, often in 3x3 panels
- `coverage audit`: stricter qualification-focused project for determining which dimensions meaningfully contain data

Use [`cja-project-builder`](../cja-project-builder/SKILL.md) for all v96 project structure, date-range shape, layout, naming, and helper-script guidance. This skill defines the dimension-coverage workflow and guardrails on top of that canonical builder.

Do not auto-invoke unless the user explicitly asks for dimension coverage, data-view exploration, lots of dimensions in table grids, or similar dimension-focused audits.

---

## When to Use

User explicitly asks for:
- "Dimension coverage"
- "Which dimensions have data"
- "Survey lots of dimensions"
- "Build a project with many dimension tables"
- "Data view exploration"
- "Data quality audit on dimensions"
- Similar intent to explore or qualify dimensions in bulk

---

## Operating Modes

### 1. Survey Grid

Use when the user wants a Workspace survey artifact, such as:
- top 20 or 30 non-empty dimensions
- 3x3 panels of tables
- top 5 rows by Events
- broad exploratory scanning

Defaults:
- dimension selection: top validated non-empty dimensions
- ordering: preserve chosen ranking unless user asks for lexicographic
- metric: Events
- viewBy: 5
- layout: 9 tables per panel in a 3x3 grid unless user asks otherwise
- date handling: inline panel date range

### 2. Coverage Audit

Use when the user cares about qualification rules and a defensible inclusion threshold, such as:
- which dimensions truly have data
- which dimensions meet a minimum non-null threshold
- data quality or governance review

Defaults:
- dimension selection: qualification-first
- ordering: lexicographic by ID or path unless user asks otherwise
- thresholding: exclude dimensions with insufficient non-null values
- include technical descriptions when useful

---

## Workflow

### Step 1 - Turn the request into a concrete spec

If the user already specified the key parameters, do not stop to ask routine questions. Proceed directly when the request already defines enough of:
- data view
- count of dimensions
- date range
- layout
- metric
- ordering preference
- threshold or qualification rule, if any

Only ask follow-up questions when the missing choice would materially change the result.

Suggested defaults when the user did not specify:
- mode: `survey grid`
- count: 20
- metric: Events
- row limit: 5
- date range: Last 30 Full Days
- ordering:
  - survey grid: validated non-empty ranking
  - coverage audit: lexicographic by ID
- minimum non-null item threshold for audit mode: 2

### Step 2 - Data view selection

- Use `findDataViews` and paginate through all pages as needed.
- Match the user’s requested data view directly when specified.
- If not specified, suggest likely candidates from the complete list.
- Do not hardcode or privilege one historical demo data view.

### Step 3 - Dimension selection strategy

Choose the strategy that best matches the request:

- `validated non-empty`
  - Best for survey grids
  - Start with `findDimensions`
  - Prefer dimensions marked with `hasData: true` when available
  - Validate ambiguous or borderline candidates with `searchDimensionItems` or `runReport` when needed

- `usage-ranked`
  - Use `listComponentUsage(componentType: "dimension")` when the user wants the most-used dimensions

- `lexicographic audit`
  - Best for systematic audits
  - Use `findDimensions`, then sort by ID or path before qualification

- `curated or interesting`
  - Prefer understandable business-facing dimensions over obscure technical fields unless the user asked for exhaustive coverage

- `user-specified`
  - Preserve the user’s supplied list and validate each dimension

### Step 4 - Qualification logic

Use a practical qualification ladder rather than one rigid rule:

1. Start with `findDimensions`.
2. Exclude hidden or obviously unusable dimensions when appropriate.
3. For fast non-empty qualification, prefer `hasData: true` when the MCP response provides it.
4. If the user asked for stricter validation, or if `hasData` is missing or insufficient, validate with:
   - `searchDimensionItems`, or
   - `runReport` using the dimension and Events
5. Exclude dimensions that return errors or clearly fail the requested qualification rule.

Qualification defaults by mode:

- `survey grid`
  - Prefer a fast, pragmatic non-empty test
  - `hasData: true` is sufficient unless the user asked for stricter validation

- `coverage audit`
  - Use explicit qualification
  - Count rows where the value is not `"No value"`
  - Exclude dimensions below the requested threshold

### Step 5 - Dimension filtering guardrails

Apply these unless the user explicitly asks for exhaustive inclusion:
- skip dimensions starting with `variables/daterange`
- skip dimensions starting with `variables/timepart`
- skip dimensions that error during validation
- skip noisy technical dimensions when the request is clearly exploratory rather than exhaustive

Do not assume these skips are mandatory in every scenario. If the user wants all dimensions, honor that and only exclude those that truly fail validation or access.

### Step 6 - Project structure

Use [`cja-project-builder`](../cja-project-builder/SKILL.md) for the actual project definition.

Coverage-specific structure defaults:
- project naming should reflect the mode, count, metric, and date window
- use multi-panel layouts when needed
- for survey grids, default to 9 tables per panel in a 3x3 layout
- last panel may have fewer tables
- use inline panel date ranges by default
- use content-aware panel names

Recommended naming patterns:
- survey grid:
  - `"Top 30 Non-Empty Dimensions - Events Grid"`
- coverage audit:
  - `"Dimension Coverage Audit - >=2 Non-Null Items"`

Panel naming:
- survey grid:
  - `"Dimensions 1-9"`, `"Dimensions 10-18"`, and so on
- audit:
  - either indexed groups or first-to-last dimension naming, depending on readability

### Step 7 - Subpanel layout

For reportlet shape, v96 structure, and layout rules, defer to [`cja-project-builder`](../cja-project-builder/SKILL.md), its references, and helper scripts.

Survey-grid defaults:
- explicit 3x3 subpanel positions
- width in thirds on a 0-100 scale
- use fixed heights in a tested range, usually around 260 to 280 for compact 5-row tables
- `autoSize: false`
- `linkedSourceId: ""` for tables

Do not hardcode one magic height as a universal rule. Use a tested range and adjust based on density and number of columns.

### Step 8 - Table configuration

Defaults unless the user asks otherwise:
- metric: Events (`metrics/occurrences`)
- pagination: `viewBy: 5`
- sort: descending by Events
- one row dimension per table using `freeformTable.dimensionSettings`

### Step 9 - Descriptions and captions

Descriptions are mode-dependent:

- `survey grid`
  - optional
  - omit unless a caption adds clear value

- `coverage audit`
  - optional but often useful
  - may include shortened technical path information

If using shortened-path descriptions:
1. Remove `variables/`
2. If the string starts with a 24-character alphanumeric token before the first `.`, replace that token with `...` plus its last 4 characters
3. Split into:
   - `Y`: everything up to and including the final `.`
   - `Z`: everything after the final `.`

Quill description format:
```json
{"ops":[{"insert":"<Y>\n"},{"attributes":{"italic":true},"insert":"<Z>"},{"insert":"\n"}]}
```

Use this only when the description is genuinely helpful.

### Step 10 - Execute

- Prefer one accurate `upsertProject` when the request is straightforward.
- Use `large-json-workflow` when the payload is large, needs diffing, or requires branch-level edits.
- Return the clickable Workspace link on success.

---

## Tool Notes

When using `searchDimensionItems`:
- use explicit `dataViewId`
- use explicit date boundaries
- preserve the current working `dimensionId` format required by the MCP tool
- treat pagination quirks as implementation details, not permanent truths; if tool behavior has drifted, follow the currently working contract

When using `runReport` for validation:
- use Events as the default metric
- keep the validation query small and purpose-built

---

## Guardrails

- Do not auto-invoke unless the user explicitly requests dimension coverage or a bulk dimension survey.
- Do not force old configuration questions when the user already gave a complete spec.
- Do not hardcode one legacy demo data view.
- Do not require lexicographic ordering for survey projects unless the user asked for it.
- Do not assume `describeProject` is required to succeed; build fresh from the canonical builder when appropriate.
- Do not overuse technical descriptions in exploratory survey projects.
- Prefer understandable, useful outputs over rigid adherence to old audit habits when the user’s goal is exploration.
