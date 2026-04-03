# CJA `upsertProject` - pre-upsert checklist

**Use:** Final yes/no pass immediately before `upsertProject`.
**Not:** A full spec. See `projectSchema_v96.json`, `Project Definition Guidev96.pdf`, and [REFERENCE_DIGEST.md](REFERENCE_DIGEST.md) for navigation and rules.

When `definition.version` moves beyond **96**, refresh those files and this list together.

---

## Checks

- [ ] `definition.version` matches the bundled schema you validated against (`96` for this folder).
- [ ] No mixing of patterns from another definition version. In v96, freeform rows use `dimensionSettings`, not legacy `dimension`-only row config.
- [ ] `TextReportlet` and subpanel `description` rich text fields use stringified Quill Delta, not plain prose.
- [ ] Date range shape matches intent: preset entity vs inline `__metaData__.definition` vs fixed ISO span.
- [ ] Panels, subpanels, and reportlets have content-aware names, not only generic labels like `Freeform Table` when the analysis is known.
- [ ] Copied subtrees from `describeProject`, exports, or MCP docs are minimal and re-checked against `projectSchema_v96.json`.
- [ ] Any copied component IDs were revalidated in the destination data view or org context.
- [ ] No preflight payload-size probe was used. The first `upsertProject` attempt is the real intended payload.
- [ ] If a clear size-related failure happened, payload reduction used meaningful branches such as panels, subpanels, or reportlets rather than random edits.
- [ ] If size retries were needed, they stayed within a reasonable ceiling and any removed scope is ready to be explained to the user.
- [ ] No direct API fallback was used without explicit user approval.
- [ ] If a smoke or test project was created for this task, it is replaced in place or removed so orphan temp projects do not accumulate.
- [ ] Compact metric-summary widgets are either standard freeform tables with real rows or a known-good `KeyMetricSummaryReportlet` pattern.
- [ ] If this is an update, the target `projectId` is clearly the intended one and not just a similar project discovered during exploration.

---

## If Something Breaks After Upsert

- Compare to a known-good project at the same `definition.version` and copy only the smallest missing subtree.
- Re-check the component shape in `projectSchema_v96.json` first, then the PDF troubleshooting section.
- Classify the failure before retrying: schema, invalid ID, clear size-related failure, or blocked auth/tooling.
