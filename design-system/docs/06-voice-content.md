# 06 · Voice & content

## Voice

Operator-grade field manual. Write like a veteran commander briefing another:
terse, technical, confident, useful. State the call, then the reason.

- **No marketing.** No hype, no exclamation, no emoji, no "amazing/ultimate/game-changing".
- **Lead with the verdict.** Say the recommendation or the headline fact first, then
  justify. The `.verdict` box is the page's thesis in one or two sentences.
- **Concrete over vague.** Numbers, system names, module grades, credit figures —
  specifics, not adjectives.
- **Second person, present tense.** "You fit four large multi-cannons…", "Dock at…".
- **Brevity.** Leads are 1–2 sentences. Card/cell copy is one line where possible.
- **Bold sparingly** — only the single key phrase in a sentence (`<b>`), not whole
  clauses. Use `.acc` for inline accent emphasis.

## Identity & attribution

- The brand is **E:D Black Box** — shown as the logo + wordmark in the global
  `.site-header`. The masthead kicker carries **no** commander/INARA id.
- Author credit is **`By CMDR Ka0s`** in the footer only.
- `.masthead-meta` carries the series part and a **last-updated** date (`Updated
  YYYY-MM-DD`). No sources line and no patch-version line in the masthead. Per-page data
  lineage is verified per `01-principles.md` and listed in the bottom-of-page
  **`section.credits`** (Sources) block.

## Content format conventions

- **Credits:** thousands separators, `CR` suffix — `38,500,000 CR`. Use `~` for
  approximate all-in costs — `~80M all-in`.
- **Distances / speeds / mass:** unit in a `<small>` inside the value — `256 / 345
  <small>m/s</small>`, `19.4 <small>ly</small>`, `450 <small>t</small>`.
- **Ratings:** 1–100, shown as `NN<small>/100</small>` in dials, bare `NN` in table
  `.rscore`/`.score`. Scores come from `ratings.csv`; don't recompute set scores.
- **Module grades:** game notation — `5A`, `Pulse Laser 3`, `MC 3 — Overcharged +
  Corrosive`. Use an em dash between a module and its engineering.
- **Hardpoints/pads:** `4 Large · 2 Medium`, pad `S/M/L`. Use the middot `·` as the
  inline separator; `//` as the masthead kicker separator.
- **Unknowns:** `.kv-tbd` with text like "unconfirmed" — never a guessed number.
- **Section tags** (`.sec-head .tag`): a short count or category — `SHIP-SIDE · 6`,
  `Tabular`, `Legend`, `Displays`.
- **Numbering:** sections zero-padded `01, 02 …`; the rank column in ladders likewise.

## Titles & headings

- `h1.title`: the subject, with exactly one word wrapped in `<span>` (gold). Optional
  `<span class="role">` suffix names the role for ship × role dossiers.
- Section `h2`: short, uppercase by CSS — write in normal case, the style uppercases it.
- Keep a consistent series label in the kicker across a family of manuals (e.g.
  "Field Manual // Ship × Role Dossier // <manufacturer>").
