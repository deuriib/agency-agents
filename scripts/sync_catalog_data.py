#!/usr/bin/env python3
"""Keep the bundled package catalog in sync with the repository source of truth.

The CLI resolves its catalog from the current directory when it is a repository
checkout, and from ``agency_agents.data`` when it is installed from PyPI. That
bundled copy lives under ``src/agency_agents/data/`` and is generated here, then
committed, so ``uv build`` always ships a complete catalog without a build-time
hook. CI runs ``--check`` to fail the build when the bundle drifts from the
source of truth.

Only the standard library is used so the script runs on a bare ``python3`` as
well as under ``uv run``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "src" / "agency_agents" / "data"

# Fixed catalog entries that are not division directories.
FIXED_SOURCES = ("tools.json", "divisions.json", "strategy")

_INIT_PY = (
    '"""Bundled agent catalog.\n\nSynced from the repository root by '
    "``scripts/sync_catalog_data.py``; do not edit by hand.\n\"\"\"\n"
)


def _division_names() -> list[str]:
    divisions = json.loads((ROOT / "divisions.json").read_text(encoding="utf-8"))
    return sorted(divisions["divisions"].keys())


def _source_paths() -> list[Path]:
    paths = [ROOT / name for name in FIXED_SOURCES]
    paths.extend(ROOT / name for name in _division_names())
    return paths


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_bytecode(path: Path) -> bool:
    """True for Python bytecode caches, which are build artifacts, not catalog data."""
    return path.suffix == ".pyc" or "__pycache__" in path.parts


def _source_manifest() -> dict[str, str]:
    """Map each catalog file's repo-relative path to its content hash."""
    manifest: dict[str, str] = {}
    for source in _source_paths():
        if source.is_dir():
            for path in sorted(source.rglob("*")):
                if path.is_file() and not _is_bytecode(path):
                    manifest[str(path.relative_to(ROOT))] = _sha256(path)
        elif not _is_bytecode(source):
            manifest[str(source.relative_to(ROOT))] = _sha256(source)
    return manifest


def _bundled_manifest() -> dict[str, str]:
    """Map each bundled file's data-relative path to its content hash."""
    manifest: dict[str, str] = {}
    for path in sorted(DATA_DIR.rglob("*")):
        if path.is_file() and path.name != "__init__.py" and not _is_bytecode(path):
            manifest[str(path.relative_to(DATA_DIR))] = _sha256(path)
    return manifest


def _rebuild() -> None:
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    DATA_DIR.mkdir(parents=True)
    (DATA_DIR / "__init__.py").write_text(_INIT_PY, encoding="utf-8")
    for source in _source_paths():
        if source.is_dir():
            shutil.copytree(source, DATA_DIR / source.name)
        else:
            shutil.copy2(source, DATA_DIR / source.name)


def _report_diff(expected: dict[str, str], actual: dict[str, str]) -> None:
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = sorted(
        path for path in set(expected) & set(actual) if expected[path] != actual[path]
    )
    if missing:
        print(f"missing ({len(missing)}):", *missing, sep="\n  ", file=sys.stderr)
    if extra:
        print(f"stale ({len(extra)}):", *extra, sep="\n  ", file=sys.stderr)
    if changed:
        print(f"changed ({len(changed)}):", *changed, sep="\n  ", file=sys.stderr)


def _sync() -> int:
    _rebuild()
    count = len(_bundled_manifest())
    print(f"synced {count} catalog files -> {DATA_DIR.relative_to(ROOT)}")
    return 0


def _check() -> int:
    if not (DATA_DIR / "__init__.py").is_file():
        print("missing bundled package marker: src/agency_agents/data/__init__.py", file=sys.stderr)
        return 1
    expected = _source_manifest()
    actual = _bundled_manifest()
    if expected == actual:
        print(f"catalog bundle in sync ({len(actual)} files)")
        return 0
    print(
        "catalog bundle is out of sync with the repository root.\n"
        "Run `python scripts/sync_catalog_data.py` and commit the result.",
        file=sys.stderr,
    )
    _report_diff(expected, actual)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the bundle is in sync and exit non-zero on drift (CI mode)",
    )
    args = parser.parse_args(argv)
    return _check() if args.check else _sync()


if __name__ == "__main__":
    raise SystemExit(main())
