#!/usr/bin/env bash
# convert-dossier-rating-cards.sh
# One-off migration: convert each ship dossier's briefing rating card from the
# dial WHEEL form to the number + ladder-bar form.
#
#   FROM: <div class="stat rating"><div class="dial" style="--v:NN"><div class="num">NN<small>/100</small></div></div><div class="l">… suitability</div></div>
#   TO:   <div class="stat"><div class="n">NN<small>/100</small></div><div class="bar mini"><i style="--pct:NN"></i></div></div>
#
# Idempotent: only rewrites cards still in the wheel form; re-running is a no-op.
# Paths resolve relative to the script, so it runs from anywhere.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="$ROOT/guides/ships/dossiers"

python3 - "$DIR" <<'PY'
import re, sys, glob, os
d = sys.argv[1]
pat = re.compile(
    r'<div class="stat rating"><div class="dial" style="--v:(\d+)">'
    r'<div class="num">\d+<small>/100</small></div></div>'
    r'<div class="l">[^<]*</div></div>'
)
def repl(m):
    n = m.group(1)
    return (f'<div class="stat"><div class="n">{n}<small>/100</small></div>'
            f'<div class="bar mini"><i style="--pct:{n}"></i></div></div>')
changed = 0
for f in sorted(glob.glob(os.path.join(d, '*.html'))):
    s = open(f, encoding='utf-8').read()
    s2, n = pat.subn(repl, s)
    if n:
        open(f, 'w', encoding='utf-8').write(s2)
        changed += 1
total = len(glob.glob(os.path.join(d, '*.html')))
print(f"rating cards converted: {changed} / {total} dossiers")
PY
