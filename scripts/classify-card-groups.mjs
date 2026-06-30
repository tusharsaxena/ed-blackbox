// scripts/classify-card-groups.mjs — give every .cards grid an explicit column-count class.
// The class names how many cards share one content-width row: .four · .three · .two · .one.
// Per container:
//   • already has an explicit count (one|two|three|four) → left untouched (author override wins)
//   • legacy width name  .cards.extra-wide → .cards.one  ·  .cards.wide → .cards.two
//   • plain .cards → .cards.<n>  where n = min(card count, 4)
// So a plain section of 3 cards becomes .three, 4 (or more) becomes .four. Pick fewer/wider columns
// by hand (set .two/.one) when the cards are long and prose-heavy. Class-only edits, gate-neutral,
// re-runnable. Usage: node scripts/classify-card-groups.mjs [dir]   (default: guides)
import { chromium } from 'playwright';
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const root = process.argv[2] || 'guides';
const walk = (d) => readdirSync(d).flatMap((e) => {
  const p = join(d, e);
  return statSync(p).isDirectory() ? walk(p) : p.endsWith('.html') ? [p] : [];
});
const NAMES = { 1: 'one', 2: 'two', 3: 'three', 4: 'four' };
const target = (cls, count) => {
  if (/\b(one|two|three|four)\b/.test(cls)) return cls;          // explicit count — respect it
  if (/\bextra-wide\b/.test(cls)) return 'cards one';
  if (/\bwide\b/.test(cls)) return 'cards two';
  return count < 1 ? 'cards' : `cards ${NAMES[Math.min(count, 4)]}`;
};

const files = walk(root);
const browser = await chromium.launch();
const page = await browser.newPage();
let totalGroups = 0, changed = 0, mismatches = 0;
for (const file of files) {
  await page.goto('file://' + process.cwd() + '/' + file, { waitUntil: 'domcontentloaded' });
  const counts = await page.$$eval('.cards', (conts) => conts.map((c) =>
    [...c.children].filter((el) => el.classList.contains('card')).length));
  if (!counts.length) continue;
  totalGroups += counts.length;
  let src = readFileSync(file, 'utf8'), i = 0, diffs = [];
  src = src.replace(/<div class="(cards[^"]*)">/g, (m, cur) => {
    const w = target(cur, counts[i]);
    if (cur !== w) diffs.push(`  ${cur}  ->  ${w}   (${counts[i]} cards)`);
    i++; return `<div class="${w}">`;
  });
  if (i !== counts.length) { console.log(`!! MISMATCH ${file}: DOM ${counts.length} vs source ${i} — skipped`); mismatches++; continue; }
  if (diffs.length) { writeFileSync(file, src); changed += diffs.length; console.log(`${file}:`); diffs.forEach((d) => console.log(d)); }
}
await browser.close();
console.log(`\n${totalGroups} card groups across ${files.length} files · ${changed} reclassified · ${mismatches} mismatch(es)`);
