# apply-title-blocks.py

Apply the reviewed, standardized title blocks to the guide pages from the workbook
export. Phase 2 of the title-block standardization task.

## Run
```bash
python3 scripts/apply-title-blocks.py --dry-run          # preview every page
python3 scripts/apply-title-blocks.py                    # apply to all changed pages
python3 scripts/apply-title-blocks.py --files guides/systems/powerplay.html ...  # one batch
```

## Input
`scripts/out/edited-rows.json` — produced from the reviewed `title-blocks.xlsx`
(`{file, group, cur:{…}, new:{…}}` per page). The `new:*` cells are the targets.

## What it does
**Element-targeted and idempotent.** For each page it rewrites ONLY the masthead
elements whose target differs from what's live, so anything the workbook doesn't model
(e.g. an h1 with middle text the user didn't touch) is preserved verbatim:

- **`<title>`** ← `"<page_name> &middot; <title_suffix> | E:D Black Box"` (no suffix → `"<name> | E:D Black Box"`).
- **`.kicker`** ← `"<kicker_a> <span class="sep">//</span> <kicker_b>"`.
- **`h1.title`** ← rebuilt from `h1_lead`/`h1_accent`/`h1_role` **only when a user-modelled
  h1 field changed**; the existing accent→role spacing is preserved. Otherwise left as-is.
- **`p.subtitle`** removed when the target subtitle is blank (the masthead carries none).
- **`.masthead-meta`** ← exactly two spans, `"<label>"` + `"Updated <b>YYYY-MM-DD</b>"`,
  collapsing any bespoke 3–4-span metas.

### Built-in corrections
- **Dates** normalized to the site's ISO `YYYY-MM-DD` (Excel exports `M/D/YYYY`).
- **`checklist.html`** "Unlock Chestlist" typo → "Unlock Checklist".
- **Bare ampersands** in inserted text escaped to `&amp;` (real entities preserved).
- **Meta keyword bolded** house-style: `Series Ships` → `Series <b>Ships</b>` (labels that
  already carry their own `<b>`, like the index count, pass through).

Verify the result with `verify-title-blocks.py`. Re-running is safe (no-op once applied).
