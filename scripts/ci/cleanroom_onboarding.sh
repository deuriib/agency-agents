#!/usr/bin/env bash
# Clean-room onboarding harness — the M1/M5/M6 instrument.
#
# Runs the documented golden path against a disposable container that holds no
# prior copy of the repo, no language runtime from this project, and no cached
# credential, then prints one timing line per step.
#
# The runbook's definition of a clean machine is proven here rather than
# asserted: the pre-run block records an empty work-directory listing and an
# empty `which` transcript, and fails the run if Python, uv or agency-agents is
# already present.
#
# Usage:
#   scripts/ci/cleanroom_onboarding.sh --path scripts/ci/paths/<name>.sh
#
# Options:
#   --path FILE     Shell file holding the documented commands. Required: the
#                   harness never invents a step.
#   --repo PATH     Local repo to clone from. Default: the repo holding this script.
#   --ref REF       Ref to check out. Default: the current branch.
#   --image IMG     Container image. Default: agency-agents-cleanroom:1.
#   --build-image   Rebuild the clean-room image first.
#   --workdir DIR   Empty directory the subject works in. Default: /work.
#   --out FILE      Transcript path. Default: /tmp/cleanroom-<stamp>.log.
#
# Exit codes: 0 all steps exited 0, 1 a step failed, 2 harness misuse.
#
# The transcript this writes is ENGINEER-EXECUTED evidence. It is not a recorded
# session of a human subject and never satisfies G4 clause 4.1 on its own.
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PATH_FILE=""
REPO="${ROOT_DIR}"
REF="$(git -C "${ROOT_DIR}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
IMAGE="agency-agents-cleanroom:1"
BUILD_IMAGE=0
WORKDIR="/work"
OUT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --path) PATH_FILE="${2:-}"; shift 2 ;;
    --repo) REPO="${2:-}"; shift 2 ;;
    --ref) REF="${2:-}"; shift 2 ;;
    --image) IMAGE="${2:-}"; shift 2 ;;
    --build-image) BUILD_IMAGE=1; shift ;;
    --workdir) WORKDIR="${2:-}"; shift 2 ;;
    --out) OUT="${2:-}"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ -z "${PATH_FILE}" ] || [ ! -f "${PATH_FILE}" ]; then
  echo "error: --path must name an existing step file" >&2
  exit 2
fi

# Docker volume sources must be absolute; a relative name is read as a volume.
PATH_FILE="$(cd "$(dirname "${PATH_FILE}")" && pwd)/$(basename "${PATH_FILE}")"
REPO="$(cd "${REPO}" && pwd)"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${OUT:-/tmp/cleanroom-${STAMP}.log}"

# Ship the ref as a self-contained git bundle. Mounting a working tree fails for
# a linked worktree, whose .git file names a host path the container cannot see,
# and a bundle keeps the subject's `git clone` a real clone from a real source.
BUNDLE_DIR="$(mktemp -d)"
trap 'rm -rf "${BUNDLE_DIR}"' EXIT
BUNDLE="${BUNDLE_DIR}/repo.bundle"
if ! git -C "${REPO}" bundle create "${BUNDLE}" "${REF}" >/dev/null 2>&1; then
  echo "error: cannot bundle ref '${REF}' from ${REPO}" >&2
  exit 2
fi

if [ "${BUILD_IMAGE}" -eq 1 ]; then
  echo "building ${IMAGE} from scripts/ci/cleanroom.Dockerfile"
  docker build --tag "${IMAGE}" --file "${ROOT_DIR}/scripts/ci/cleanroom.Dockerfile" "${ROOT_DIR}" || exit 1
fi

# The steps file is mounted read-only and executed inside the container, so the
# documented path is the only thing that runs. Nothing from the host environment
# crosses the boundary except the clone source.
exec > >(tee "${OUT}") 2>&1

echo "# Clean-room onboarding transcript"
echo "harness_start_utc: ${STAMP}"
echo "image: ${IMAGE}"
echo "clone_source: git bundle of ref ${REF}"
echo "path_file: $(basename "${PATH_FILE}")"
echo "executor: ENGINEER-EXECUTED (not a human subject)"
echo

docker run --rm \
  --volume "${BUNDLE}:/src/repo.bundle:ro" \
  --volume "${PATH_FILE}:/onboarding-path.sh:ro" \
  --env "REF=${REF}" \
  --env "CLEAN_WORKDIR=${WORKDIR}" \
  --env "CLEANROOM_IMAGE=${IMAGE}" \
  "${IMAGE}" \
  bash -lc '
set -uo pipefail

# ---- Prove the machine is clean before any documented command runs ----------
mkdir -p "${CLEAN_WORKDIR}"
cd "${CLEAN_WORKDIR}" || exit 1
echo "## Pre-run cleanliness check"
echo "image: ${CLEANROOM_IMAGE}"
echo "workdir: $(pwd)"
echo "workdir listing (expect empty):"
ls -A . 2>/dev/null | sed "s/^/  /"
echo "  [end of listing]"
for binary in git curl uv python3 agency-agents; do
  found="$(command -v "${binary}" 2>/dev/null || true)"
  echo "which ${binary}: ${found:-<absent>}"
done
if [ -n "$(ls -A . 2>/dev/null)" ]; then
  echo "FAIL: the work directory is not empty"
  exit 1
fi
for binary in uv python3 agency-agents; do
  if command -v "${binary}" >/dev/null 2>&1; then
    echo "FAIL: ${binary} is present on a machine that must not have it"
    exit 1
  fi
done
echo "clean: true"
echo

# ---- Execute the documented path, timing every step ------------------------
echo "## Documented path"
step=0
failed=0
step_start=${SECONDS}
run_step() {
  step=$((step + 1))
  local label="$1"; shift
  local start end code
  start=$(date +%s)
  echo "--- step ${step}: ${label}"
  "$@"
  code=$?
  end=$(date +%s)
  echo "step_${step}_label: ${label}"
  echo "step_${step}_exit: ${code}"
  echo "step_${step}_seconds: $((end - start))"
  echo
  if [ "${code}" -ne 0 ]; then
    failed=1
    echo "step_${step}_FAILED: true"
    return 1
  fi
  return 0
}

export PATH="$HOME/.local/bin:$PATH"
# shellcheck disable=SC1091
source /onboarding-path.sh
total=$((SECONDS - step_start))

echo "## Result"
echo "steps_total: ${step}"
echo "steps_failed: ${failed}"
echo "totals_seconds: ${total}"
echo "harness_end_utc: $(date -u +%Y%m%dT%H%M%SZ)"
exit "${failed}"
'

status=$?
echo
echo "transcript: ${OUT}"
echo "harness_exit: ${status}"
exit "${status}"
