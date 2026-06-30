// scripts/fingerprint.mjs — content fingerprint of a guide page (chrome-excluded).
// Usage: node scripts/fingerprint.mjs <abs-html-path>  > fp.json
import { chromium } from 'playwright';
const [, , input] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('file://' + input, { waitUntil: 'load' });
const fp = await page.evaluate(() => {
  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const head = document.querySelector('header.hero, header.masthead');
  const title = norm(head && (head.querySelector('h1') || {}).textContent);
  const subtitle = norm(head && (head.querySelector('.lede, .subtitle') || {}).textContent);
  // content sections only — exclude the credits/sources section (chrome-ish, may be restyled)
  const sections = [...document.querySelectorAll('.wrap > section, .wrap section')]
    .filter((s) => !s.classList.contains('credits'))
    .map((s) => ({ id: s.id || '', text: norm(s.textContent) }));
  const ids = [...document.querySelectorAll('[id]')].map((e) => e.id).filter(Boolean);
  return { title, subtitle, sections, ids };
});
console.log(JSON.stringify(fp));
await browser.close();
