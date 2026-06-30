# link-checklist-engineers.py

Links engineer names in the **`checklist.html` step headers** — the one deliberate exception to
the "never link headers" rule (the engineer is the whole point of each unlock/climb step).

Scoped to `<h3 class="step-action">` headers inside `ac-unlock` / `ac-climb` step cards only
(NOT farm/build/grind cards, whose headers name locations like "Jameson Crash Site"). Two passes:
1. Expand a partial engineer surname to the full name ("Climb Farseer" → "Climb Felicity Farseer";
   "referrals to Qwent, Nemo" → "… Marco Qwent, Zacariah Nemo"). Skips a surname already preceded
   by its first name and one followed by another Capitalized word (a place).
2. Link each engineer full name (not already inside an `<a>`) to `engineers.html#engineer-<slug>`.

Idempotent. The Engineer Unlock Map nodes and the "What to do" prose are already linked and are
left alone; quick-nav is never touched. `engineer-<slug>` targets come from the link dictionary.

```bash
python3 scripts/link-checklist-engineers.py            # apply
python3 scripts/link-checklist-engineers.py --check    # report only
```
