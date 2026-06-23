# add-ship-render.py

Drops a framed **ship render** into each dossier's briefing box — the "Concept A"
placement: the hull image rides at the right of the `.verdict`, with the stat strip
spanning full width beneath it.

## What it does

For every dossier in `guides/ships/dossiers/`:

1. **Derives the render** from the dossier slug — strips the role suffix
   (`-combat`, `-exploration`, `-multipurpose`, `-ax`, `-trading`, `-mining`,
   `-passenger`) and collapses `mk-<roman>` → `mk<roman>` to match the image filenames
   (`cobra-mk-iii` → `cobra-mkiii.jpg`). A dossier whose render is **not** present in
   `images/ships/` is **skipped** (and listed).
2. **Builds the caption** as `<b>Display Name</b> &middot; Manufacturer` — display name
   from `scripts/ship-names.tsv` (keyed by hull slug), manufacturer parsed from the
   page's own kicker (`… // <Manufacturer>`).
3. **Rewrites the briefing**: wraps the eyebrow/heading/copy in `.v-body`, inserts the
   `<figure class="ship-figure">` before the `.stat-grid`, and adds `has-render` to the
   `.verdict`.

The image path written is `../../../images/ships/<render>.jpg` (relative to the dossier),
with `alt` = display name and intrinsic `width="160" height="90"`.

The matching component CSS lives in **`design-system/css/ed-blackbox.css`**
(`.ship-figure` and `.verdict.has-render`, shown at the renders' native 160px to stay
pixel-sharp, and collapsing to a single column below 760px).

**Idempotent:** a dossier already carrying `verdict has-render` (or a `.ship-figure`) is
left untouched — safe to re-run after a missing render is added to `images/ships/`.

## Usage

```bash
python3 scripts/add-ship-render.py            # edit all dossiers in place
python3 scripts/add-ship-render.py --check     # report what WOULD change, write nothing
```

Paths resolve relative to the script, so it runs from anywhere. On completion it prints a
summary: dossiers changed, already done, and any skipped for a missing render.

## Coverage (at authoring time)

77 dossiers · **76 get a render** · **1 skipped** (`cobra-mk-iv-multipurpose` — no
`cobra-mkiv.jpg` render exists yet). Add that render to `images/ships/` and re-run to fill
it in. All 46 ship renders are referenced; none unused.
