#!/usr/bin/env bash
# Assert that the catalog lint gate fails on an inconsistency.
#
# Regression guard for defect D2 (docs/dx/baseline.md): `lint` used to print
# "Tools Consistency Errors" and exit 0, so the CI gate reported red text on a
# green run and CONTRIBUTING.md's "fails the build if any of the pieces
# disagree" was false.
#
# The injected tool is schema-valid and differs only in naming a `format` with no
# registered renderer, which is exactly the class of drift the catalog check
# exists to catch. tools.json is restored even when the assertion fails.
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}" || exit 2

BACKUP="$(mktemp)"
cp tools.json "${BACKUP}"
restore() {
  cp "${BACKUP}" tools.json
  rm -f "${BACKUP}"
}
trap restore EXIT

python3 - <<'PY'
import copy
import json

with open("tools.json", encoding="utf-8") as handle:
    catalog = json.load(handle)

bogus = copy.deepcopy(catalog["tools"]["claude-code"])
bogus.update(
    {"kebab": "bogus-tool", "id": "bogusTool", "format": "no-such-format", "order": 999}
)
catalog["tools"]["bogus-tool"] = bogus

with open("tools.json", "w", encoding="utf-8") as handle:
    json.dump(catalog, handle, indent=2)
PY

echo "--- lint with an unrenderable tool format (must fail) ---"
if uv run python -m agency_agents lint; then
  echo "::error::lint exited 0 while reporting a catalog inconsistency (D2 regressed)"
  exit 1
fi

echo "--- lint on the restored, consistent catalog (must pass) ---"
restore
trap - EXIT
uv run python -m agency_agents lint
echo "OK: the lint gate fails on inconsistency and passes when consistent."
