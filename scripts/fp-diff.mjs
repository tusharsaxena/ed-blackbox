// scripts/fp-diff.mjs — assert content invariance between two fingerprints.
// Usage: node scripts/fp-diff.mjs <before.json> <after.json>
import { readFileSync } from 'node:fs';
const [, , a, b] = process.argv;
const before = JSON.parse(readFileSync(a, 'utf8'));
const after = JSON.parse(readFileSync(b, 'utf8'));
const problems = [];
if (before.title !== after.title) problems.push(`title changed:\n  - ${before.title}\n  + ${after.title}`);
if (before.subtitle !== after.subtitle) problems.push(`subtitle changed`);
// no pre-existing id may disappear
const afterIds = new Set(after.ids);
for (const id of before.ids) if (!afterIds.has(id)) problems.push(`MISSING id: #${id}`);
// section text must match by id (order-independent), and all old sections must still exist
const afterById = new Map(after.sections.map((s) => [s.id, s.text]));
for (const s of before.sections) {
  if (!afterById.has(s.id)) { problems.push(`MISSING section: #${s.id}`); continue; }
  if (afterById.get(s.id) !== s.text) problems.push(`TEXT changed in #${s.id}`);
}
if (problems.length) { console.error('FAIL content invariance:\n' + problems.join('\n')); process.exit(1); }
console.log('PASS content invariant'); process.exit(0);
