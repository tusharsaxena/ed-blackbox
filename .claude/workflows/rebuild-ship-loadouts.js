export const meta = {
  name: 'rebuild-ship-loadouts',
  description: 'Author SLEF loadout data for all 127 ship dossiers, build their tables, adversarially verify, and fix flagged ones',
  phases: [
    { title: 'Author', detail: 'one agent per dossier: author 3-build SLEF + run generator + self-verify' },
    { title: 'Verify', detail: 'adversarial check of each built dossier vs hull/module data + role fit' },
    { title: 'Fix', detail: 'repair dossiers the verifier flagged' },
  ],
}

const ROOT = '/mnt/d/Profile/Users/Tushar/Documents/GIT/ed-blackbox'
let WORK = args
if (typeof WORK === 'string') WORK = JSON.parse(WORK)
if (!Array.isArray(WORK)) throw new Error('args is not an array: got ' + typeof WORK)

const AUTHOR_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    basename: { type: 'string' },
    built: { type: 'boolean', description: 'true if generator reported built/ok with 0 errors' },
    generatorResult: { type: 'string', description: 'the generator summary line + any warnings' },
    corrections: { type: 'array', items: { type: 'string' }, description: 'errors fixed vs the existing dossier (old -> new + why)' },
    uncertain: { type: 'array', items: { type: 'string' }, description: 'cells where you made a judgement call' },
  },
  required: ['basename', 'built', 'generatorResult'],
}
const VERIFY_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    ok: { type: 'boolean', description: 'true if the built loadout is accurate, valid, and role-appropriate' },
    issues: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          severity: { type: 'string', enum: ['fatal', 'major', 'minor'] },
          detail: { type: 'string' },
        },
        required: ['severity', 'detail'],
      },
    },
  },
  required: ['ok', 'issues'],
}

const RULES = `
SLEF DATA FORMAT (data/ship-loadouts/<basename>.json) — study the GOLD reference
${ROOT}/data/ship-loadouts/federal-corvette-combat.json and the guide
${ROOT}/scripts/build-ship-loadouts.md BEFORE writing anything.
- The file is a JSON ARRAY of THREE SLEF builds, each {header:{appName,appVersion,appURL,appCustomProperties:{state}}, data:{Ship, Modules:[...]}}.
  state is "initial" (cheapest buy-only — only list fitted slots), "arated" (A-rated, no engineering), "engineered" (A-rated modules + Engineering blocks).
- The ENGINEERED build must list ALL the same modules as A-Rated (so it is a complete importable build), adding an "Engineering":{BlueprintName,Level,Quality,ExperimentalEffect} block ONLY where engineered.
- Editorial layer goes in the ENGINEERED build's header.appCustomProperties.edbb = {role, intro, callout:{label,text}, notes:{<Slot>:"why"}, engineeringPlan:[{module,size,grade,blueprint,experimental,engineer}]}.
  notes are keyed by the SLEF Slot name; one terse sentence per fitted slot on WHY that A-Rated + engineering choice. intro/callout/notes are PLAIN TEXT (use literal — and &, NOT entities).

SLOT NAMES (must be exact so they resolve + sort): hardpoints HugeHardpoint1.., LargeHardpoint1.., MediumHardpoint1.., SmallHardpoint1..; utilities TinyHardpoint1..N; cores PowerPlant, MainEngines (thrusters), FrameShiftDrive, LifeSupport, PowerDistributor, Radar (sensors), FuelTank; military Military01..; optional internals Slot01_Size<N>, Slot02_Size<N>, ... numbered in DESCENDING size order with <N> = that slot's size (e.g. Slot01_Size7). Use only as many hardpoint/utility/optional slots as the hull actually has.

ITEM SYMBOLS: every module's "Item" is an FDev symbol. DO NOT guess them — look each up:
  python3 ${ROOT}/scripts/slef_resolve.py find <modulefile> <size> <rating> <mount>
  e.g. \`find multi_cannon 4 A G\` -> hpt_multicannon_gimbal_huge. <modulefile> is the data/modules/**/*.json basename (multi_cannon, beam_laser, shield_generator, bi_weave_shield_generator, hull_reinforcement_package, shield_cell_bank, power_plant, thrusters, frame_shift_drive, life_support, power_distributor, sensors, fuel_tank, shield_booster, chaff_launcher, heat_sink_launcher, point_defence, fighter_hangar, surface_scanner, fuel_scoop, cargo_rack, auto_field_maintenance_unit, guardian_fsd_booster, planetary_vehicle_hanger, module_reinforcement_package, ...). mount is F/G/T for weapons, omit for the rest.
  Blueprint fdname + experimental edname: look up with \`slef_resolve.py bp <fdname>\` and \`slef_resolve.py special <edname>\`, and grep data/modifications/blueprints.json / specials.json. ONLY use blueprints that exist for that module type (e.g. shield GENERATORS have Reinforced/Optimised/Kinetic/Thermic — NOT "Resistance Augmented", which is a shield BOOSTER blueprint). Engineering.Level is the grade (1-5), Quality 1.0.

ENGINEERED CELL RULES (the generator enforces the display; you control the data):
- Assign a blueprint AND an experimental wherever one exists for that module. If a blueprint has no experimental you want, the cell will read "(no experimental effect)".
- If a fitted module has NO engineering blueprint at all (chaff, heat sink, point defence, SCB, MRP, fighter hangar, fuel tank, scanners, limpet controllers, fuel scoop), omit its Engineering block -> renders "(No blueprint available)". Do NOT invent blueprints for these.
- RECONCILIATION: a module may only be engineered if it is fitted in the A-Rated build. Never put a blueprint on a slot that is empty in A-Rated.
- HRP and MRP cap at size 5; if a slot is larger, a size-5 module under-fills it (that is correct). Shield generators / SCB / cargo racks go up to 8. Fighter hangars are 5-7. Verify sizes exist before assigning.

ACCURACY (rule 1): the loadout must be ship x role SPECIFIC and game-accurate. Start from the existing dossier's curated picks (read its section-3-state-loadout + section-engineering-plan tables + the intro <p> + trailing callout), enrich every cell with size+rating, validate against EDCD coriolis-data in data/, and CORRECT anything wrong (note each correction). Keep the editorial intent/voice (initial = cheapest buy-only, A-Rated = role-ready, Engineered = full pattern); preserve the intro/callout wording (lightly fix factual errors).
`

function rolesHint(basename) {
  if (basename.endsWith('-combat')) return 'COMBAT: weapons + shields/hull tank; A-rate distributor/plant/thrusters; engineer weapons (Overcharged/Efficient + experimentals), shields, hull.'
  if (basename.endsWith('-ax')) return 'ANTI-XENO: AX/Guardian weapons (ax_multi_cannon, guardian_gauss_cannon, guardian_plasma_charger, guardian_shard_cannon), caustic sink, heavy thermal/caustic resist; module/hull reinforcement; Guardian FSD booster optional.'
  if (basename.endsWith('-exploration')) return 'EXPLORATION: max jump range (A-rated FSD + Guardian FSD Booster, lightweight everything), Fuel Scoop, Detailed Surface Scanner, AFMU, heat sinks; minimal/no weapons; shields light/optional. Engineer = Lightweight + Increased Range.'
  if (basename.endsWith('-mining')) return 'MINING: mining lasers / abrasion blaster / sub-surface displacement missile / seismic charge, prospector + collector limpet controllers, refinery, cargo racks, Detailed Surface Scanner, decent shields.'
  if (basename.endsWith('-trading')) return 'TRADING: maximise cargo racks, A-rated FSD for range, enough shielding/defence to survive; no weapons or token defence only.'
  if (basename.endsWith('-passenger')) return 'PASSENGER: passenger cabins (economy/business/first/luxury per ship class), A-rated FSD, shields, some cargo; comfortable range.'
  return 'MULTIPURPOSE: a balanced jack-of-all-trades fit — moderate weapons, shields, cargo, and jump range; swappable optionals.'
}

function authorPrompt(w) {
  return `You are authoring the canonical SLEF loadout data file for ONE Elite Dangerous dossier in the repo at ${ROOT}.

TARGET: data/ship-loadouts/${w.basename}.json  (ship x role: ${w.basename})
HULL DATA: ${w.hasJson ? `data/ships/${w.hull}.json (key inside; slots.standard order = Power Plant, Thrusters, Frame Shift Drive, Life Support, Power Distributor, Sensors, Fuel Tank; slots.hardpoints + slots.internal give sizes; dict entries are Military/special slots)` : `NONE EXISTS for this hull — derive slot sizes from the existing dossier's stated sizes and coriolis.io; the generator will skip hull-size validation.`}
EXISTING DOSSIER (baseline + editorial source): guides/ships/dossiers/${w.basename}.html

${rolesHint(w.basename)}

${RULES}

STEPS:
1. Read the GOLD reference JSON, build-ship-loadouts.md, slef_resolve.md.
2. Read the existing dossier's section-3-state-loadout (intro <p>, table rows, trailing callout) and section-engineering-plan tables — this is your baseline.
3. ${w.hasJson ? `Read data/ships/${w.hull}.json for the exact slot layout (how many hardpoints/utilities/optionals and their sizes).` : `Determine the slot layout from the existing dossier + coriolis.io.`}
4. Build the three SLEF builds, looking up EVERY Item symbol with slef_resolve.py find. Put editorial (intro, callout, per-slot notes, engineeringPlan) in the engineered build's appCustomProperties.edbb.
5. Write data/ship-loadouts/${w.basename}.json (valid JSON array of 3 builds).
6. Run: cd ${ROOT} && python3 scripts/build-ship-loadouts.py ${w.basename}
   It MUST report "built" (or "ok") with 0 warnings and 0 errors. Fix any warning:
   - "unresolved Item" -> wrong symbol, re-run slef_resolve.py find.
   - "item size != hull size" -> wrong size for that core slot.
   - "blueprint but slot empty in A-Rated" -> reconciliation violation.
7. Re-read the rendered section-3-state-loadout to confirm it looks right.

Return the AUTHOR_SCHEMA object: basename, built (true only if 0 errors), generatorResult (the summary line + any remaining warnings), corrections (old -> new + why, vs the existing dossier), uncertain (judgement calls).`
}

function verifyPrompt(w) {
  return `Adversarially verify the just-built SLEF loadout for ${w.basename} in the repo at ${ROOT}. Assume it is wrong until proven right.

CHECK:
1. data/ship-loadouts/${w.basename}.json parses as a SLEF array of 3 builds (states initial/arated/engineered) and \`cd ${ROOT} && python3 scripts/build-ship-loadouts.py --check ${w.basename}\` reports 0 warnings / 0 errors.
2. Read the rendered section-3-state-loadout in guides/ships/dossiers/${w.basename}.html. For a sample of rows, confirm each Item resolves to the displayed size+rating (spot-check with \`python3 scripts/slef_resolve.py item <symbol>\`), and that slot sizes are valid for the hull${w.hasJson ? ` (data/ships/${w.hull}.json)` : ''}.
3. Engineering validity: every engineered cell uses a blueprint that EXISTS for that module type (e.g. no "Resistance Augmented" on a shield generator); experimentals are assigned where they exist; "(No blueprint available)" only on truly un-engineerable modules; no blueprint on a slot empty in A-Rated; HRP/MRP not assigned above size 5.
4. Role fit: the loadout makes sense for ${w.basename.split('-').pop()} (weapons for combat/ax, cargo for trading, scoop+range for exploration, limpets+lasers for mining, cabins for passenger). Flag obviously wrong picks.
5. Notes column present and sensible; intro/callout intact.

Return VERIFY_SCHEMA: ok (true only if accurate, valid, role-appropriate — minor wording nits don't fail it), and issues[] (severity fatal/major/minor + detail). Be specific and terse.`
}

function fixPrompt(w, issues) {
  return `Fix the SLEF loadout data file data/ship-loadouts/${w.basename}.json in the repo at ${ROOT}. A verifier flagged these issues:

${issues.map((i, n) => `${n + 1}. [${i.severity}] ${i.detail}`).join('\n')}

${RULES}

Read the current data/ship-loadouts/${w.basename}.json and the gold reference, address EVERY flagged issue, re-write the file, then run \`cd ${ROOT} && python3 scripts/build-ship-loadouts.py ${w.basename}\` until it reports 0 warnings / 0 errors and the issues are resolved. Look up any corrected symbols with slef_resolve.py. Return AUTHOR_SCHEMA: basename, built, generatorResult, corrections (what you changed), uncertain.`
}

log(`Authoring + verifying ${WORK.length} ship dossiers as SLEF (gold reference: federal-corvette-combat)...`)

const results = await pipeline(
  WORK,
  (w) => agent(authorPrompt(w), { label: `author:${w.basename}`, phase: 'Author', schema: AUTHOR_SCHEMA, agentType: 'general-purpose' }),
  (author, w) => {
    if (!author) return { basename: w.basename, ok: false, issues: [{ severity: 'fatal', detail: 'author agent returned null' }], author: null }
    return agent(verifyPrompt(w), { label: `verify:${w.basename}`, phase: 'Verify', schema: VERIFY_SCHEMA, agentType: 'general-purpose', effort: 'low' })
      .then((v) => ({ basename: w.basename, author, ok: v ? v.ok : false, issues: v ? v.issues : [{ severity: 'fatal', detail: 'verify agent returned null' }] }))
  }
)

const done = results.filter(Boolean)
const buildFailed = done.filter((r) => !r.author || !r.author.built)
const needsFix = done.filter((r) => (r.author && r.author.built) && (r.ok === false || (r.issues || []).some((i) => i.severity === 'fatal' || i.severity === 'major')))

log(`Author+verify complete: ${done.length} processed, ${buildFailed.length} build-failed, ${needsFix.length} flagged for fix.`)

let fixed = []
if (needsFix.length) {
  fixed = await parallel(needsFix.map((r) => () => {
    const w = WORK.find((x) => x.basename === r.basename)
    return agent(fixPrompt(w, r.issues || []), { label: `fix:${r.basename}`, phase: 'Fix', schema: AUTHOR_SCHEMA, agentType: 'general-purpose' })
  }))
}

return {
  total: WORK.length,
  built: done.filter((r) => r.author && r.author.built).length,
  verifiedClean: done.filter((r) => r.ok === true).length,
  buildFailed: buildFailed.map((r) => r.basename),
  flaggedForFix: needsFix.map((r) => ({ basename: r.basename, issues: r.issues })),
  fixed: fixed.filter(Boolean).map((f) => ({ basename: f.basename, built: f.built, corrections: f.corrections })),
  allCorrections: done.filter((r) => r.author && (r.author.corrections || []).length).map((r) => ({ basename: r.basename, corrections: r.author.corrections })),
}
