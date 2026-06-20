# CLAUDE.md — Elite Dangerous Fleet & Engineering Project

> This file is project memory for Claude Code. It carries over the full history and
> context from the prior Claude project. Read it before doing any work.

---

## 0. Scope & Purpose

**Game:** Elite Dangerous: Odyssey on PC.

**Commander:** Tushar plays as **CMDR Ka0s** (Inara ID `173082`), based at **Ray Gateway** in the
**Diaguandri** system.

**Overarching project:** Build a comprehensive, role-specialized fleet with full engineering
across all ships, supported by an ecosystem of reference documentation, automation skills, and
tracking spreadsheets.

**Definition of success:** A fully engineered multi-role fleet, all 38 engineers unlocked, and a
rich personal knowledge base of field manuals covering ships, activities, and mechanics.

---

## 1. Working Principles (read these first)

- **Documentation-first.** Every major game activity gets a field-manual HTML dossier in the
  house style (see §7) before or alongside playing.
- **Accuracy over speed.** Tushar verifies facts and corrects errors. Fetch authoritative data
  (EDCD coriolis-data, EDEngineer GitHub, live web sources) rather than relying on memory.
  Acknowledge errors directly and fix them.
- **Iterative design.** Major deliverables (Blueprint.html, ship dossiers) go through explicit
  review-and-revise loops before being locked.
- **Proactive implementation.** Tushar prefers Claude to implement fixes and present results
  rather than asking permission at each step.
- **Skill-based automation.** Repetitive workflows are encapsulated as self-contained skills.
- **Data sourcing hierarchy:** Google Sheets Coriolis mirror → EDCD coriolis-data GitHub repo
  (ZIP via codeload endpoint) → web search fallback.
- **Spreadsheet workflow:** Google Sheets are the live source of truth. Download as xlsx, edit
  with openpyxl, deliver a new versioned file for manual re-import. Direct cell editing is not
  possible (read-only Drive integration).

---

## 2. Filesystem & Journal

**ED journal directory:**
```
D:\Profile\Users\Tushar\Saved Games\Frontier Developments\Elite Dangerous\
```

- Journal files are named `Journal.YYYY-MM-DDTHHMMSS.01.log`.
- Always copy the **two newest** logs (the newest may lack a `Materials` snapshot if it was
  started mid-session).
- For live held-material counts, always re-read the newest `Journal*.log` fresh.

---

## 3. Fleet Composition (identifier prefix `KA-`)

| Ship | ID | Role |
|---|---|---|
| Sidewinder Mk I | — | Insurance / taxi (fallback) |
| Viper Mk IV | KA-17V | Small PvE combat |
| Cobra Mk V | KA-05C | Small PvE multirole, small-pad access |
| Asp Explorer | KA-04A | Exploration & engineer-unlock workhorse |
| Mandalay | — | Planned Asp replacement, primary explorer |
| Lynx Highliner | KA-16M | Passenger liner (Robigo–Sirius loop) |
| Python Mk II | KA-05P | Medium PvE combat flagship |
| Type-9 Heavy | KA-05T | Bulk cargo hauler (ARX Jumpstart, pre-engineered) |
| Type-11 Prospector | KA-05L | Dedicated mining vessel |
| Federal Corvette | — | Long-term large combat goal (requires Rear Admiral rank) |

---

## 4. Engineering Goals — Core Blueprint Patterns

Target: **Full G5 engineering across the fleet.**

- **Power plant (combat):** G5 Overcharged + Thermal Spread.
- **Thrusters:** G5 Dirty Drive Tuning.
- **FSD:** G5 Increased Range + Mass Manager.
- **Power distributor:** Charge Enhanced + Cluster Capacitor (combat/mining); Engine Focused +
  Stripped Down (explorers/liners). *(Note: a "Lightweight" power distributor blueprint does not
  exist.)*
- **Shield generator:** Reinforced G5 + Thermo Block (combat); Enhanced Low Power (non-combat).
- **Multi-cannons:** G5 Overcharged with **one** Corrosive Shell per ship + Auto Loader on the
  remaining multi-cannons.
- **Beam lasers:** Efficient + Thermal Vent.

### Engineering sequencing
- Minimum-roll grades 1–4, optimize at G5.
- Experimental effects applied **last**, in a single in-person visit (cannot be applied remotely).
- Pinned blueprints enable Remote Workshop crafting from any station.

---

## 5. Engineer Unlock Run (38-engineer goal — in progress)

**Completed / in progress:**
- **Felicity Farseer** — maxed G5.
- **Tod McQuinn** — in progress (requires 100k CR bounty vouchers).
- **Elvira Martuuk** — invited, unlock not complete (needs 3× Soontill Relics).
- **Lei Cheung** — fully unlocked at Grade 1.
- **The Dweller** — was at Grade 1; needs sequential grade completion in person before G5 unlocks.
- **Marco Qwent** — requires Sirius Corp **Allied** reputation for permit. **NOT** via Li Yong-Rui
  Powerplay pledge (that perk was removed post-Powerplay 2.0).

**Notable upcoming prerequisites:**
- **Lori Jameson:** Dangerous combat rank + 25× Kongga Ale + Shinrarta permit (Phase 04).
- **Professor Palin:** 25× Sensor Fragments already collected.
- **Hera Tani:** requires Empire Outsider (rank 1).
- **Tiana Fortune:** requires Friendly reputation.
- **Imperial Navy rank:** working toward Achenar permit (requires Squire, rank 4).

**Reputation caution:** Do not over-invest Sirius Corp reputation — it will need lowering later
for Odyssey engineer unlocks.

---

## 6. Powerplay & Materials Status

**Powerplay:**
- Pledged to **Li Yong-Rui**; currently **Hostile** to Lavigny-Duval.
- Passenger missions earn **zero merits** under any Power.

**Materials:**
- All seven raw G4s previously capped and traded down; G5 manufactured target materials banked.
- **Selenium** has no crystalline shard farm — must trade at a Raw Material Trader.

---

## 7. Documentation House Style (LOCKED)

- Dark grid background.
- **Chakra Petch** and **Saira** fonts.
- Maroon–amber color palette.
- Radial gradient glows.
- HUD-style corner brackets.
- Numbered sections.
- Per-ship / per-role accent colors.
- Field manuals are **self-contained single-file HTML** with embedded CSS.

---

## 8. Live Documents — Source of Truth (Tushar's profile)

**Google Sheets:**
- Fleet Tracker — ID `1aHNCsxIQhdOtk1cfjn3Iinhc8MHift8N0_yXLho7jEY`
  https://docs.google.com/spreadsheets/d/1aHNCsxIQhdOtk1cfjn3Iinhc8MHift8N0_yXLho7jEY/edit
- Engineering Tracker — ID `1o67x9shillt8i-3t_FRlZNpq3-pdGKRcd63QYaZie04`
  https://docs.google.com/spreadsheets/d/1o67x9shillt8i-3t_FRlZNpq3-pdGKRcd63QYaZie04/edit
- Coriolis mirror sheet — ID `1mjn18y4dIfV8CW3lfDmImLmG-YMOpmWSzlzcT1FMsMU`

**Engineering Tracker tabs:** README, Checklist, Blueprint Climb, Blueprint Materials, Material
Inventory, Farm Guide, Engineers. (Material Inventory tracks all 147 materials with dated snapshot
columns; the Engineers tab lists all engineers in the game and is the source of truth for fleet
needs via its "Fleet need" column.)

**Third-Party Apps & Websites Directory:**
https://claude.ai/public/artifacts/6f62de5c-ec41-4c8d-82e6-69f998a44ac6

**Ship Field Manuals (published artifacts):**
- Sidewinder Mk I — https://claude.ai/public/artifacts/8098af01-8bca-4659-8c62-62587e17091f
- Viper Mk IV — https://claude.ai/public/artifacts/e6e8cd3d-b600-4f83-814a-94d601672caa
- Cobra Mk V — https://claude.ai/public/artifacts/daf9239d-e22f-4f9c-b240-5db3f71cd91c
- Asp Explorer — https://claude.ai/public/artifacts/addd5a27-2f42-4154-9489-d777659c2201
- Mandalay — https://claude.ai/public/artifacts/30ecf143-e5bb-4ca3-a894-edb2a19285ad
- Lynx Highliner — https://claude.ai/public/artifacts/a84efa9a-e98d-4351-a27f-bad05f5b907d
- Python Mk II — https://claude.ai/public/artifacts/bce81e3e-54af-4b7a-a146-d09f0232de7e
- Type-9 — https://claude.ai/public/artifacts/f6d7f7b7-594c-47a5-a012-aeeb769cafa2
- Type-11 — https://claude.ai/public/artifacts/e94fce4f-e63d-4a95-9deb-a32f4d9a72b2
- Federal Corvette — https://claude.ai/public/artifacts/9863dd3c-271a-42da-bfd4-a3b9e61ef041

**Material Farm Field Manuals:**
- HGE — https://claude.ai/public/artifacts/959f8e7c-10d5-42f2-ba0a-3c0abcf6c4bc
- Crystalline Shards — https://claude.ai/public/artifacts/d68a48c9-bc75-4ddd-8672-16206874fec1
- Dav's Hope — https://claude.ai/public/artifacts/b58509e4-6582-451c-bf56-1a255d213064
- Jameson Crash Site — https://claude.ai/public/artifacts/7ffb86bc-990d-4b9d-b94c-0623255b586a

---

## 9. Public Data Sources

- **EDCD coriolis-data** (ships, components, blueprint materials, engineers, experimentals):
  `https://github.com/EDCD/coriolis-data` — authoritative files: `modifications/blueprints.json`,
  `modules.json`, `specials.json`. Download ZIP via codeload:
  `https://codeload.github.com/EDCD/coriolis-data/zip/refs/heads/master`
  - Ship files use snake_case naming. Python Mk II = `python_nx`;
    Panther Clipper Mk II = `panther_clipper`; Caspian Explorer = `explorer_nx`.
- **EDCD FDevIDs** (FDev Companion API community data):
  `https://github.com/EDCD/FDevIDs/tree/master`
- **EDEngineer blueprints.json** (experimental effects — entries without a `Grade` key are
  experimentals; parse with `encoding='utf-8-sig'`):
  `raw.githubusercontent.com/msarilar/EDEngineer/...`

**Third-party tools in use:** EDSY (ship fitting), Inara (market/engineer data), EDSM
(navigation), Spansh (route planning), EDDiscovery (journal companion, SLEF exports),
EDEngineer (material tracking), Odyssey Materials Helper.

---

## 10. Current State / Next Deliverables

- **Blueprint.html dossier:** Design fully iterated and locked in `Blueprint_mockup_final3.html`.
  Full build scope ≈ **186 cards across ~81 distinct blueprints**. Data architecture confirmed:
  EDCD coriolis-data repo is the authoritative source. **The full Blueprint.html build is the next
  major deliverable.**
- **Engineering Tracker:** last delivered at **v30**.
- **Fleet Upgrade Excel:** versioned per the naming convention below.
- **Engineer unlock run:** actively in progress (see §5).

**On the horizon:**
- Complete the full Blueprint.html build using the locked design.
- Continue engineer unlock run through all 38 engineers.
- Federal Corvette acquisition (long-term; requires Federal Navy Rear Admiral rank).
- Potential System Colonisation project (suggested blueprint prioritizes Military economy,
  RES-capable rings, Asteroid Base, Tourism/Refinery layers).
- Self-hosting HTML field manuals (GitHub Pages recommended for stable, bookmarkable URLs).

---

## 11. Key Learnings & Principles (game mechanics)

- **ARX prebuilt rule:** Stock modules carry free rebuy until swapped. Removed stock modules sell
  for 0 CR and cannot be stored. Engineering stock modules *in place* does NOT void free rebuy —
  always engineer cores in place rather than replacing them.
- **Shield meta:** Resistance bonuses multiply with raw shield strength. Thermo Block beats Hi-Cap
  for combat ships against thermal-heavy NPC meta.
- **Multi-cannon loadout:** One Corrosive Shell per ship (debuffs armor for all weapons), Auto
  Loader on remaining multi-cannons (counteracts the Overcharged clip-size penalty).
- **Respawn mechanic:** Respawn occurs at the nearest rebuy-capable port to where the ship was
  destroyed, not the last docked station. Fleet carriers count as valid respawn points.
- **Soontill Relics** are cargo (carried in a cargo rack), not materials — same for other engineer
  unlock commodities (Meta Alloys, Landmines, Gold, etc.).
- **Coriolis/EDSY links:** Coriolis deep links cannot be reliably generated; EDSY links work for
  current builds. Coriolis is a client-side SPA — web fetch returns only the shell.
- **Material trader rates:** Down 1 grade = 1:3; up 1 grade = 6:1; category switch = ×6 penalty.
- **Dav's Hope:** Manufactured materials only (not raw).
- **Crystalline shards:** Have their own DSS filter (not "Biological"). Shard sites do not reset on
  mode-switch and take weeks to regenerate.
- **Selenium:** No crystalline shard farm; trade down from other capped G4s at a Raw Material
  Trader.
- **Marco Qwent / Sirius permit:** Powerplay 2.0 removed the Li Yong-Rui permit perk. Only route is
  grinding the Sirius Corporation minor faction to Allied.
- **G5 encoded materials:** Adaptive Encryptors Capture and Datamined Wake Exceptions have reliable
  direct farms; others best obtained via mission rewards.
- **Python Mk II internals:** Only 6 optional internal slots by design (dedicated medium combat
  platform); no military slots — HRP/MRP/SCB all compete in the same 6 bays.
- **Scoring consistency:** For role/ship rating tables, `ratings.csv` is the source of truth;
  scores are frozen once set and never recalculated.

---

## 12. Technical Notes / Tooling Gotchas

- **openpyxl:** Do NOT run LibreOffice formula recalculation — the sheet uses Google Sheets-native
  functions (`UNIQUE`, `SORT`, `SPLIT`) that LibreOffice corrupts. Use `data_only=True` for
  reading; omit it for writing to preserve formulas. After any `delete_cols`, rebuild data
  validations by column-header lookup (not hardcoded letters). `insert_rows` and `delete_cols` both
  strip hyperlinks and fail to shift merged cells and data-validation ranges — repair manually
  afterward.
- **Google Drive download (Claude.ai MCP):** `download_file_content` with
  `exportMimeType: application/vnd.openxmlformats-officedocument.spreadsheetml.format`. Result is
  double-nested: `json.loads(raw[0]['text'])` → `base64.b64decode(inner['content'])`. Read-only —
  cannot edit cells directly. *(In Claude Code, prefer downloading the xlsx locally and editing it
  with openpyxl.)*
- **EDDiscovery SLEF exports:** Include cosmetic/system slots that should be filtered out.
- **Inara (inara.cz):** Main profile pages load; subpages blocked by robots.txt. Rate-limits after
  ~5 blueprint fetches.
- **GitHub API (api.github.com):** Rate-limits quickly — use the raw codeload ZIP download instead.
- **Published artifact URLs:** Cannot be retrieved as raw HTML (claude.ai artifacts are
  client-side rendered). Save HTML locally at generation time for future retrieval.

---

## 13. Naming Conventions

- **Fleet Upgrade Excel:** `Fleet_Upgrade_v<N>.xlsx` — increment the version number for each new
  file.
- **Engineering Tracker Excel:** `Engineering_Tracker_v<N>.xlsx` — standalone sequential counter,
  independent of Fleet_Upgrade numbering. **Last delivered: v30.**

---

## 14. Skills / Automation

Skills are self-contained ZIP packages installed via Settings → Capabilities. (In Claude Code these
correspond to skill directories.)

- **`/ed-material-farm`** — Triggered by `/ed-material-farm`, "Dav's Hope SRV Loop Material Update,"
  or a loop-name update. Reads materials and Need values from the Engineering Tracker "Materials
  Farm" tab (Source col A, Material col B, Total col G); always re-reads the newest `Journal*.log`
  for live held counts. Renders inline via `show_widget` with green=collected / red=remaining bars.
  Not a spreadsheet output.
- **`/ed-material-update`** — Snapshots currently-held materials into the Engineering Tracker as a
  new timestamped column (header `YYYYMMDD-HHMMSS`, one count per material in the sheet's row
  order). Reads the newest journal fresh. Spreadsheet-logging task.
- **`/ed-ship-update`** — Triggered by `/ed-ship-update <SLEF>` or "convert this SLEF." Converts a
  SLEF JSON array to a tab-separated loadout table for the fleet Google Sheet. Self-contained —
  reads SLEF only (no journal/Drive access). Uses `slef_to_table.py` + bundled `data/` (coriolis
  ships.json, EDCD outfitting.csv, shipyard.csv). Output columns: Ship, Section, Slot, Class,
  Module, Engineering, Value (CR); all slots incl. empty; no meta rows; cosmetic slots filtered.
- **`ed-ship-field-manual`** — One ship in one role, 12 fixed sections, 1–100 suitability rating.
  Two mandatory params (ship, role); ask if either is missing.
- **`ed-role-field-manual`** — One role across every capable hull, grouped by pad class (S/M/L),
  nine fixed sections. One mandatory param (role); ask if missing.

### SLEF format reference
JSON array; each entry has a `header` (appName, appVersion) and a `data` block mirroring the
journal Loadout event. Required fields: `Ship` (internal type name) and `Modules[]` with `Slot` +
`Item` (internal symbols) plus `Engineering` when present. Always an array even for one ship.

---

## 15. Standing Instructions

- **No Artifact Index.** Do not maintain or reference an `ED_Artifact_Index_Dossier`. After
  creating a new field manual or dossier, do not prompt to publish-and-index, do not ask which
  index section it belongs in, and do not re-deliver any index file.

---

*End of CLAUDE.md*
