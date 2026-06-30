# Deployment — custom domain (edblackbox.com)

How the site is published: **GitHub Pages** serving the repo at the apex domain
**`edblackbox.com`** (with `www.edblackbox.com` redirecting to it). Registrar is
**Spaceship** (DNS only); GitHub Pages does the hosting and TLS. For the technical
system model see [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## At a glance

| Thing | Value |
|---|---|
| Hosting | GitHub Pages — repo `github.com/tusharsaxena/ed-blackbox`, branch `master` |
| GitHub Pages target | `tusharsaxena.github.io` |
| Canonical domain | `edblackbox.com` (apex) — set in repo `CNAME` |
| Redirect | `www.edblackbox.com` → `edblackbox.com` (handled by GitHub) |
| Entry path | `/` → `/guides/` via the hand-authored root `index.html` redirect |
| Registrar / DNS | Spaceship (default Spaceship nameservers) |
| TLS | Let's Encrypt, auto-provisioned by GitHub; **Enforce HTTPS** on |

The repo's **`CNAME`** file (one line: `edblackbox.com`) is what binds GitHub Pages to the
apex domain — leave it as-is; GitHub rewrites it if the custom domain is changed in the UI.

---

## 1. GitHub Pages (one-time)

**Settings → Pages** on `tusharsaxena/ed-blackbox`:

1. **Custom domain** = `edblackbox.com` → Save. (This writes `CNAME`; it's already committed.)
2. Wait for the DNS check (Part 2) to pass, then enable **Enforce HTTPS**.

## 2. Spaceship DNS records

**Domains → edblackbox.com → Manage → Advanced DNS** (using Spaceship's default
nameservers). Remove any pre-populated parking/`www` records first, then add:

**Apex `edblackbox.com` — four A records** (host `@`):

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

**Apex IPv6 (recommended) — four AAAA records** (host `@`):

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

**`www` subdomain — one CNAME record:**

```
Host: www   →   tusharsaxena.github.io
```

TTL: default/automatic. These are GitHub Pages' published apex IPs — if GitHub ever changes
them, re-check <https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site>.

## 3. Verify

```bash
dig +short edblackbox.com        # expect the four 185.199.x.153 IPs
dig +short www.edblackbox.com    # expect a CNAME via tusharsaxena.github.io
```

Then confirm all four endpoints resolve and force HTTPS:

- `http://edblackbox.com` → `https://edblackbox.com`
- `https://edblackbox.com`
- `http://www.edblackbox.com` → `https://edblackbox.com`
- `https://www.edblackbox.com`

DNS propagation is usually minutes but can take up to ~24h; the GitHub TLS cert lands a few
minutes after the DNS check goes green.

---

## Troubleshooting

- **Pages DNS check stuck red** — a stale apex A record (often a Spaceship parking IP) is
  still present, or the four A records aren't all there. Re-check Advanced DNS.
- **`Enforce HTTPS` greyed out** — DNS hasn't fully resolved yet, or the cert is still
  provisioning. Wait and refresh the Pages settings.
- **`www` doesn't redirect** — the `www` CNAME is missing or points somewhere other than
  `tusharsaxena.github.io`.
- **Domain shows the wrong site / "improperly configured"** — confirm the repo `CNAME` still
  contains exactly `edblackbox.com` (a Pages rebuild can't drop it; a manual edit can).
