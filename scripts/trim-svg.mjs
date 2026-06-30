// scripts/trim-svg.mjs — tighten inline diagram <svg> viewBoxes to their content.
// Design-system spec: a figure SVG should leave at most ~5px of empty margin around its
// content on every edge. This loads the page in headless Chromium, measures each
// `figure svg`'s rendered content bounding box (getBBox, in viewBox user units), and
// rewrites its viewBox to `contentBBox` padded by PAD px on all sides. Icon SVGs (no
// xmlns / not inside a figure) are left untouched.
// Usage: node scripts/trim-svg.mjs <abs-html-path> [pad]
import { readFileSync, writeFileSync } from 'node:fs';
import { chromium } from 'playwright';
const [, , input, padArg] = process.argv;
const PAD = Number(padArg ?? 5);
if (!input) { console.error('usage: trim-svg.mjs <abs-html-path> [pad]'); process.exit(2); }

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 1000 } });
await page.goto('file://' + input, { waitUntil: 'networkidle' });
// content bbox + current viewBox for each figure svg, in document order
const boxes = await page.$$eval('figure svg', (svgs, pad) => svgs.map((s) => {
  const b = s.getBBox();
  const vb = `${Math.floor(b.x - pad)} ${Math.floor(b.y - pad)} ${Math.ceil(b.width + pad * 2)} ${Math.ceil(b.height + pad * 2)}`;
  return { old: s.getAttribute('viewBox'), neu: vb };
}), PAD);
await browser.close();

let html = readFileSync(input, 'utf8');
let i = 0, changed = 0;
// rewrite each figure-svg viewBox in order (figure svgs carry xmlns; the icon svg does not)
html = html.replace(/<svg viewBox="[^"]*"(\s+xmlns=)/g, (m, tail) => {
  const box = boxes[i++];
  if (!box) return m;
  if (box.old !== box.neu) changed++;
  return `<svg viewBox="${box.neu}"${tail}`;
});
writeFileSync(input, html);
console.log(`trim-svg: ${changed} of ${boxes.length} figure SVG viewBoxes tightened (pad ${PAD}px)`);
boxes.forEach((b, n) => console.log(`  svg ${n + 1}: ${b.old}  ->  ${b.neu}`));
