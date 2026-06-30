# drop-empty-arx-section.py

Remove empty "ARX Pre-Built Option" sections from ship dossiers and repair the page.

Most dossiers carried an ARX section that only said no such pre-built exists ("There is no
&lt;role&gt;-specific ARX pre-built …; buy and outfit it normally") — pure filler. Given a list
of dossiers, this script:

1. Deletes the `<section id="section-arx-pre-built-option"> … </section>` block (and an
   immediately-preceding `<!-- sN -->` author comment, if present).
2. Deletes the quick-nav item linking to `#section-arx-pre-built-option`.
3. Renumbers every `<span class="sec-num">NN</span>` and `<span class="qn-side">NN</span>`
   sequentially in document order, so the displayed numbering stays contiguous.

It verifies sec-num count == qn-side count and that the anchor is fully gone, flagging any
file that doesn't reconcile. Idempotent. There are no cross-page links to this anchor.

The keep-vs-delete decision is a judgement call (some hulls have a *real* pre-built — e.g.
the Type-9 Trading Jumpstart, the Lynx Highliner) and was made by a classification pass; this
script only executes a supplied delete-list.

```bash
python3 scripts/drop-empty-arx-section.py --list <newline-delimited-file> --dry-run
python3 scripts/drop-empty-arx-section.py --list <newline-delimited-file>
# then:
bash scripts/generate-anchor-files.sh && python3 scripts/verify-links.py
```
