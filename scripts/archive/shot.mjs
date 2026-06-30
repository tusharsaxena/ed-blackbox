// scripts/shot.mjs — full-page screenshot of a local HTML file.
// Usage: node scripts/shot.mjs <abs-html-path> <out.png>
import { chromium } from 'playwright';
const [, , input, out] = process.argv;
if (!input || !out) { console.error('usage: shot.mjs <html> <out.png>'); process.exit(2); }
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 2000 } });
await page.goto('file://' + input, { waitUntil: 'networkidle' });
await page.screenshot({ path: out, fullPage: true });
await browser.close();
console.log('shot →', out);
