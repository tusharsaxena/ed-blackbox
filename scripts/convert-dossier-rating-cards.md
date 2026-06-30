# convert-dossier-rating-cards.sh

One-off migration that converts every ship dossier's **briefing rating card** from the
dial *wheel* form to the *number + ladder-bar* form.

```
FROM  <div class="stat rating"><div class="dial" style="--v:NN"><div class="num">NN<small>/100</small></div></div><div class="l">… suitability</div></div>
TO    <div class="stat"><div class="n">NN<small>/100</small></div><div class="bar mini"><i style="--pct:NN"></i></div></div>
```

- Operates on `guides/ships/dossiers/*.html`.
- `NN` (the ship's 0–100 rating) is preserved for both the number and the bar fill.
- The rating card drops the `rating` class and the "… suitability" text label; the
  `.bar.mini` ladder bar becomes the second row (its colour auto-derives from `--pct`).
- **Idempotent** — only matches cards still in the wheel form, so re-running does nothing.

## Run

```bash
bash scripts/convert-dossier-rating-cards.sh   # prints "rating cards converted: N / 77 dossiers"
```

## Related

The matching CSS lives in `design-system/css/ed-blackbox.css` (`.stat`, `.stat .n small`,
`.stat .bar.mini`). The amber briefing box + compact equal-height stat cards were part of
the same masthead/briefing standardization pass.
