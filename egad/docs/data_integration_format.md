# Data integration format

How a dataset is registered into the data lake. Promotion is **user-gated** — never register a
dataset without asking first. Default is to leave data in `${CIIM_TEMP_DIR}/{task}/raw_data/`.

## When to promote

All three must hold:
- **Stable identity** — a resolvable accession, DOI, or versioned URL.
- **Task-independent** — the source dataset, not this task's filtered subset.
- **Costly to redo** — >1 h compute or >5 GB transfer.

Processed data adds a fourth: a reproduction script sits next to it. Processed data without a
recipe is not registered.

## Before downloading

Grep `docs/datalake.md` for the accession. Already there → reuse the registered path, do not
re-download.

## 1. `${CIIM_DATALAKE_DIR}/{name}/`

Where the files land. Processed derivatives of a registered dataset go in
`${CIIM_DATALAKE_DIR}/{name}/processed/{recipe}/` together with the script that produced them.

## 2. `datalake_docs/{name}/list.md`

One `## {filename}` block per file, with a one-line description derived from the source docs,
readme, or a quick `head`/`zcat | head`. See `datalake_docs/dice/list.md` for the format.

## 3. `docs/datalake.md`

Insert a `## {name}` section in alphabetical order (update in place if it exists):

```
## {name} — {pretty name}
#tag #tag #tag
source: {accession or URL}
added: {YYYY-MM-DD} (task: {task})
→ [`datalake_docs/{name}/list.md`](datalake_docs/{name}/list.md)
```

Tags are the search surface — cover assay, cohort type, condition, and species-level scope.
