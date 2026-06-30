// scripts/fix-step-tuples.mjs — repair the malformed step-data generator bug.
//
// A number of dossiers render their "A-rated upgrade plan" step list as a raw Python
// tuple repr instead of unpacked markup, e.g.:
//   <li><span class="stepnum">1</span>('FSD &rarr; A', 'Jump range is everything.', '~150k Cr')</li>
// Each tuple is (action, rationale, cost). This script unpacks every such <li> into
// readable markup, preserving the step number and all inner HTML entities:
//   <li><span class="stepnum">1</span><b>FSD &rarr; A</b> &mdash; Jump range is everything. <span class="acc">~150k Cr</span></li>
// The cost uses .acc (accent text) — a class that renders on both legacy inline-CSS
// pages and migrated design-system pages, so the fix is correct before AND after migration.
//
// Quote-aware: fields are single- OR double-quoted (apostrophe-bearing fields use "..."),
// and may contain commas and HTML entities — so this matches quoted fields, not a split.
//
// Usage: node scripts/fix-step-tuples.mjs <file.html> [more.html ...]
//        node scripts/fix-step-tuples.mjs            # defaults to guides/**/*.html
import { readFileSync, writeFileSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

// stepnum span, then ( field , field , field ) — each field single- or double-quoted.
const QF = `(?:'([^']*)'|"([^"]*)")`;
const RE = new RegExp(
  `(<span class="stepnum">\\d+</span>)\\(\\s*${QF}\\s*,\\s*${QF}\\s*,\\s*${QF}\\s*\\)`,
  'g'
);

let files = process.argv.slice(2);
if (files.length === 0) {
  files = execSync(`find "${ROOT}/guides" -name '*.html'`, { encoding: 'utf8' })
    .split('\n').filter(Boolean);
}

let totalReplacements = 0, totalFiles = 0;
for (const f of files) {
  const src = readFileSync(f, 'utf8');
  let n = 0;
  const out = src.replace(RE, (_m, span, a1, a2, b1, b2, c1, c2) => {
    n++;
    const action = a1 ?? a2, rationale = b1 ?? b2, cost = c1 ?? c2;
    return `${span}<b>${action}</b> &mdash; ${rationale} <span class="acc">${cost}</span>`;
  });
  if (n > 0) {
    writeFileSync(f, out);
    totalReplacements += n; totalFiles++;
    console.log(`  ${n.toString().padStart(3)}  ${f.replace(ROOT + '/', '')}`);
  }
}
console.log(`\nfixed ${totalReplacements} step items across ${totalFiles} files`);
