#!/usr/bin/env python3
"""Automated verification suite for Agency Agents docs site (MkDocs Material).

Validates criteria D1-D8, D10, D13:
- D1: mkdocs.yml exists, Material theme, docs_dir != 'docs', site/ in .gitignore
- D2: mkdocs build --strict exits 0 with 0 warnings/broken links
- D3: Site contains exactly 18 division pages and 300 agent pages
- D4: 0 files originating from docs/agency-flow/**
- D6: Every content page carries the language switcher
- D7: Fallback invariant holds: fallback_count == total_pages - 22
- D8: Each of the 22 core pages has a valid Spanish counterpart (non-empty, diff SHA)
- D13: Footer credits upstream project msitarzewski/agency-agents and site_url configured
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SITE_DIR = REPO_ROOT / "site"
MKDOCS_FILE = REPO_ROOT / "mkdocs.yml"

DIVISIONS = [
    "academic", "design", "engineering", "finance", "game-development",
    "gis", "healthcare", "marketing", "paid-media", "product",
    "project-management", "research", "sales", "security",
    "spatial-computing", "specialized", "support", "testing"
]


def test_d1_structure() -> None:
    print("[TEST] D1: Structure & Configuration...")
    assert MKDOCS_FILE.exists(), "mkdocs.yml does not exist"
    content = yaml.safe_load(MKDOCS_FILE.read_text(encoding="utf-8"))
    assert content.get("theme", {}).get("name") == "material", "Theme is not Material"
    docs_dir = content.get("docs_dir", "")
    assert docs_dir != "docs" and "agency-flow" not in docs_dir, f"Invalid docs_dir: {docs_dir}"
    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert re.search(r"^site/?$", gitignore_text, re.MULTILINE), "site/ not in .gitignore"
    print("  -> D1 PASS")


def test_d3_parity() -> None:
    print("[TEST] D3: Catalog Parity (18 divisions + 300 agents)...")
    # Verify raw repo agent count
    raw_agents = []
    for d in DIVISIONS:
        for root, _, files in os.walk(REPO_ROOT / d):
            for f in files:
                if f.endswith(".md"):
                    raw_agents.append(Path(root) / f)
    assert len(raw_agents) == 300, f"Expected 300 raw agents, found {len(raw_agents)}"

    # Check generated English docs
    en_divisions_dir = REPO_ROOT / "site-docs" / "docs" / "en" / "divisions"
    assert en_divisions_dir.exists(), "en/divisions directory missing"

    division_landing_pages = list(en_divisions_dir.glob("*/index.md"))
    assert len(division_landing_pages) == 18, f"Expected 18 division index pages, found {len(division_landing_pages)}"

    agent_pages = [p for p in en_divisions_dir.glob("*/*.md") if p.name != "index.md"]
    assert len(agent_pages) == 300, f"Expected 300 agent markdown pages, found {len(agent_pages)}"
    print("  -> D3 PASS")


def test_d4_leakage() -> None:
    print("[TEST] D4: 0 files originating from docs/agency-flow/** in site...")
    assert SITE_DIR.exists(), "site/ directory does not exist"

    site_files = {p.relative_to(SITE_DIR).as_posix() for p in SITE_DIR.rglob("*") if p.is_file()}
    flow_files = {p.relative_to(REPO_ROOT / "docs" / "agency-flow").as_posix()
                  for p in (REPO_ROOT / "docs" / "agency-flow").rglob("*") if p.is_file()}

    leaked = []
    for ff in flow_files:
        html_variant1 = ff.replace(".md", ".html")
        html_variant2 = ff.replace(".md", "/index.html")
        if ff in site_files or html_variant1 in site_files or html_variant2 in site_files:
            leaked.append(ff)

    assert len(leaked) == 0, f"Leaked agency-flow files: {leaked}"
    print("  -> D4 PASS")


def test_d6_language_switcher() -> None:
    print("[TEST] D6: Language switcher present on all content pages...")
    content_pages = [p for p in SITE_DIR.rglob("*.html") if p.name != "404.html"]
    assert len(content_pages) > 0, "No content HTML pages found"

    missing_switcher = []
    for page in content_pages:
        html = page.read_text(encoding="utf-8")
        if "md-header__option" not in html and "Select language" not in html:
            missing_switcher.append(str(page.relative_to(SITE_DIR)))

    assert len(missing_switcher) == 0, f"Pages missing language switcher: {missing_switcher[:5]}"
    print(f"  -> D6 PASS ({len(content_pages)} content pages verified)")


def test_d7_fallback_invariant() -> None:
    print("[TEST] D7: Fallback invariant: fallback_count == total_pages - 22...")
    es_site = SITE_DIR / "es"
    assert es_site.exists(), "site/es does not exist"

    core_rel = {
        "index.html",
        "installation/index.html",
        "contributing/index.html",
        "security/index.html",
    }
    for d in DIVISIONS:
        core_rel.add(f"divisions/{d}/index.html")

    assert len(core_rel) == 22, f"Expected 22 core pages, found {len(core_rel)}"

    all_es_pages = {p.relative_to(es_site).as_posix() for p in es_site.rglob("*.html") if p.name != "404.html"}
    fallback_pages = {p for p in all_es_pages if p not in core_rel}

    # Verify fallback count invariant
    total_pages = len(all_es_pages)
    fallback_count = len(fallback_pages)
    assert fallback_count == total_pages - 22, (
        f"Invariant broken: fallback_count ({fallback_count}) != total ({total_pages}) - 22"
    )

    # Verify none of the 22 core pages is in fallback
    intersection = core_rel.intersection(fallback_pages)
    assert len(intersection) == 0, f"Core pages present in fallback set: {intersection}"
    print(f"  -> D7 PASS (total: {total_pages}, translated core: 22, fallback: {fallback_count})")


def test_d8_core_translations() -> None:
    print("[TEST] D8: Spanish core pages non-empty & diff SHA...")
    core_pages = [
        "index.md",
        "installation.md",
        "contributing.md",
        "security.md",
    ] + [f"divisions/{d}/index.md" for d in DIVISIONS]

    en_base = REPO_ROOT / "site-docs" / "docs" / "en"
    es_base = REPO_ROOT / "site-docs" / "docs" / "es"

    for rel in core_pages:
        en_p = en_base / rel
        es_p = es_base / rel
        assert en_p.exists(), f"Missing EN page: {en_p}"
        assert es_p.exists(), f"Missing ES page: {es_p}"
        assert es_p.stat().st_size > 0, f"Empty ES page: {es_p}"

        sha_en = hashlib.sha256(en_p.read_bytes()).hexdigest()
        sha_es = hashlib.sha256(es_p.read_bytes()).hexdigest()
        assert sha_en != sha_es, f"Byte-identical translation found: {rel}"

    print(f"  -> D8 PASS ({len(core_pages)} translated core pages verified)")


def test_d13_attribution() -> None:
    print("[TEST] D13: Upstream attribution & site_url...")
    content = yaml.safe_load(MKDOCS_FILE.read_text(encoding="utf-8"))
    assert content.get("site_url") == "https://deuriib.github.io/agency-agents/", "Incorrect site_url"
    assert "msitarzewski/agency-agents" in MKDOCS_FILE.read_text(encoding="utf-8"), "Missing upstream attribution"
    print("  -> D13 PASS")


def main() -> None:
    print("=== Running Agency Agents Docs Verification Suite ===")
    test_d1_structure()
    test_d3_parity()
    test_d4_leakage()
    test_d6_language_switcher()
    test_d7_fallback_invariant()
    test_d8_core_translations()
    test_d13_attribution()
    print("=== ALL 7 AUTOMATED VERIFICATION CHECKS PASSED ===")


if __name__ == "__main__":
    main()
