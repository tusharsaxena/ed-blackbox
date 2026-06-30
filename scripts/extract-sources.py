#!/usr/bin/env python3
"""extract-sources.py — one-time bootstrap: HTML credits sections -> data/sources/ canon.

Parses the <section class="credits"> block of every credits-bearing guide and writes the
canonical data file at data/sources/<path-mirroring-guides>.json:

    { "page": "guides/activities/exploration.html",
      "lead": ["Figures on this page are verified against the sources below."],
      "sources": [ { "label", "what", "url", "display" }, ... ] }

The Sources section is EXTERNAL references only: inline internal cross-links
(<a href="#..."> / relative / .html) embedded in the description prose are unwrapped to
plain text, and every such strip is reported for review.

Text (label/what/display) is captured VERBATIM — entities (&mdash;, &rarr;) and literal
em-dashes are preserved exactly so build-sources.py round-trips cleanly.

Usage:
    python3 scripts/extract-sources.py            # write all data files
    python3 scripts/extract-sources.py --check    # report only, write nothing

After the canon exists this script is reference-only; edit the JSON and run build-sources.py.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sources_lib as L  # noqa: E402


def main():
    check = "--check" in sys.argv
    pages = list(L.iter_credits_pages())
    written = 0
    total_rows = 0
    strips = []  # (page, field, before, after)

    for page in pages:
        text = L.read_text(page)
        parsed = L.parse_credits(text)
        page_rel = str(page.resolve().relative_to(L.ROOT)).replace("\\", "/")

        leads = []
        for lead in parsed["leads"]:
            clean, n = L.strip_internal_links(lead)
            if n:
                strips.append((page_rel, "lead", lead, clean))
            leads.append(clean)

        sources = []
        for r in parsed["rows"]:
            entry = {}
            for field in ("label", "what", "url", "display"):
                val = r[field]
                if field != "url":
                    val, n = L.strip_internal_links(val)
                    if n:
                        strips.append((page_rel, f'{field}: {r["label"]}', r[field], val))
                entry[field] = val
            sources.append(entry)
            total_rows += 1

        data = {"page": page_rel, "lead": leads, "sources": sources}
        if parsed["tag"]:
            data["tag"] = parsed["tag"]
        out_path = L.page_to_data_path(page_rel)
        payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"

        if check:
            print(f"  would write {out_path.relative_to(L.ROOT)}  "
                  f"({len(sources)} sources, {len(leads)} lead)")
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(payload, encoding="utf-8")
            written += 1

    print()
    print(f"pages: {len(pages)}   source rows: {total_rows}")
    if strips:
        print(f"\nstripped {len(strips)} internal cross-link(s) (Sources = external only):")
        for page_rel, where, before, after in strips:
            print(f"  {page_rel}  [{where}]")
    if check:
        print("\n--check: nothing written.")
    else:
        print(f"\nwrote {written} data file(s) under {L.DATA_DIR.relative_to(L.ROOT)}/")


if __name__ == "__main__":
    main()
