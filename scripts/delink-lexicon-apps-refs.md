# delink-lexicon-apps-refs.py

Trims redundant/noisy auto-applied cross-links on two reference pages where they add noise
rather than value. **Byte-preserving** otherwise.

## What it does

**1. `guides/systems/cmdrs-lexicon.html`**
- **Term column** — every first cell is `<td class="mod">` and the abbreviation/term itself
  was hyperlinked. Unwrap **all** links in those cells (keep the text); the Meaning column
  carries the useful links.
- **Ship-name links in the Meaning column** — ship rows read
  `<b><a …dossiers…>Asp Explorer</a></b> — desc. <a …dossiers…>Dossier</a>.` The bold
  ship-name link duplicates the trailing "Dossier" link, so unwrap the ship-name link (keep
  `<b>…</b>` + the Dossier link). Only dossier links are touched; module/blueprint bold links
  in other tables are left alone.

**2. `guides/systems/third-party-apps.html`**
- App cards carry a deliberate **external** link to the resource (`<a class="cb-ext">` ↗ in
  the `<h3>`). The card free-text had game-concept/app cross-links (Fuel Scoop, ship dossiers,
  `#app-…` anchors) auto-applied. Unwrap every **internal** link inside each
  `<article class="card">` block (relative or `#anchor`); keep the external `cb-ext` link and
  any other `http(s)` link.

## Usage

```bash
python3 scripts/delink-lexicon-apps-refs.py
```

No flags. **Idempotent** — re-running on already-trimmed pages writes nothing. Prints a
per-page summary of links unwrapped.

> Note: both pages are link **sources** for `apply-hyperlinks.py`, so a future pass could
> re-add internal links; mark elements `class="nolink"` if that recurs.
