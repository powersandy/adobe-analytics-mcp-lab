---
name: large-json-workflow
description: Analyze, compare, and safely edit large JSON files or nested JSON fragments without pasting entire blobs into context. Use when Codex needs to inspect oversized payloads, summarize structure, compare one JSON file to another, diff one subtree against another chunk, trace changes across versions, normalize noisy formatting, or extract a precise path from complex objects such as API payloads, config files, schema outputs, MCP request bodies, or exported analytics definitions. Especially use for CJA MCP work such as comparing `upsertProject` args, isolating `projectBody.definition` changes, reviewing `segmentBody` or audience definitions, and separating volatile generated IDs from meaningful behavioral changes.
---

# Large JSON Workflow

Use this skill to stay fast and precise when JSON is too large, too nested, or too noisy to reason about comfortably by eye. It is generic for large JSON work, but it should default to CJA MCP-friendly workflows whenever the payload looks like project, segment, audience, metric, or report-definition JSON.

## Quick Start

1. Start with structure, not full content.
2. Narrow work to the smallest relevant subtree.
3. Compare normalized chunks before drawing conclusions.
4. Filter volatile metadata when noise is obscuring the real diff.
5. Summarize meaningful changes separately from formatting noise.

Prefer using the helper script in [`scripts/json_workbench.py`](scripts/json_workbench.py) instead of loading entire files into model context.

For recurring CJA patterns and ready-to-copy prompts, read [`references/cja-mcp-json-patterns.md`](references/cja-mcp-json-patterns.md).

## Core Workflow

### 1. Map the shape first

Run a summary before editing or comparing:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py summary path\to\file.json
```

Use this to answer:

- Is the root an object or array?
- Which top-level keys matter?
- Where are the large lists or deeply nested branches?
- Which subtree should be compared instead of diffing the whole file?

For CJA MCP payloads, start by checking whether the real work lives under:

- `projectBody.definition`
- `projectBody.definition.workspaces`
- `segmentBody`
- `audienceBody`
- `metricBody`
- `definition`

If the relevant area is unclear, read [`references/path-syntax.md`](references/path-syntax.md) and extract a smaller branch first.

### 2. Scope to the exact chunk

When the user asks about "that section," "the changed block," or "the project definition part," extract only the relevant subtree:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py extract path\to\file.json --path workspaces[0].panels[0]
```

Use scoped extraction whenever:

- The full file is too large to inspect safely
- Only one branch appears to be broken
- Two files should be compared at different paths
- You want to reuse one chunk as a clean reference

For CJA MCP, prefer comparing subtrees instead of whole envelopes. The envelope often includes IDs, expansions, labels, or generated metadata that hide the meaningful change.

### 3. Diff normalized JSON, not raw text

For meaningful comparisons, diff parsed JSON rather than line-based text:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff before.json after.json
```

For subtree-to-subtree comparison:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff before.json after.json --path-a definition --path-b definition
```

Use `--ignore-array-order` only when array order is not semantically meaningful.

When the payload includes volatile metadata, start with:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff before.json after.json --ignore-common-noise
```

For `upsertProject`-style CJA payloads where the real question is behavioral change, prefer:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff before.json after.json --cja-project-noise
```

Add targeted filters when needed:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff before.json after.json --ignore-key id --ignore-key modified --ignore-path definition.version
```

Use `--classify-noise` when you want the output to label UUID-like and datetime-like changes without suppressing them.

Use `--focus-path-prefix` to narrow output to one branch when the diff is still too broad:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff before.json after.json --ignore-common-noise --focus-path-prefix projectBody.definition.workspaces[0].panels[2]
```

Use `--summary-only` when you want a quick decision surface for large diffs:

```powershell
python .cursor/skills/large-json-workflow/scripts/json_workbench.py diff before.json after.json --ignore-common-noise --summary-only
```

### 4. Report changes in a decision-friendly way

After inspecting or diffing, summarize results as:

- Added paths
- Removed paths
- Value changes
- Type changes
- Array-length changes
- High-risk changes that may affect behavior

Separate semantic changes from noise such as key order or whitespace.
Call out when noise filters were applied so the reader knows which changes were intentionally excluded.

For CJA MCP, explicitly distinguish between:

- Structural/reporting changes: panel composition, reportlet type, dimension IDs, metric IDs, sorting, date ranges, segment filters
- Generated noise: internal IDs, GUID churn, timestamps, editor metadata
- Wrapper-only project metadata: `projectId`, `expansions`, project title/description text

## Editing Guidance

- Preserve existing encoding and overall file style unless a cleanup is part of the request.
- Avoid rewriting the whole file when only one subtree needs to change.
- When a change is risky, extract the target branch first, reason about it, then patch the source file.
- If a diff is very large, report representative paths and counts instead of pasting giant payloads.
- When arrays are long, describe shape and sample entries rather than dumping everything.
- For CJA MCP payloads, keep envelope changes and definition changes mentally separate. A safe default is to inspect `projectBody.definition` first and only then look at root-level metadata.

## Helper Script

[`scripts/json_workbench.py`](scripts/json_workbench.py) supports three subcommands:

- `summary`: show shape, key distribution, child previews, and scalar counts
- `extract`: print one subtree using dotted paths with array indexes
- `diff`: compare two JSON documents or two extracted subtrees, optionally ignoring noisy keys or specific paths, focusing on one path prefix, or returning summary-only output

Use the script first when a JSON file is large enough that reading it raw would waste context or increase error risk.

## Path Rules

Supported path syntax examples:

- `definition`
- `workspaces[0].panels[0]`
- `definition.workspaces[0].panels[1].subPanels[0].reportlet`

See [`references/path-syntax.md`](references/path-syntax.md) for details and troubleshooting.

## CJA MCP Defaults

When the JSON appears to come from CJA MCP work, use these defaults unless the request clearly needs raw output:

1. Start with `summary` on the full file.
2. Move quickly to `projectBody.definition`, `segmentBody`, `audienceBody`, or `metricBody`.
3. Run `diff` with `--ignore-common-noise`.
4. Prefer `--cja-project-noise` for `upsertProject` envelope-vs-definition comparisons.
5. Add `--focus-path-prefix` for the exact panel, reportlet, or definition branch under review.
6. Use `--summary-only` first if the diff is large, then rerun without it on the most relevant branch.

Typical high-signal CJA questions:

- Did this `upsertProject` change only generated IDs, or did it alter panel behavior?
- Which `projectBody.definition.workspaces` branch changed between these two versions?
- Did the segment definition logic change, or only wrapper metadata?
- Which reportlet settings changed under one panel?
- Did date range, sort, metrics, or dimensions change in a meaningful way?

## Output Style

When reporting results, prefer this structure:

1. One-sentence summary of what changed
2. Small list of the most important changed paths
3. Any inferred risk or likely behavioral effect
4. Recommended next edit or verification step

Keep answers compact. Do not paste entire JSON blobs unless the user explicitly asks for them.
