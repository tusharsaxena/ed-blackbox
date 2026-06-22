// scripts/restructure-app-cards.mjs — one-shot restructure of the third-party-apps tool cards.
// Per card: drop the per-domain accent (→ plain amber .card), add a stable id ("app-<slug>"),
// drop the decorative .c-eyebrow, move the .pill tag onto its own .card-tags row under the
// title, and convert the trailing "Open ▸" link into a right-aligned ↗ glyph in the head.
// Usage: node scripts/restructure-app-cards.mjs <abs-html-path>
import { readFileSync, writeFileSync } from 'node:fs';
const file = process.argv[2];
if (!file) { console.error('usage: restructure-app-cards.mjs <file>'); process.exit(2); }
let html = readFileSync(file, 'utf8');

const decode = (s) => s.replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/&mdash;|&ndash;/g, '-')
  .replace(/&middot;/g, ' ').replace(/&[a-z]+;/g, '').trim();
const used = new Set();
const slugify = (title) => {
  let base = decode(title).toLowerCase().replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  let s = 'app-' + base; let n = 2;
  while (used.has(s)) s = `app-${base}-${n++}`;
  used.add(s); return s;
};

const CARD = /<article class="card[^"]*">([\s\S]*?)<\/article>/g;
const CHEAD = /<div class="c-head"><h3>([\s\S]*?)<\/h3><span class="c-eyebrow">[\s\S]*?<\/span><span class="(pill [a-z]+)">([\s\S]*?)<\/span><\/div>/;
const OPENP = /\s*<p><a(?: href="([^"]*)")?[^>]*>(?:Open|Closed)[^<]*<\/a><\/p>/;

let n = 0, anomalies = [];
html = html.replace(CARD, (whole, inner) => {
  const ch = inner.match(CHEAD);
  if (!ch) { anomalies.push(whole.slice(0, 80)); return whole; }
  const [, title, pillClass, pillText] = ch;
  const open = inner.match(OPENP);
  const href = open && open[1];
  const slug = slugify(title);
  const aria = decode(title).replace(/"/g, '');
  const ext = href ? `<a class="cb-ext" href="${href}" aria-label="Open ${aria}">&#8599;</a>` : '';
  let body = inner.replace(CHEAD, '').replace(OPENP, '').trim();
  n++;
  return `<article class="card" id="${slug}">\n` +
    `        <div class="c-head"><h3>${title}</h3>${ext}</div>\n` +
    `        <div class="card-tags"><span class="${pillClass}">${pillText}</span></div>\n` +
    `        ${body}\n      </article>`;
});
writeFileSync(file, html);
console.log(`restructured ${n} cards`);
if (anomalies.length) { console.log('ANOMALIES (unmatched c-head):'); anomalies.forEach((a) => console.log('  ' + a)); }
