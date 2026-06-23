# audit-section-numbers.py

Read-only checker that verifies **section numbering is continuous** and the in-page
**quick-nav agrees with it**, across every guide.

## What it checks

For each `guides/**/*.html` (except `index.html`):

1. The ordered `<span class="sec-num">NN</span>` values are `1..N` — no gaps, no
   duplicates, and in standard 2-digit form (so a skipped `07`, or a non-standard
   `SEC 03`, fails).
2. Any numeric `<span class="qn-side">NN</span>` quick-nav side-numbers match the
   section numbers exactly (a quick-nav out of sync with its sections fails).

## Output / exit code

Prints each problem (`DISCONTINUOUS`, `NON-STANDARD sec-num`, `QUICK-NAV != SECTIONS`)
and exits **non-zero** if any are found, **zero** when clean. Good as a pre-commit gate
after editing section heads or the quick-nav on any page.

## Usage

```bash
python3 scripts/audit-section-numbers.py
```

Pair with `linkify-section-refs.py` — run this audit (and fix any numbering) **before**
linkifying `§` references, since the linker maps `§N` to the current section number.
