# restructure-app-cards.mjs — simplify the third-party-apps tool cards

One-shot restructure of the tool cards in `guides/systems/third-party-apps.html`. Per
`<article class="card …">`:

- drops the per-domain accent (`ac-fed`/`ac-good`/`ac-maroon` → plain `.card`, amber default);
- adds a stable bookmark `id="app-<slug>"` (slug from the `<h3>` title, de-duplicated);
- removes the decorative `.c-eyebrow` ("inara.cz · Web · …");
- moves the `.pill` tag onto its own `.card-tags` row under the title;
- converts the trailing "Open ▸" link into a right-after-title `.cb-ext` ↗ glyph
  (defunct "Closed ▸" cards get no glyph).

## Usage
```bash
node scripts/restructure-app-cards.mjs <abs-html-path>
```
Prints the count restructured and any cards whose `.c-head` didn't match the expected
shape. Single-purpose (this page's card vocabulary); not a general migration tool. The
section-18 in-prose links to these card ids and the removal of the Sources section were
done separately.
