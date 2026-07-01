export const meta = {
  name: 'build-dossiers',
  description: 'Draft + adversarially verify candidate ship dossiers in parallel',
  phases: [
    { title: 'Draft', detail: 'author loadout + sources + HTML per dossier' },
    { title: 'Verify', detail: 'adversarial game-accuracy + structure check' },
  ],
}

// args: array of { ship, role, slug, rating, template, loadoutTemplates:[...] }
let CANDS = args
if (typeof CANDS === 'string') { try { CANDS = JSON.parse(CANDS) } catch (e) { CANDS = [] } }
if (CANDS && !Array.isArray(CANDS) && Array.isArray(CANDS.candidates)) CANDS = CANDS.candidates
if (!Array.isArray(CANDS)) CANDS = []
log(`args type=${typeof args}, candidates=${CANDS.length}`)

const SCORECARD_SCHEMA = {
  type: 'object',
  required: ['slug', 'ok', 'scorecard'],
  properties: {
    slug: { type: 'string' },
    ok: { type: 'boolean' },
    audit_clean: { type: 'boolean' },
    scorecard: {
      type: 'object',
      required: ['verdict', 'factors'],
      properties: {
        verdict: { type: 'string' },
        factors: {
          type: 'array',
          items: {
            type: 'object',
            required: ['factor', 'earned', 'why'],
            properties: {
              factor: { type: 'string' },
              earned: { type: 'integer' },
              why: { type: 'string' },
            },
          },
        },
      },
    },
    notes: { type: 'string' },
  },
}

const VERIFY_SCHEMA = {
  type: 'object',
  required: ['slug', 'pass', 'issues'],
  properties: {
    slug: { type: 'string' },
    pass: { type: 'boolean' },
    issues: { type: 'array', items: { type: 'string' } },
  },
}

const draftPrompt = (c) => `You are building ONE Elite Dangerous ship dossier for the E:D Black Box static site (repo root /mnt/d/Profile/Users/Tushar/Documents/GIT/ed-blackbox). Work game-accurately — this is a LIVE site, accuracy over recall (never invent stats; read the data).

TARGET: ${c.ship} · ${c.role} — suitability rating ${c.rating}/100. slug = ${c.slug}

Author THREE new files (only these three; do NOT touch any other file):
1. data/ship-loadouts/${c.slug}.json  — SLEF loadout, 3 builds (initial / arated / engineered)
2. data/sources/ships/ship-dossiers/${c.slug}.json — external Sources
3. guides/ships/ship-dossiers/${c.slug}.html — the 13-section dossier page

STEP A — read to ground yourself (do not skip):
- data/ship-loadouts/federal-corvette-combat.json — the canonical SLEF schema (3 builds; editorial 'edbb' block with role/intro/callout/notes/engineeringPlan on the engineered build).
- The template dossier guides/ships/ship-dossiers/${c.template}.html — SAME HULL (reuse ALL hull facts: manufacturer, pad, speed/boost, hardpoints, utility mounts, optional internals, hull price, image, header/masthead/footer scaffolding).
- Same-role loadout patterns for correct module/engineering/experimental choices: ${(c.loadoutTemplates||[]).map(t=>'data/ship-loadouts/'+t+'.json').join(', ')}.
- data/ships/<hull>.json (find it by manufacturer/name) for the hull's EXACT slot layout (standard core sizes, hardpoint sizes, optional internal sizes). Module Item symbols MUST match sizes the hull actually has.
- data/ship-ratings/${c.role}.json → its "scorecard_weights" (the role's factors + weights summing to 100). Your scorecard factors MUST be exactly those factors in that order; earned points 0..weight and MUST sum to ${c.rating}.

STEP B — loadout (data/ship-loadouts/${c.slug}.json):
- Build a role-appropriate ${c.role} fit for ${c.ship}. Use FDev Item symbols exactly as they appear in the template loadouts (e.g. int_powerplant_size7_class5, hpt_multicannon_gimbal_large, int_shieldgenerator_size6_class3_fast). Sizes must fit the hull's real slots.
- initial = buy-only stock cores (class1) only. arated = full A-rated fit, no engineering. engineered = same modules with Engineering blocks (BlueprintName/Level 5/Quality 1.0/ExperimentalEffect) + the edbb editorial block (role, intro, per-slot notes keyed by Slot, engineeringPlan array).
- You may use scripts/slef_resolve.py to look up symbols: python3 scripts/slef_resolve.py find <module> <size> <rating> <mount>.
- SELF-CHECK (required): run \`python3 scripts/audit-ship-loadouts.py 2>&1 | grep -iE '${c.slug}|error|E[0-9]'\`. Fix until your dossier shows NO error (E-codes / missing core slots / sizing). W1/W2 warnings are acceptable (shared across the fleet). Report audit_clean=true only if no errors.

STEP C — sources (data/sources/ships/ship-dossiers/${c.slug}.json): schema { page, lead:["Figures on this page are verified against the sources below."], sources:[{label,what,url,display}] }. The "page" field MUST be exactly "guides/ships/ship-dossiers/${c.slug}.html" (include the leading "guides/"). EXTERNAL references only (Coriolis, EDSY, elitedangerous.com, EDCD coriolis-data, Inara, Fandom) — never a link to another page on this site. Model it on data/sources/ships/ship-dossiers/${c.template}.json.

STEP D — HTML (guides/ships/ship-dossiers/${c.slug}.html): clone ${c.template}.html and retarget to ${c.role}. Keep the EXACT 13 <section id> order and the design-system markup (component classes only, NO new CSS beyond the accent comment). Rules:
- Accent by role: combat→maroon, ax→good-green, mining→amber, trading→green, exploration→blue, passenger→purple, multipurpose→amber (match how an existing ${c.role} dossier sets '<!-- Per-page accent -->' and '<span class="role ac-role-${c.role}">'). If unsure, open any existing ${c.role} dossier and copy its accent comment + role tag class.
- <title>, hdr-crumb-title, masthead role tag, and the masthead stat "<div class=\\"n\\">${c.rating}<small>/100</small></div>" + "--pct:${c.rating}" bar.
- LEAVE AS SHELLS (regenerated later — just .sec-head + a one-line intro <p>, copy the template's shell EXACTLY): §03 section-why-this-rating, §06 section-3-state-loadout, §09 section-engineering-plan, §13 section-credits. For §13 the shell must be EXACTLY these FOUR SEPARATE LINES (the <section> open tag and the </section> close tag MUST each be alone on their own line — a one-line block breaks the sources parser):
  <section class="credits" id="section-credits">
    <div class="sec-head"><span class="sec-num">13</span><h2>Sources</h2></div>
    <p class="lead">Figures on this page are verified against the sources below.</p>
  </section>
Do NOT add any <div class="cr-rows"> or other content inside it. Keep the .vchips "Other role builds" placeholder wrapper.
- All hull stats (speed, boost, mass, hardpoints, slots, prices) MUST come from data/ships/<hull>.json (coriolis) — read them, do not estimate. Speed = properties.speed, boost = properties.boost. Keep every speed/boost figure on the page consistent with those two numbers (engineered figures may be noted separately as "~N engineered").
- Rewrite the AUTHORED prose for ${c.role}: briefing, §01 Role & Overview, §02 Key Stats, §04 How It Compares (TWO cmp tables ranking ${c.ship} among ${c.role} peers — read data/ship-ratings/${c.role}.json for real peer ratings; include the '${c.ship} <span class="pill md">this</span>' baseline row in rating order; link peer names to their <peer>-${c.role}.html dossiers ONLY if that file exists in guides/ships/ship-dossiers/), §05 Cost & Access, §07/§08 loadout plans, §10 Key Stat Upgrades, §11 Key Activities, §12 Field Notes. Operator-grade voice: terse, factual, no hype, no emoji, lead with the verdict. Be HONEST about why it scores ${c.rating} (not higher). Update the quick-nav (#qn-panel) labels to match any changed headings.

Return the scorecard manifest: { slug:"${c.slug}", ok:true, audit_clean:<bool>, scorecard:{verdict, factors:[{factor,earned,why}]}, notes:"<one line>" }. Do NOT run build-ship-* scripts, git, or edit shared files (role JSONs, index, matrix). Final message = the JSON manifest only.`

const verifyPrompt = (c, d) => `Adversarially verify the just-drafted Elite Dangerous dossier for ${c.ship} · ${c.role} (rating ${c.rating}). Repo root /mnt/d/Profile/Users/Tushar/Documents/GIT/ed-blackbox. Try to FALSIFY it; default pass=false unless it genuinely checks out.

IMPORTANT — do NOT flag these (they are generated LATER by build scripts, not the draft's job): §03 scorecard table empty, §06 3-State Loadout table empty, §09 Engineering Plan table empty, §13 Sources block empty, the ship being absent from data/ship-ratings/<role>.json, or the .vchips pills being placeholders. Those are all expected at this stage. Only report REAL content/accuracy defects in the authored files.

Check:
1. LOADOUT data/ship-loadouts/${c.slug}.json: run \`python3 scripts/audit-ship-loadouts.py 2>&1 | grep -iE '${c.slug}|E[0-9]'\` — any E-code / missing core slot / sizing error = FAIL. Cross-check every module Item size against the hull's real slots in data/ships/<hull>.json (a size-8 module in a size-6 slot = FAIL). Weapons must fit the hull's actual hardpoint sizes/count. Engineering blueprints must be valid for the module.
2. Role fit: is the fit actually appropriate for ${c.role}? (e.g. a trading fit needs cargo racks; a passenger fit needs passenger cabins; a combat fit needs weapons + shield/hull.) Wrong-role loadout = FAIL.
3. HTML guides/ships/ship-dossiers/${c.slug}.html: 13 <section id> present & correctly ordered; correct role accent + role tag; masthead shows ${c.rating}/100; the §04 peer ratings match data/ship-ratings/${c.role}.json; NO template/other-role residue (e.g. combat page mentioning Thargoids, or wrong hull name); every internal <a href> target file exists.
4. Sources: external-only (no internal-site links); well-formed.
5. Scorecard factors sum to exactly ${c.rating} and match the role's scorecard_weights factors.

Return { slug:"${c.slug}", pass:<bool>, issues:[<specific fixable problems, empty if pass>] }. If small issues are fixable, FIX them directly in the files, then set pass=true and list what you fixed. Final message = the JSON only.`

phase('Draft')
const results = await pipeline(
  CANDS,
  (c) => agent(draftPrompt(c), { label: `draft:${c.slug}`, phase: 'Draft', schema: SCORECARD_SCHEMA }),
  (draft, c) => agent(verifyPrompt(c, draft), { label: `verify:${c.slug}`, phase: 'Verify', schema: VERIFY_SCHEMA })
    .then((v) => ({ slug: c.slug, ship: c.ship, role: c.role, rating: c.rating, draft, verify: v }))
)

const ok = results.filter(Boolean).filter((r) => r.verify && r.verify.pass)
const bad = results.filter(Boolean).filter((r) => !r.verify || !r.verify.pass)
log(`drafted ${results.length}, verified-pass ${ok.length}, needs-attention ${bad.length}`)
return { ok, bad, all: results }
