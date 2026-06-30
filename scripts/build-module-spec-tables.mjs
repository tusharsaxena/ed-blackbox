// scripts/build-module-spec-tables.mjs — rebuild every module spec table on
// guides/engineering/modules.html FROM the locally-imported EDCD/coriolis-data
// dataset under data/modules/{standard,internal,hardpoints}/*.json.
//
// Source of truth is LOCAL JSON (no web scraping). Each coriolis file is shaped
// { "<grp>": [ rowObjects ] }; every row carries at least class, rating, cost,
// mass, integrity + module-specific stats. Most modules also have `power` (power
// DRAW in MW); power plants & generators expose pgen/eff instead of a draw.
//
// For each of the 33 stable .bp-card ids on the page, this generator:
//   1. STRIPS any existing spec block(s): the <p class="spec-label"> labels and
//      <div class="spec-wrap"> tables a prior build appended, plus any leftover
//      ">Availability<" / ">Core stats<" .bp-panel cells (and now-empty .bp-ctx).
//   2. MOVES every <div class="callout">…</div> to the END of the panel region
//      (callouts last-before-table).
//   3. APPENDS one Concept-D class-grouped + fade-reveal table per mapped coriolis
//      file (family cards get a <p class="spec-label"><b>Variant</b></p> first).
//
// Columns per table (strict order): Class, Rating, [Mass, Integrity, Power draw],
// up to 5 module-relevant stats, then Value (CR) last (thousands-separated). The
// Concept-D <style> (now incl. a 2-line th clamp) + the .spec-pill JS are injected
// once. Pure string/regex transforms anchored on stable card ids — no DOM lib.
//
// IDEMPOTENT: strips existing spec blocks first, then regenerates, so re-running
// reproduces byte-identical output. Prints a sanity count (cards built / columns
// per card). Node only, no deps. Usage: node scripts/build-module-spec-tables.mjs

import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const DATA_DIR = join(ROOT, 'data', 'modules');
const HTML = join(ROOT, 'guides', 'engineering', 'modules.html');

const SPEC_STYLE_MARKER = '/* concept-D spec tables */';

// ---------------------------------------------------------------------------
// CARD → coriolis file MAP. A family card lists [variant-label, file] pairs in
// render order; a plain card lists a single [null, file].
// ---------------------------------------------------------------------------
// NOTE: keys are the live HTML `.bp-card` ids (module-* scheme, standardized
// 2026-06-24). A family card lists [variant-label, file] pairs in render order;
// a plain card lists a single [null, file].
const CARD_MAP = {
  'module-power-plant':            [[null, 'standard/power_plant']],
  'module-thrusters':             [[null, 'standard/thrusters']],
  'module-frame-shift-drive':     [[null, 'standard/frame_shift_drive']],
  'module-life-support':          [[null, 'standard/life_support']],
  'module-power-distributor':     [[null, 'standard/power_distributor']],
  'module-sensors':               [[null, 'standard/sensors']],
  'module-fuel-tank':             [[null, 'standard/fuel_tank']],
  'module-shield-generator':      [['Standard', 'internal/shield_generator'],
                                ['Bi-Weave', 'internal/bi_weave_shield_generator'],
                                ['Prismatic', 'internal/pristmatic_shield_generator']],
  'module-shield-cell-bank':      [[null, 'internal/shield_cell_bank']],
  'module-hull-reinforcement':    [[null, 'internal/hull_reinforcement_package']],
  'module-module-reinforcement':  [[null, 'internal/module_reinforcement_package']],
  'module-guardian-reinforcement':[['Guardian Hull', 'internal/guardian_hull_reinforcement_package'],
                                ['Guardian Module', 'internal/guardian_module_reinforcement_package'],
                                ['Guardian Shield', 'internal/guardian_shield_reinforcement_package'],
                                ['Meta-Alloy Hull', 'internal/meta_alloy_hull_reinforcement_package']],
  'module-guardian-fsd-booster':  [[null, 'internal/guardian_fsd_booster']],
  'module-fuel-scoop':            [[null, 'internal/fuel_scoop']],
  'module-detailed-surface-scanner': [[null, 'internal/surface_scanner']],
  'module-cargo-rack':            [['Standard', 'internal/cargo_rack'],
                                ['Mk II (Lightweight)', 'internal/cargo_rack_large']],
  'module-passenger-cabin':       [['Economy', 'internal/economy_passenger_cabin'],
                                ['Business', 'internal/business_passenger_cabin'],
                                ['First', 'internal/first_passenger_cabin'],
                                ['Luxury', 'internal/luxury_passenger_cabin']],
  'module-afmu':                  [[null, 'internal/auto_field_maintenance_unit']],
  'module-limpet-controllers':    [['Collector', 'internal/collector_limpet_controllers'],
                                ['Prospector', 'internal/prospector_limpet_controllers'],
                                ['Fuel Transfer', 'internal/fuel_transfer_limpet_controllers'],
                                ['Hatch Breaker', 'internal/hatch_breaker_limpet_controller'],
                                ['Repair', 'internal/repair_limpet_controller'],
                                ['Recon', 'internal/recon_limpet_controllers'],
                                ['Decontamination', 'internal/decontamination_limpet_controller'],
                                ['Research', 'internal/research_limpet_controller'],
                                ['Universal (Multi)', 'internal/multi_limpet_controllers']],
  'module-weapon-stabiliser':     [[null, 'internal/experemental_weapon_stabilizer']],
  'module-refinery':              [[null, 'internal/refinery']],
  'module-fsd-interdictor':       [[null, 'internal/frame_shift_drive_interdictor']],
  'module-flight-assists':        [['Docking Computer', 'internal/docking_computer'],
                                ['Supercruise Assist', 'internal/supercruise_assist'],
                                ['Fighter Hangar', 'internal/fighter_hangar'],
                                ['Planetary Vehicle Hangar (SRV)', 'internal/planetary_vehicle_hanger'],
                                ['Planetary Approach Suite', 'internal/planetary_approach_suite']],
  'module-shield-booster':       [[null, 'hardpoints/shield_booster']],
  'module-countermeasures':      [['Heat Sink Launcher', 'hardpoints/heat_sink_launcher'],
                                ['Chaff Launcher', 'hardpoints/chaff_launcher'],
                                ['Point Defence', 'hardpoints/point_defence'],
                                ['ECM', 'hardpoints/electronic_countermeasure']],
  'module-scanners':             [['Kill Warrant Scanner', 'hardpoints/kill_warrant_scanner'],
                                ['Manifest Scanner', 'hardpoints/cargo_scanner'],
                                ['Frame Shift Wake Scanner', 'hardpoints/frame_shift_wake_scanner']],
  'module-xeno':                 [['Xeno Scanner', 'hardpoints/xeno_scanner'],
                                ['Pulse Wave Analyser', 'hardpoints/pulse_wave_analyser'],
                                ['Caustic Sink', 'hardpoints/caustic_sink_launcher'],
                                ['Shutdown Field Neutraliser', 'hardpoints/shutdown_field_neutraliser']],
  'module-lasers':                [['Beam Laser', 'hardpoints/beam_laser'],
                                ['Burst Laser', 'hardpoints/burst_laser'],
                                ['Pulse Laser', 'hardpoints/pulse_laser']],
  'module-kinetic':               [['Multi-Cannon', 'hardpoints/multi_cannon'],
                                ['Multi-Cannon (Advanced)', 'hardpoints/multi_cannon_advanced'],
                                ['Cannon', 'hardpoints/cannon'],
                                ['Fragment Cannon', 'hardpoints/fragment_cannon'],
                                ['Rail Gun', 'hardpoints/rail_gun'],
                                ['Shock Cannon', 'hardpoints/shock_cannon']],
  'module-explosive':             [['Missile Rack', 'hardpoints/missile_rack'],
                                ['Missile Rack (Advanced)', 'hardpoints/missile_rack_advanced'],
                                ['Torpedo Pylon', 'hardpoints/torpedo_pylon'],
                                ['Mine Launcher', 'hardpoints/mine_launcher']],
  'module-plasma':                [[null, 'hardpoints/plasma_accelerator']],
  'module-mining':                [['Mining Laser', 'hardpoints/mining_laser'],
                                ['Abrasion Blaster', 'hardpoints/abrasion_blaster'],
                                ['Sub-surface Displacement Missile', 'hardpoints/sub_surface_displacement_missile'],
                                ['Seismic Charge Launcher', 'hardpoints/seismic_charge_launcher'],
                                ['Mining Volley Repeater', 'hardpoints/mining_volley_repeater']],
  'module-guardian-ax':           [['Guardian Gauss Cannon', 'hardpoints/guardian_gauss_cannon'],
                                ['Guardian Shard Cannon', 'hardpoints/guardian_shard_cannon'],
                                ['Guardian Plasma Charger', 'hardpoints/guardian_plasma_charger'],
                                ['AX Multi-Cannon', 'hardpoints/ax_multi_cannon'],
                                ['AX Multi-Cannon (Enhanced)', 'hardpoints/ax_multi_cannon_enhanced'],
                                ['AX Missile Rack', 'hardpoints/ax_missile_rack'],
                                ['AX Missile Rack (Enhanced)', 'hardpoints/ax_missile_rack_enhanced'],
                                ['Enzyme Missile Rack', 'hardpoints/enzyme_missile_rack'],
                                ['Nanite Torpedo Pylon', 'hardpoints/nanite_torpedo_pylon'],
                                ['Remote Flak Launcher', 'hardpoints/remote_release_flak_launcher'],
                                ['Remote Flechette Launcher', 'hardpoints/remote_release_flechette_launcher']],
};

// ---------------------------------------------------------------------------
// COLUMN SELECTION — per coriolis file (basename, no dir). Each entry is the
// ordered list of up-to-5 module-relevant stat keys to surface BETWEEN the
// always-on [Mass, Integrity, Power] block and the always-last Value (CR).
// `powerStat` (optional) names a power field to use IN PLACE OF a `power` draw
// column (e.g. power plant has no draw — it surfaces pgen instead).
// ---------------------------------------------------------------------------
const PWR_DRAW = 'power'; // the standard power-DRAW field

// friendly labels for every key we render
const LABELS = {
  class: 'Class', rating: 'Rating', mass: 'Mass (t)', integrity: 'Integrity',
  power: 'Power (MW)', cost: 'Value (CR)',
  // generators / plant
  pgen: 'Power Gen (MW)', eff: 'Heat Eff.',
  // thrusters
  optmass: 'Optimal Mass (t)', maxmass: 'Max Mass (t)', minmass: 'Min Mass (t)',
  // fsd
  maxfuel: 'Max Fuel/Jump (t)', fuelmul: 'Fuel Multiplier', fuelpower: 'Fuel Power', boot: 'Boot Time (s)',
  // life support / interdictor
  time: 'Duration (s)', facinglimit: 'Facing Limit (°)', ranget: 'Range Bonus',
  // power distributor
  syscap: 'SYS Cap', sysrate: 'SYS Rate', engcap: 'ENG Cap', engrate: 'ENG Rate',
  wepcap: 'WEP Cap', weprate: 'WEP Rate',
  // sensors
  range: 'Range (m)', angle: 'Scan Angle (°)',
  // fuel tank / scoop / cargo / cabins / refinery / fighter / dss
  fuel: 'Capacity (t)', rate: 'Scoop Rate (kg/s)', cargo: 'Capacity (t)',
  passengers: 'Passengers', bins: 'Refinery Bins', bays: 'Bays',
  proberadius: 'Probe Radius', jumpboost: 'Jump Boost (ly)',
  // shields
  optmul: 'Optimal Mult.', minmul: 'Min Mult.', maxmul: 'Max Mult.',
  regen: 'Regen (MJ/s)', brokenregen: 'Broken Regen (MJ/s)', distdraw: 'Distributor Draw (MW)',
  kinres: 'Kinetic Res.', thermres: 'Thermal Res.', explres: 'Explosive Res.',
  // shield cell bank
  shieldreinforcement: 'Shield Reinf. (MJ)', spinup: 'Spin-up (s)', duration: 'Duration (s)',
  clip: 'Clip', ammo: 'Ammo', thermload: 'Thermal Load',
  // hull / module reinforcement
  hullreinforcement: 'Hull Reinf.', protection: 'Damage Protection', causres: 'Caustic Res.',
  shieldaddition: 'Shield Reinf. (MJ)',
  // limpets
  maximum: 'Max Limpets', hacktime: 'Hack Time (s)',
  // shield booster
  shieldboost: 'Shield Boost',
  // scanners
  scantime: 'Scan Time (s)', scanrange: 'Scan Range (m)', maxangle: 'Max Angle (°)',
  cooldown: 'Cooldown (s)', activepower: 'Active Power (MW)',
  // afmu
  repair: 'Repair Capacity',
  // weapons
  mount: 'Mount', damage: 'Damage', piercing: 'Armour Pierce', falloff: 'Falloff (m)',
  shotspeed: 'Shot Speed (m/s)', reload: 'Reload (s)', fireint: 'Fire Interval (s)',
  roundspershot: 'Rounds/Shot', charge: 'Charge (s)', chargetime: 'Charge Time (s)',
  burst: 'Burst Size', burstrof: 'Burst RoF',
};

// mount-code → readable
const MOUNT = { F: 'Fixed', G: 'Gimballed', T: 'Turreted' };

// per-file extra-stat column choices (in render order)
const COLS = {
  // ---- standard ----
  power_plant:          { powerStat: 'pgen', extra: ['eff'] },
  thrusters:            { extra: ['optmass', 'maxmass'] },
  frame_shift_drive:    { extra: ['optmass', 'maxfuel', 'fuelmul', 'fuelpower'] },
  life_support:         { extra: ['time', 'boot'] },
  power_distributor:    { extra: ['wepcap', 'weprate', 'engcap', 'syscap', 'sysrate'] },
  sensors:             { extra: ['range', 'angle'] },
  fuel_tank:            { extra: ['fuel'] },
  // ---- internal ----
  shield_generator:     { extra: ['optmass', 'minmass', 'maxmass', 'optmul', 'regen'] },
  bi_weave_shield_generator:  { extra: ['optmass', 'minmass', 'maxmass', 'optmul', 'regen'] },
  pristmatic_shield_generator:{ extra: ['optmass', 'minmass', 'maxmass', 'optmul', 'regen'] },
  shield_cell_bank:     { extra: ['shieldreinforcement', 'spinup', 'duration', 'clip', 'ammo'] },
  hull_reinforcement_package:   { extra: ['hullreinforcement', 'kinres', 'thermres', 'explres', 'causres'] },
  module_reinforcement_package: { extra: ['protection'] },
  guardian_hull_reinforcement_package:   { extra: ['hullreinforcement', 'kinres', 'thermres', 'explres', 'causres'] },
  guardian_module_reinforcement_package: { extra: ['protection'] },
  guardian_shield_reinforcement_package: { extra: ['shieldaddition'] },
  meta_alloy_hull_reinforcement_package: { extra: ['hullreinforcement', 'kinres', 'thermres', 'explres', 'causres'] },
  experemental_weapon_stabilizer: { extra: [] },
  guardian_fsd_booster: { extra: ['jumpboost'] },
  fuel_scoop:           { extra: ['rate'] },
  surface_scanner:      { extra: ['proberadius'] },
  cargo_rack:           { extra: ['cargo'] },
  cargo_rack_large:     { extra: ['cargo'] },
  planetary_vehicle_hanger: { extra: ['bays'] },
  planetary_approach_suite: { extra: [] },
  economy_passenger_cabin:  { extra: ['passengers'] },
  business_passenger_cabin: { extra: ['passengers'] },
  first_passenger_cabin:    { extra: ['passengers'] },
  luxury_passenger_cabin:   { extra: ['passengers'] },
  auto_field_maintenance_unit: { extra: ['repair', 'ammo'] },
  collector_limpet_controllers:    { extra: ['maximum', 'range', 'time'] },
  prospector_limpet_controllers:   { extra: ['maximum', 'range'] },
  fuel_transfer_limpet_controllers:{ extra: ['maximum', 'range'] },
  hatch_breaker_limpet_controller: { extra: ['maximum', 'range', 'time'] },
  repair_limpet_controller:        { extra: ['maximum', 'range'] },
  recon_limpet_controllers:        { extra: ['maximum', 'range', 'hacktime'] },
  decontamination_limpet_controller: { extra: ['maximum', 'range'] },
  research_limpet_controller:      { extra: ['maximum', 'range', 'time'] },
  multi_limpet_controllers:        { extra: ['maximum', 'range'] },
  refinery:             { extra: ['bins'] },
  frame_shift_drive_interdictor: { extra: ['facinglimit', 'ranget', 'boot'] },
  docking_computer:     { extra: [] },
  supercruise_assist:   { extra: [] },
  fighter_hangar:       { extra: ['bays'] },
  // ---- hardpoints ----
  shield_booster:       { extra: ['shieldboost', 'kinres', 'thermres', 'explres'] },
  heat_sink_launcher:   { extra: ['thermload', 'clip', 'ammo'] },
  chaff_launcher:       { extra: ['duration', 'clip', 'ammo'] },
  point_defence:        { extra: ['range', 'damage', 'clip', 'ammo'] },
  electronic_countermeasure: { extra: ['activepower', 'range', 'cooldown', 'thermload'] },
  kill_warrant_scanner: { extra: ['range', 'scantime'] },
  cargo_scanner:        { extra: ['range', 'scantime', 'angle'] },
  frame_shift_wake_scanner: { extra: ['range', 'scantime'] },
  xeno_scanner:         { extra: ['range', 'scantime', 'angle'] },
  pulse_wave_analyser:  { extra: ['scanrange', 'maxangle', 'scantime'] },
  caustic_sink_launcher: { extra: ['clip', 'ammo', 'reload'] },
  shutdown_field_neutraliser: { extra: ['activepower', 'range', 'duration', 'cooldown'] },
  // weapons: Mount, Damage, Armour Pierce + per-weapon extras
  beam_laser:           { extra: ['mount', 'damage', 'piercing', 'distdraw', 'thermload'] },
  burst_laser:          { extra: ['mount', 'damage', 'piercing', 'distdraw', 'thermload'] },
  pulse_laser:          { extra: ['mount', 'damage', 'piercing', 'distdraw', 'thermload'] },
  multi_cannon:         { extra: ['mount', 'damage', 'piercing', 'clip', 'ammo'] },
  multi_cannon_advanced:{ extra: ['mount', 'damage', 'piercing', 'clip', 'ammo'] },
  cannon:               { extra: ['mount', 'damage', 'piercing', 'clip', 'ammo'] },
  fragment_cannon:      { extra: ['mount', 'damage', 'roundspershot', 'clip', 'ammo'] },
  rail_gun:             { extra: ['mount', 'damage', 'piercing', 'distdraw', 'thermload'] },
  shock_cannon:         { extra: ['mount', 'damage', 'piercing', 'clip', 'ammo'] },
  missile_rack:         { extra: ['mount', 'damage', 'clip', 'ammo', 'thermload'] },
  missile_rack_advanced:{ extra: ['mount', 'damage', 'clip', 'ammo', 'thermload'] },
  torpedo_pylon:        { extra: ['mount', 'damage', 'clip', 'ammo', 'thermload'] },
  mine_launcher:        { extra: ['mount', 'damage', 'clip', 'ammo', 'thermload'] },
  plasma_accelerator:   { extra: ['mount', 'damage', 'piercing', 'clip', 'ammo'] },
  // mining tools
  mining_laser:         { extra: ['mount', 'damage', 'distdraw', 'thermload'] },
  abrasion_blaster:     { extra: ['mount', 'damage', 'distdraw', 'thermload'] },
  sub_surface_displacement_missile: { extra: ['mount', 'damage', 'clip', 'ammo'] },
  seismic_charge_launcher: { extra: ['mount', 'damage', 'clip', 'ammo'] },
  mining_volley_repeater: { extra: ['mount', 'damage', 'clip', 'ammo'] },
  guardian_gauss_cannon:   { extra: ['mount', 'damage', 'piercing', 'clip', 'ammo'] },
  guardian_shard_cannon:   { extra: ['mount', 'damage', 'roundspershot', 'clip', 'ammo'] },
  guardian_plasma_charger: { extra: ['mount', 'damage', 'piercing', 'clip', 'ammo'] },
  ax_multi_cannon:      { extra: ['mount', 'damage', 'piercing', 'clip', 'ammo'] },
  ax_multi_cannon_enhanced: { extra: ['mount', 'damage', 'piercing', 'clip', 'ammo'] },
  ax_missile_rack:      { extra: ['mount', 'damage', 'clip', 'ammo', 'thermload'] },
  ax_missile_rack_enhanced: { extra: ['mount', 'damage', 'clip', 'ammo', 'thermload'] },
  enzyme_missile_rack:  { extra: ['mount', 'damage', 'clip', 'ammo', 'thermload'] },
  nanite_torpedo_pylon: { extra: ['mount', 'damage', 'clip', 'ammo', 'thermload'] },
  remote_release_flak_launcher:      { extra: ['mount', 'damage', 'clip', 'ammo', 'thermload'] },
  remote_release_flechette_launcher: { extra: ['mount', 'damage', 'clip', 'ammo', 'thermload'] },
};

// ---- helpers ---------------------------------------------------------------
const RATING_ORDER = { A: 0, B: 1, C: 2, D: 3, E: 4, F: 5, G: 6, H: 7, I: 8 };
const ratingRank = (r) => (r in RATING_ORDER ? RATING_ORDER[r] : 100);

const esc = (s) => String(s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// true junk row: coriolis "missing"/"unrecognised" placeholder
const isJunk = (r) =>
  r.rating === 'Z' || /Missing|Unrecognised/i.test(r.symbol || '') || /Unrecognised/i.test(r.ukName || '');

// numeric formatting: thousands separators for cost; otherwise keep source
// precision (number → its own toString, trimming nothing fabricated).
function fmtNum(v) {
  if (typeof v !== 'number' || !Number.isFinite(v)) return esc(v);
  if (Number.isInteger(v)) return v.toLocaleString('en-US');
  // keep source precision, but group the integer part
  const neg = v < 0;
  const [int, frac] = Math.abs(v).toString().split('.');
  const grouped = Number(int).toLocaleString('en-US');
  return (neg ? '-' : '') + grouped + (frac ? '.' + frac : '');
}

// render a single cell value for a given key
function fmtCell(key, v) {
  if (v === undefined || v === null || v === '') return '—';
  if (key === 'mount') return esc(MOUNT[v] || v);
  if (key === 'cost') return (typeof v === 'number' && Number.isFinite(v)) ? Math.round(v).toLocaleString('en-US') : esc(v);
  if (typeof v === 'number') return fmtNum(v);
  return esc(v);
}

// Build the ordered column key list for a file (basename, no dir/ext).
function colKeys(base) {
  const cfg = COLS[base] || { extra: [] };
  const keys = ['class', 'rating', 'mass', 'integrity'];
  if (cfg.powerStat) keys.push(cfg.powerStat);          // power plant: pgen replaces draw
  else keys.push(PWR_DRAW);                              // standard power-draw column
  for (const k of cfg.extra) keys.push(k);
  keys.push('cost');                                     // Value (CR) always last
  return keys;
}

const labelFor = (key) => LABELS[key] || key;

// dedupe rows on (class, rating, mount), preferring the "plain" standard row
// (no special `name`, no preEngineered flag) so special/variant duplicates that
// would collide on the same (class, rating) don't render twice.
function dedupe(rows) {
  const seen = new Map();
  for (const r of rows) {
    const key = `${r.class}|${r.rating}|${r.mount || ''}`;
    const isSpecial = !!r.name || r.preEngineered != null || r.experimental != null;
    if (!seen.has(key)) { seen.set(key, r); continue; }
    const prev = seen.get(key);
    const prevSpecial = !!prev.name || prev.preEngineered != null || prev.experimental != null;
    if (prevSpecial && !isSpecial) seen.set(key, r); // replace special with plain
  }
  return [...seen.values()];
}

// Render one Concept-D table from a coriolis row array + its requested column keys.
function renderTable(rows0, keysReq) {
  const cleaned = dedupe(rows0.filter((r) => !isJunk(r)));
  // prune any column (other than the always-shown Class/Rating/Value) that no
  // row in THIS table populates — modules genuinely lacking e.g. integrity or a
  // power draw shouldn't carry an all-em-dash column.
  const keys = keysReq.filter((k, i) => {
    if (i === 0 || i === 1 || k === 'cost') return true; // Class, Rating, Value
    return cleaned.some((r) => r[k] !== undefined && r[k] !== null && r[k] !== '');
  });
  const colCount = keys.length;
  const gIdx = 0;   // class
  const rIdx = 1;   // rating

  // sort: Class DESC, Rating ASC, then mount order F<G<T, then damage/optmass DESC
  const mountRank = (m) => (m === 'F' ? 0 : m === 'G' ? 1 : m === 'T' ? 2 : 3);
  const sorted = cleaned.slice().sort((a, b) => {
    const gc = b.class - a.class;
    if (gc) return gc;
    const rc = ratingRank(a.rating) - ratingRank(b.rating);
    if (rc) return rc;
    return mountRank(a.mount) - mountRank(b.mount);
  });

  const thead = '<thead><tr>' + keys.map((k) => {
    const lbl = labelFor(k);
    return `<th title="${esc(lbl)}"><span class="th-lbl">${esc(lbl)}</span></th>`;
  }).join('') + '</tr></thead>';

  const classes = [...new Set(sorted.map((r) => r.class))];
  const grouped = classes.length > 1;
  const firstClass = sorted.length ? sorted[0].class : null;

  const body = [];
  let lastBand = Symbol('none');
  for (const r of sorted) {
    if (grouped && r.class !== lastBand) {
      body.push(`<tr class="grp" data-grp="${esc(r.class)}"><td colspan="${colCount}">Class ${esc(r.class)}</td></tr>`);
      lastBand = r.class;
    }
    const vis = grouped && r.class === firstClass ? ' class="cd-vis"' : '';
    const tds = keys.map((k, i) => {
      if (i === gIdx) return `<td class="num">${esc(r.class)}</td>`;
      if (i === rIdx) return `<td class="rt" data-r="${esc(r.rating)}">${esc(r.rating)}</td>`;
      return `<td>${fmtCell(k, r[k])}</td>`;
    }).join('');
    body.push(`<tr${vis}>${tds}</tr>`);
  }

  const table =
    `<div class="tbl-scroll"><table class="data spec cD">${thead}<tbody>` +
    body.join('') + `</tbody></table></div>`;

  if (grouped) {
    return `<div class="spec-wrap">${table}<div class="spec-fade"></div>` +
      `<button class="spec-pill" type="button">Show all classes &#9662;</button></div>`;
  }
  // Flat (single class group) tables aren't collapsible — mark the wrap `open` so
  // the collapsed-state rule (`.spec-wrap .cD tbody tr{display:none}`) doesn't hide
  // their rows (they carry no `.cd-vis`, and there's no pill to reveal them).
  return `<div class="spec-wrap open">${table}</div>`;
}

// Build the full appended spec block for a card from its CARD_MAP entry.
function renderCardSpec(entries) {
  const parts = [];
  let totalCols = 0;
  for (const [variant, file] of entries) {
    const base = file.split('/').pop();
    const d = JSON.parse(readFileSync(join(DATA_DIR, file + '.json'), 'utf8'));
    const grp = Object.keys(d)[0];
    const keys = colKeys(base);
    totalCols = keys.length;
    if (variant) parts.push(`<p class="spec-label"><b>${esc(variant)}</b></p>`);
    parts.push(renderTable(d[grp], keys));
  }
  return { html: parts.join('\n'), cols: totalCols, tables: entries.length };
}

// ---- card body transforms --------------------------------------------------
// find matching </div> for a <div ...> opened at innerStart-1 (depth-aware)
function matchClose(s, innerStart) {
  const re = /<div\b|<\/div>/g;
  re.lastIndex = innerStart;
  let depth = 1, tok;
  while ((tok = re.exec(s))) {
    if (tok[0] === '</div>') { depth--; if (depth === 0) return tok.index; }
    else depth++;
  }
  return -1;
}

// strip every <div class="spec-wrap">…</div> and the <p class="spec-label"> just
// before it (so re-running starts from a clean body).
function stripSpecBlocks(body) {
  let out = body;
  const WRAP = /<div class="spec-wrap(?: open)?">/;   // flat tables carry the `open` class
  for (;;) {
    const m = /<p class="spec-label">[\s\S]*?<\/p>\s*<div class="spec-wrap(?: open)?">|<div class="spec-wrap(?: open)?">/.exec(out);
    if (!m) break;
    const wm = WRAP.exec(out.slice(m.index));
    const wrapStart = m.index + wm.index;
    const innerStart = wrapStart + wm[0].length;
    const close = matchClose(out, innerStart);
    out = out.slice(0, m.index) + out.slice(close + '</div>'.length);
  }
  return out;
}

// strip Availability / Core stats panels, then drop emptied .bp-ctx rows
function stripStalePanels(body) {
  body = body.replace(
    /\s*<div class="bp-panel"><h6>(?:Availability|Core stats)<\/h6>[\s\S]*?<\/p><\/div>/g, '');
  // drop now-empty .bp-ctx
  let out = '', cursor = 0;
  const openRe = /<div class="bp-ctx">/g;
  let mm;
  while ((mm = openRe.exec(body))) {
    const ctxStart = mm.index;
    const innerStart = mm.index + mm[0].length;
    const close = matchClose(body, innerStart);
    const inner = body.slice(innerStart, close);
    out += body.slice(cursor, ctxStart);
    if (inner.includes('class="bp-panel"')) out += body.slice(ctxStart, close + '</div>'.length);
    cursor = close + '</div>'.length;
    openRe.lastIndex = cursor;
  }
  out += body.slice(cursor);
  return out;
}

// extract callouts into sink (in order), removing them from body
function extractCallouts(body, sink) {
  let out = '', cursor = 0;
  const openRe = /<div class="callout[^"]*">/g;
  let mm;
  while ((mm = openRe.exec(body))) {
    const cStart = mm.index;
    const innerStart = mm.index + mm[0].length;
    const close = matchClose(body, innerStart);
    sink.push(body.slice(cStart, close + '</div>'.length).trim());
    out += body.slice(cursor, cStart);
    cursor = close + '</div>'.length;
    openRe.lastIndex = cursor;
  }
  out += body.slice(cursor);
  return out;
}

function transformCard(cardHtml, entries) {
  const m = /<div class="bp-card-body">/.exec(cardHtml);
  const bodyStart = m.index + m[0].length;
  const bodyEnd = matchClose(cardHtml, bodyStart);
  let body = cardHtml.slice(bodyStart, bodyEnd);

  body = stripSpecBlocks(body);
  body = stripStalePanels(body);

  const callouts = [];
  body = extractCallouts(body, callouts);

  const spec = renderCardSpec(entries);

  let tail = '';
  if (callouts.length) tail += '\n    ' + callouts.join('\n    ');
  tail += '\n    ' + spec.html + '\n  ';

  const newBody = body.replace(/\s*$/, '') + tail;
  return { html: cardHtml.slice(0, bodyStart) + newBody + cardHtml.slice(bodyEnd), spec };
}

// ---- run -------------------------------------------------------------------
let html = readFileSync(HTML, 'utf8');

// locate every .bp-card span by id
const cardRe = /<div class="bp-card" id="([^"]+)">/g;
const cards = [];
let cm;
while ((cm = cardRe.exec(html))) {
  const id = cm[1];
  const start = cm.index;
  const end = matchClose(html, cm.index + cm[0].length) + '</div>'.length;
  cards.push({ id, start, end });
}

const report = [];
// process last → first so indices stay valid
for (let c = cards.length - 1; c >= 0; c--) {
  const { id, start, end } = cards[c];
  const entries = CARD_MAP[id];
  if (!entries) { report.unshift({ id, skipped: true }); continue; }
  const cardHtml = html.slice(start, end);
  const { html: newCard, spec } = transformCard(cardHtml, entries);
  html = html.slice(0, start) + newCard + html.slice(end);
  report.unshift({ id, cols: spec.cols, tables: spec.tables });
}

// ---- style injection (replace-or-insert, so CSS edits always propagate on re-run) ----
{
  const styleBlock = `<style>
${SPEC_STYLE_MARKER}
table.spec.cD{table-layout:fixed;width:100%;min-width:560px}
table.spec.cD th,table.spec.cD td{text-align:center;white-space:nowrap;font-variant-numeric:tabular-nums}
table.spec.cD th:nth-child(1),table.spec.cD td:nth-child(1){width:72px}
table.spec.cD th:nth-child(2),table.spec.cD td:nth-child(2){width:74px}
table.spec.cD th .th-lbl{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;white-space:normal;line-height:1.15}
table.spec.cD td.rt{font-weight:700}
table.spec.cD tr.grp td{text-align:left;background:rgba(224,168,56,.07);font-weight:700;letter-spacing:.04em;color:var(--accent-lt,#e0a838);text-transform:uppercase;font-size:.78rem}
.spec-label{margin:14px 0 4px;color:var(--ink-2,#b9c0c8);font-size:.86rem}
.spec-wrap{position:relative;margin-top:6px}
.spec-wrap .cD tbody tr{display:none}
.spec-wrap .cD tbody tr.cd-vis{display:table-row}
.spec-wrap.open .cD tbody tr{display:table-row}
.spec-fade{position:absolute;left:0;right:0;bottom:0;height:90px;pointer-events:none;background:linear-gradient(to bottom,rgba(11,13,16,0),var(--bg,#0b0d10) 92%)}
.spec-wrap.open .spec-fade{display:none}
.spec-pill{position:absolute;left:50%;bottom:12px;transform:translateX(-50%);z-index:2;padding:7px 18px;border-radius:999px;background:var(--panel,#14181d);border:1px solid var(--accent-soft,#5a4a22);color:var(--accent-lt,#e0a838);font:inherit;font-size:.82rem;letter-spacing:.04em;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.5)}
.spec-pill:hover{background:rgba(224,168,56,.12)} .spec-wrap.open .spec-pill{position:static;transform:none;display:block;margin:10px auto 0}
</style>`;
  if (html.includes(SPEC_STYLE_MARKER)) {
    html = html.replace(/<style>\s*\/\* concept-D spec tables \*\/[\s\S]*?<\/style>/, styleBlock);
  } else {
    html = html.replace(
      /(<link rel="stylesheet" href="\.\.\/\.\.\/design-system\/css\/ed-blackbox\.css">)/,
      `$1\n${styleBlock}`);
  }
}

// ---- one-time pill JS injection ----
if (!html.includes('p.closest(\'.spec-wrap\')')) {
  const jsBlock = `
  // ---- Concept-D spec-table reveal pills ----
  document.querySelectorAll('.spec-pill').forEach(function(p){p.addEventListener('click',function(){var w=p.closest('.spec-wrap');if(!w)return;w.classList.toggle('open');var o=w.classList.contains('open');p.innerHTML=o?'Collapse \\u25B2':'Show all classes \\u25BE';if(!o){var t=w.getBoundingClientRect().top+window.pageYOffset-80;window.scrollTo({top:t,behavior:'smooth'});}});});
`;
  html = html.replace(/\n\}\)\(\);\n<\/script>/, `\n${jsBlock}})();\n</script>`);
}

writeFileSync(HTML, html, 'utf8');

// ---- sanity report ----
console.log('build-module-spec-tables — Concept D (coriolis-sourced)');
let built = 0;
for (const r of report) {
  if (r.skipped) { console.log(`  (unmapped card) ${r.id}`); continue; }
  built++;
  console.log(`  ${r.id.padEnd(28)} ${r.cols} cols, ${r.tables} table(s)`);
}
console.log(`  cards built: ${built}/${Object.keys(CARD_MAP).length}`);
