#!/usr/bin/env python3
"""Fail when the runtime ``__version__`` drifts from the project version.

release-please bumps both ``pyproject.toml`` and ``src/agency_agents/__init__.py``
(the latter via an ``extra-files`` entry). This check makes any drift fail the
gate instead of shipping a wheel whose ``agency_agents.__version__`` is stale.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = ROOT / "pyproject.toml"
INIT = ROOT / "src" / "agency_agents" / "__init__.py"

_VERSION_RE = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)


def _project_version() -> str:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return data["project"]["version"]


def _runtime_version() -> str | None:
    match = _VERSION_RE.search(INIT.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def main() -> int:
    project = _project_version()
    runtime = _runtime_version()
    if runtime is None:
        print(f"error: no __version__ assignment found in {INIT}", file=sys.stderr)
        return 1
    if project != runtime:
        print(
            f"version drift: pyproject.toml={project} but __init__.py={runtime}",
            file=sys.stderr,
        )
        return 1
    print(f"versions in sync ({runtime})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
