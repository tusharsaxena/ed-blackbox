# apply-role-tweaks.py

Apply four role-presentation tweaks across guide pages. Element-targeted and
idempotent; the transform is chosen by each file's path.

## Run
```bash
python3 scripts/apply-role-tweaks.py --dry-run            # preview all 90 pages
python3 scripts/apply-role-tweaks.py                      # apply
python3 scripts/apply-role-tweaks.py --files a.html b...  # one batch
```

## Transforms
| Pages | Change |
|---|---|
| `guides/activities/*.html` | h1 `.role` `Guide` → `Activity Guide`; kicker first segment `Role & Activities` → `Activity Guide`; breadcrumb middle crumb `Activities`(`#section-activities`) → `Systems`(`#section-systems`, classless); mark the **Systems** site-nav link `active`. Breadcrumb/nav edits are scoped to their own `<nav>` so the active class never leaks onto the breadcrumb. |
| `guides/ships/dossiers/*.html` | h1 `.role` gains a role colour class: `<span class="role">` → `<span class="role ac-role-<role>">` (Combat/Exploration/Mining/Trading/Passenger/Multipurpose; `AX Combat` → `ax`). Pairs with the `h1.title .role.ac-role-*` rules in `ed-blackbox.css`. |
| `guides/ships/by-role/*.html` | kicker first segment `Role Dossier` → `Best Ships by Role`. |

Idempotent — re-running makes no further changes. Verify with `verify-links.py`
(links) and a visual check that the dossier role tags pick up the role hue.

> The matching **index** change (moving the *Activity Guides* sub-section under
> *Systems*, above *Combat Venues*, with the quick-nav reorder) lives in
> `generate-guides-index.sh` — re-run that to rebuild `index.html`.
