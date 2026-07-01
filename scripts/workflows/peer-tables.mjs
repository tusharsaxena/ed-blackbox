export const meta = {
  name: 'peer-tables',
  description: 'Add newcomer ships to existing dossiers\' §4 peer-comparison tables',
  phases: [{ title: 'Edit', detail: 'insert newcomer rows into each dossier\'s §4 tables' }],
}

// args: { role, newcomers:[{ship,rating,pad,slug}], dossiers:[slug,...] }
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
const role = A.role
const newcomers = A.newcomers || []
const dossiers = A.dossiers || []
log(`role=${role}, ${dossiers.length} existing dossiers, ${newcomers.length} newcomers`)

const SCHEMA = {
  type: 'object',
  required: ['slug', 'added'],
  properties: {
    slug: { type: 'string' },
    added: { type: 'array', items: { type: 'string' } },
    skipped: { type: 'array', items: { type: 'string' } },
    note: { type: 'string' },
  },
}

const nc = newcomers.map(n => `${n.ship} (${n.pad}, ${n.rating}, ../ship-dossiers/${n.slug}.html)`).join('; ')

const prompt = (slug) => `Edit ONE file: /mnt/d/Profile/Users/Tushar/Documents/GIT/ed-blackbox/guides/ships/ship-dossiers/${slug}.html — an existing ${role} ship dossier. Add the newcomer ${role} ships below into its §04 "How It Compares" peer tables so the comparison reflects the full field. Edit ONLY this file.

NEWCOMERS to add: ${nc}

METHOD:
1. Read the file's §04 section (id="section-how-it-compares"). It has one or two \`table.cmp\` tables (a "same class" table for this hull's pad class, and often an "other classes" table). Each row: Ship | Class | <role stat> | Pros & cons vs THIS hull | Rating, with a \`<span class="rscore">N</span><div class="bar mini"><i style="--pct:N"></i></div>\` rating cell, a pad pill, and \`.pcc\` \`<span class="p">\`/\`<span class="c">\` cells.
2. Determine THIS hull's pad class (from its masthead/§02). For EACH newcomer: if it is ALREADY present in §04 (search for its slug), SKIP it. Otherwise insert a <tr> in DESCENDING rating order — into the "same class" table if the newcomer's pad matches THIS hull's class, or the "other classes" table if the dossier has one and the classes differ. If the dossier only has a single same-class table and the newcomer is a different class, skip it (record in skipped[] with reason).
3. Match the EXISTING row markup EXACTLY. Link the ship name: \`<td class="mod"><a href="../ship-dossiers/<newcomer-slug>.html">Ship</a></td>\`. The Pros & cons cell must be OF THE NEWCOMER **vs this hull** — read the newcomer's dossier (guides/ships/ship-dossiers/<newcomer-slug>.html) for a fair 1-pro / 1-con and its role stat + rating (rating must match data/ship-ratings/${role}.json). Terse, operator-grade, no hype.
4. Do NOT touch the baseline "this" row, other sections, the §04 prose paragraphs' counts unless a hard number is stated, or add any CSS. Do not run git or build scripts.

Return {slug:"${slug}", added:[<newcomer ships inserted>], skipped:[<ship: reason>], note:"<one line>"}.`

phase('Edit')
const results = await pipeline(
  dossiers,
  (slug) => agent(prompt(slug), { label: `${role}:${slug}`, phase: 'Edit', schema: SCHEMA })
)
const ok = results.filter(Boolean)
const totalAdded = ok.reduce((s, r) => s + (r.added ? r.added.length : 0), 0)
log(`edited ${ok.length}/${dossiers.length} dossiers, ${totalAdded} rows added`)
return { role, edited: ok.length, rowsAdded: totalAdded, results: ok }
