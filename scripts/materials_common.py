#!/usr/bin/env python3
# materials_common.py — shared loaders + helpers for the materials data pipeline.
#
# Canonical data/materials/ is verbatim EDCD/FDevIDs (read-only). Project overlays
# (corrections.json, editorial.json) live in data/materials-extra/. Imported by
# build-materials.py and audit-materials.py. Stdlib only; paths resolve relative to
# this file. See docs/superpowers/specs/2026-06-30-edcd-reference-data-pipelines-design.md.

import csv
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "materials"
EXTRA = ROOT / "data" / "materials-extra"

DISPLAYED_TYPES = ("Raw", "Manufactured", "Encoded")
GRADES_FOR = {"Raw": (1, 2, 3, 4), "Manufactured": (1, 2, 3, 4, 5), "Encoded": (1, 2, 3, 4, 5)}


def _load_json(name):
    """Load a data/materials-extra/<name> overlay, or {} if it does not exist yet."""
    p = EXTRA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def load_materials():
    """All rows of material.csv as dicts {id, symbol, rarity:int, type, category, name}."""
    rows = []
    with (DATA / "material.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append({
                "id": r["id"], "symbol": r["symbol"], "rarity": int(r["rarity"]),
                "type": r["type"], "category": r["category"], "name": r["name"],
            })
    return rows


def _corrections():
    return _load_json("corrections.json")


def raw_group_labels():
    """Map a numeric Raw category ('1'..'7') to its display label ('Group 1'..)."""
    m = _corrections().get("raw_group_labels")
    return m or {str(i): f"Group {i}" for i in range(1, 8)}


def category_order(type_name):
    """Displayed categories for a type, in render order (None -> fall back to sorted)."""
    return _corrections().get("category_order", {}).get(type_name)


def is_displayed(row):
    """True unless the row is a deferred (Guardian/Thargoid 'None'-category, or an
    explicitly display:false) material — captured in data but not rendered on the page."""
    if row["category"] == "None":
        return False
    if _corrections().get("display", {}).get(row["name"]) is False:
        return False
    return True


def displayed_grid(type_name):
    """Ordered category rows for a displayed type. Each row is
    {label, category, cells:{1..5: name|''}}. Raw populates G1-4 (G5 always '')."""
    rows = [r for r in load_materials() if r["type"] == type_name and is_displayed(r)]
    cats = {}
    for r in rows:
        cats.setdefault(r["category"], {})[r["rarity"]] = r["name"]
    labels = raw_group_labels() if type_name == "Raw" else None
    order = category_order(type_name) or sorted(cats)
    grid = []
    for cat in order:
        cells = {g: cats.get(cat, {}).get(g, "") for g in (1, 2, 3, 4, 5)}
        label = labels[cat] if labels else cat
        grid.append({"label": label, "category": cat, "cells": cells})
    return grid


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def esc(s):
    """HTML-escape matching the page's entity set (&#x27; &quot; &amp; &lt; &gt;)."""
    return html.escape(s, quote=True)
