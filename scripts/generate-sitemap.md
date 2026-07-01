# generate-sitemap.py

Build `sitemap.xml` at the **repo root** (served at `https://edblackbox.com/sitemap.xml`).

## Where it lives & why

The sitemap goes at the site root because that's the default path crawlers probe and the
only location permitted to reference every URL on the domain. Since the repo is served
with its root as the web root (`CNAME` = `edblackbox.com`; `guides/index.html` is the
landing page and the root `index.html` redirects there), `sitemap.xml` at the repo root
maps to `https://edblackbox.com/sitemap.xml`.

## What it lists

- One `<url>` per `guides/**/*.html` (199 total).
- The landing page is emitted as the canonical directory URL `https://edblackbox.com/guides/`
  (priority `1.0`), **not** `/guides/index.html` — matching the `<link rel="canonical">` in
  the root redirect. Every other guide is listed by its real `.html` URL (priority `0.7`).
- `<lastmod>` is read from each page's masthead `Updated <b>YYYY-MM-DD</b>` stamp (kept in
  sync by `set-last-updated.py`); pages without a stamp fall back to today.
- The root `index.html` is a `noindex` redirect and is **excluded**.

## Usage

```bash
python3 scripts/generate-sitemap.py            # write sitemap.xml
python3 scripts/generate-sitemap.py --check    # print to stdout, write nothing
```

## When to re-run

After adding/removing/renaming any guide page, or after bumping the last-updated dates
(`set-last-updated.py`). Deterministic and idempotent.

> Optional companion: a root `robots.txt` with a `Sitemap: https://edblackbox.com/sitemap.xml`
> line makes the sitemap discoverable without Search Console submission. Not created by this
> script.
