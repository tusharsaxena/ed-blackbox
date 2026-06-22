// scripts/classify-card-groups.mjs — set each .cards container's width class by its content.
// Rule (by the LARGEST card's word count in the group, applied to the whole container):
//   <75 words → "cards" · 75–150 → "cards wide" · 150+ → "cards extra-wide".
// Word count = each card's rendered textContent (title + eyebrow + body). Class-only edits,
// so it never changes page content (gate-neutral). Re-runnable as content evolves.
// Usage: node scripts/classify-card-groups.mjs [dir]   (default: guides)
import { chromium } from 'playwright';
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const root = process.argv[2] || 'guides';
const walk = (d) => readdirSync(d).flatMap((e) => {
  const p = join(d, e);
  return statSync(p).isDirectory() ? walk(p) : p.endsWith('.html') ? [p] : [];
});
const cls = (max) => (max >= 150 ? 'cards extra-wide' : max >= 75 ? 'cards wide' : 'cards');

const files = walk(root);
const browser = await chromium.launch();
const page = await browser.newPage();
let totalGroups = 0, changed = 0, mismatches = 0;
for (const file of files) {
  await page.goto('file://' + process.cwd() + '/' + file, { waitUntil: 'domcontentloaded' });
  const maxes = await page.$$eval('.cards', (conts) => conts.map((c) => {
    const counts = [...c.children].filter((el) => el.classList.contains('card'))
      .map((card) => (card.textContent.trim().match(/\S+/g) || []).length);
    return counts.length ? Math.max(...counts) : 0;
  }));
  if (!maxes.length) continue;
  totalGroups += maxes.length;
  const want = maxes.map(cls);
  let src = readFileSync(file, 'utf8'), i = 0, diffs = [];
  src = src.replace(/<div class="cards[^"]*">/g, (m) => {
    const cur = m.match(/class="([^"]*)"/)[1], w = want[i];
    if (cur !== w) diffs.push(`  ${cur}  ->  ${w}   (max ${maxes[i]}w)`);
    i++; return `<div class="${w}">`;
  });
  if (i !== maxes.length) { console.log(`!! MISMATCH ${file}: DOM ${maxes.length} vs source ${i} — skipped`); mismatches++; continue; }
  if (diffs.length) { writeFileSync(file, src); changed += diffs.length; console.log(`${file}:`); diffs.forEach((d) => console.log(d)); }
}
await browser.close();
console.log(`\n${totalGroups} card groups across ${files.length} files · ${changed} reclassified · ${mismatches} mismatch(es)`);
