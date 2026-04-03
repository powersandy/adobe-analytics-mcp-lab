# Path Syntax

Use dotted object keys plus zero-based array indexes in brackets.

## Examples

- `definition`
- `definition.version`
- `workspaces[0]`
- `workspaces[0].panels[1].subPanels[0]`
- `items[3].component.id`

## Rules

- Start from the JSON root.
- Separate object keys with `.`.
- Use `[index]` for array access.
- Combine both forms as needed: `panels[0].subPanels[2].reportlet`.
- Keys containing literal dots are not specially escaped in this helper. If a file uses keys like `a.b`, inspect the parent object first and handle that subtree manually.

## Recommended workflow

1. Run `summary` on the full file.
2. Identify the smallest relevant branch.
3. Run `extract` on that branch.
4. Use the same path in `diff`, or different paths with `--path-a` and `--path-b`.

## Common mistakes

- Using one-based indexes instead of zero-based indexes
- Forgetting brackets for arrays
- Comparing entire files when only one subtree matters
- Treating key order as a semantic change
