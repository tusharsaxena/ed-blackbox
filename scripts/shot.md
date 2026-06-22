# shot.mjs — full-page screenshot tool

Generates a full-page PNG screenshot of a local HTML file using Playwright/Chromium.
Used as the visual safety net for the design-system migration: capture a page before and
after migration, then diff the images to confirm no unintended visual changes.

## Prerequisites

Playwright and Chromium must be installed:

```bash
npm install           # installs playwright devDependency
npx playwright install chromium
```

Chromium also requires system libraries on Linux/WSL2. If the browser fails to launch
with a shared-library error, install them with:

```bash
sudo apt-get install -y libnspr4 libnss3 libasound2t64
```

## Usage

```bash
node scripts/shot.mjs <abs-html-path> <out.png>
```

- `<abs-html-path>` — absolute path to the HTML file (use `$PWD/...` to build it)
- `<out.png>` — output PNG path (any writable location, e.g. `/tmp/page-before.png`)

## Example

```bash
# Capture before-migration baseline
node scripts/shot.mjs "$PWD/guides/ships/dossiers/adder-exploration.html" /tmp/adder-before.png

# Capture after-migration result
node scripts/shot.mjs "$PWD/guides/ships/dossiers/adder-exploration.html" /tmp/adder-after.png
```

## Output

Prints `shot → <out.png>` on success. The PNG is a full-page render at 1280 px width.

## Notes

- Renders at viewport 1280×2000, then expands to full page height.
- Uses `waitUntil: 'networkidle'` so web fonts and deferred assets settle before capture.
- The script accepts absolute paths only; relative paths will not resolve correctly via
  the `file://` URL scheme.
