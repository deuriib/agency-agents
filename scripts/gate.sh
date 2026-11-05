#!/usr/bin/env bash
# The local gate: one command, the CI job set, cheapest check first.
#
# This is the only pre-push gate anyone needs to know (golden-path step 3). Every
# check is the exact command `.github/workflows/ci.yml` runs, and each one prints
# the CI job it stands in for, so local/CI drift shows up as a diff in the label
# instead of as a surprise red pipeline after pushing.
#
#   ./scripts/gate.sh              full gate, fail-fast — the pre-push command
#   ./scripts/gate.sh --fast       inner loop: no network audit, no coverage floor
#   ./scripts/gate.sh --keep-going run every check even after a failure
#   ./scripts/gate.sh --list       print the checks in order, run nothing
#
# `mise` is optional: the checks are invoked directly, so a machine without mise
# gates the same way CI does. Exit codes: 0 pass, 1 check failed, 2 usage/toolchain.
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

EXIT_FAILED=1
EXIT_USAGE=2

FAST=0
KEEP_GOING=0
LIST_ONLY=0
UV=''
AUDIT_REQ_FILE=''

# ---------------------------------------------------------------------------
# The check table. Order is cheapest-first by measured wall time on this repo
# (warm `uv` cache, 222 tests): see docs/dx/gate.md for the full table and why
# the order is what it is. Each cost below is the figure from that measurement.
# ---------------------------------------------------------------------------
CHECK_IDS=(
  ruff
  runbook-structure
  yamllint
  catalog-lint
  types
  verify-manifest
  catalog-sync
  test
  security-audit
)
CHECK_JOBS=(
  "[ci.yml:lint]"
  "[ci.yml:lint]"
  "[ci.yml:security]"
  "[ci.yml:lint]"
  "[ci.yml:types]"
  "[ci.yml:verify-manifest]"
  "[ci.yml:verify-manifest]"
  "[ci.yml:test]"
  "[ci.yml:security]"
)
CHECK_COSTS=(
  "0.1-1.2s"
  "0.8-0.9s"
  "0.8-1.3s"
  "2-3.2s"
  "0.9s warm, 24s cold"
  "8-15s"
  "0.5-1.5s"
  "14-27s"
  "50-57s, network"
)
CHECK_RERUNS=(
  "uv run ruff check ."
  "uv run python scripts/ci/check_runbook_structure.py"
  "uv run yamllint -d relaxed .github/"
  "uv run python -m agency_agents lint"
  "bash scripts/ci/mypy_ratchet.sh"
  "uv run python -m agency_agents verify --all"
  "uv run python scripts/sync_catalog_data.py --check"
  "uv run pytest -q --cov=agency_agents --cov-branch --cov-report=term-missing --cov-report=xml --cov-fail-under=80"
  "uv export --format requirements-txt --no-dev --no-emit-project --no-hashes -o \${TMPDIR:-/tmp}/agency-agents-requirements.txt && uv run pip-audit --strict -r \${TMPDIR:-/tmp}/agency-agents-requirements.txt --progress-spinner off"
)

# ---------------------------------------------------------------------------
# Output helpers. Colour is for humans with a terminal; a pipe gets plain text
# and stable wording so `gate.sh | grep` keeps working.
# ---------------------------------------------------------------------------
if [[ -t 1 ]] && [[ -z "${NO_COLOR:-}" ]]; then
  BOLD=$'\033[1m'; DIM=$'\033[2m'; RED=$'\033[31m'
  GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RESET=$'\033[0m'
else
  BOLD=''; DIM=''; RED=''; GREEN=''; YELLOW=''; RESET=''
fi

usage() {
  cat <<'EOF'
Usage: ./scripts/gate.sh [--fast | --keep-going | --list]

  (no flags)     Full gate, fail-fast: stops at the first failing check.
  --fast         Inner loop: skips the network dependency audit and the 80%
                 coverage floor. The output says so; it is not the full gate.
  --keep-going   Run every check even after one fails, then aggregate.
  --list         Print the checks in execution order with the CI job each
                 mirrors, then exit without running anything.
  -h, --help     This text.

Exit codes: 0 all checks passed, 1 a check failed, 2 usage or toolchain error.

Every check is the exact command CI runs. Details: docs/dx/gate.md.
EOF
}

# Milliseconds since the epoch. EPOCHREALTIME needs bash 5+; macOS ships bash
# 3.2, so fall back to whole seconds there rather than depend on GNU `date +%N`.
_now_ms() {
  if [[ -n "${EPOCHREALTIME:-}" ]]; then
    local micro="${EPOCHREALTIME/./}"
    printf '%s' "$((10#$micro / 1000))"
  else
    printf '%s' "$((SECONDS * 1000))"
  fi
}

_fmt_ms() {
  local ms="$1"
  printf '%d.%01ds' "$((ms / 1000))" "$(((ms % 1000) / 100))"
}

check_job() {
  local i
  for i in "${!CHECK_IDS[@]}"; do
    if [[ "${CHECK_IDS[$i]}" == "$1" ]]; then printf '%s' "${CHECK_JOBS[$i]}"; return 0; fi
  done
  printf '[unknown]'
}

check_rerun() {
  local i
  for i in "${!CHECK_IDS[@]}"; do
    if [[ "${CHECK_IDS[$i]}" == "$1" ]]; then printf '%s' "${CHECK_RERUNS[$i]}"; return 0; fi
  done
  printf './scripts/gate.sh'
}

# ---------------------------------------------------------------------------
# Toolchain discovery. `uv` is the only binary the gate needs; mise is searched
# only because it may already own the pinned uv, never as a requirement.
# ---------------------------------------------------------------------------
resolve_uv() {
  if command -v uv >/dev/null 2>&1; then command -v uv; return 0; fi
  if command -v mise >/dev/null 2>&1; then
    local found=''
    if found="$(mise which uv 2>/dev/null)" && [[ -n "$found" ]]; then
      printf '%s\n' "$found"
      return 0
    fi
  fi
  return 1
}

die_no_uv() {
  cat >&2 <<'EOF'
gate: uv not found — every check needs it, so nothing was run.
  CI installs uv 0.12.12; mise.toml and .python-version pin the same toolchain.
  Fix: ./scripts/bootstrap.sh          (acquires uv, then syncs the lockfile)
       or install uv 0.12.12: https://docs.astral.sh/uv/getting-started/installation/
EOF
}

cleanup_audit_file() {
  if [[ -n "$AUDIT_REQ_FILE" ]]; then rm -f -- "$AUDIT_REQ_FILE"; fi
}

# ---------------------------------------------------------------------------
# The checks. Each branch mirrors one CI step verbatim; the `test` branch is the
# only place `--fast` changes a command, and the header says so when it does.
# ---------------------------------------------------------------------------
run_security_audit() {
  # Audit the exported runtime requirements, not the environment: the project is
  # installed editable (not the published PyPI distribution), which makes an
  # env-wide audit fail on its own distribution. Same reasoning as the `security`
  # job in ci.yml.
  AUDIT_REQ_FILE="$(mktemp "${TMPDIR:-/tmp}/agency-agents-requirements.XXXXXX")"
  "$UV" export --format requirements-txt --no-dev --no-emit-project \
    --no-hashes -o "$AUDIT_REQ_FILE"
  "$UV" run pip-audit --strict -r "$AUDIT_REQ_FILE" --progress-spinner off
}

run_check() {
  case "$1" in
    ruff)
      "$UV" run ruff check .
      ;;
    runbook-structure)
      "$UV" run python scripts/ci/check_runbook_structure.py
      ;;
    yamllint)
      "$UV" run yamllint -d relaxed .github/
      ;;
    catalog-lint)
      "$UV" run python -m agency_agents lint
      ;;
    types)
      # Calls bare `uv` internally; main() puts the resolved uv on PATH first.
      bash scripts/ci/mypy_ratchet.sh
      ;;
    verify-manifest)
      "$UV" run python -m agency_agents verify --all
      ;;
    catalog-sync)
      "$UV" run python scripts/sync_catalog_data.py --check
      ;;
    test)
      if (( FAST )); then
        # mise `test`: no coverage instrumentation, so no 80% floor. Fast, and
        # explicitly not the CI check — the header and summary both say so.
        "$UV" run pytest -q
      else
        "$UV" run pytest -q --cov=agency_agents --cov-branch \
          --cov-report=term-missing --cov-report=xml --cov-fail-under=80
      fi
      ;;
    security-audit)
      run_security_audit
      ;;
    *)
      printf 'gate: internal error, unknown check %s\n' "$1" >&2
      return "$EXIT_USAGE"
      ;;
  esac
}

is_enabled() {
  if (( FAST == 0 )); then return 0; fi
  case "$1" in
    security-audit) return 1 ;;
    *) return 0 ;;
  esac
}

check_label() {
  if [[ "$1" == "test" ]] && (( FAST )); then
    printf '%s (coverage floor NOT enforced)' "$(check_job "$1")"
    return 0
  fi
  check_job "$1"
}

# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------
print_list() {
  printf '%s\n\n' "${BOLD}scripts/gate.sh — checks in execution order, cheapest first${RESET}"
  printf '%-3s %-17s %-24s %-22s %s\n' '#' 'check' 'ci job' 'measured cost' 'command'
  local i
  for i in "${!CHECK_IDS[@]}"; do
    printf '%-3s %-17s %-24s %-22s %s\n' \
      "$((i + 1))" "${CHECK_IDS[$i]}" "${CHECK_JOBS[$i]}" \
      "${CHECK_COSTS[$i]}" "${CHECK_RERUNS[$i]}"
  done
  printf '\n%s--fast skips:%s security-audit (needs network) and the coverage floor of test.\n' \
    "$DIM" "$RESET"
  printf '%sEvery check runs the same command as .github/workflows/ci.yml. See docs/dx/gate.md.%s\n' \
    "$DIM" "$RESET"
}

announce() {
  printf '%s\n' "${BOLD}scripts/gate.sh${RESET} — local gate, mirrors .github/workflows/ci.yml"
  printf '  repo: %s\n' "$ROOT_DIR"
  if (( FAST )); then
    printf '  mode: %sFAST%s — security-audit skipped, coverage floor not enforced\n' \
      "$YELLOW" "$RESET"
    printf '        %sthis is NOT the full gate; run ./scripts/gate.sh before pushing%s\n' \
      "$YELLOW" "$RESET"
  elif (( KEEP_GOING )); then
    printf '  mode: full, keep-going (every check runs, failures aggregate)\n'
  else
    printf '  mode: full, fail-fast (stops at the first failing check)\n'
  fi
  printf '\n'
}

summary() {
  local passed="$1" failed="$2" skipped="$3" total_ms="$4" tff_ms="$5" failed_id="$6"
  local not_run=$((${#CHECK_IDS[@]} - passed - failed - skipped))
  printf '\n%s\n' '------------------------------------------------------------'
  if (( failed > 0 )); then
    printf '%sGATE RESULT: FAIL%s — %d failed, %d passed, %d skipped, %d not run, %s\n' \
      "$RED" "$RESET" "$failed" "$passed" "$skipped" "$not_run" "$(_fmt_ms "$total_ms")"
    local i
    for i in "${!CHECK_IDS[@]}"; do
      if [[ -n "$failed_id" && "${CHECK_IDS[$i]}" == "$failed_id" ]]; then
        printf '  failing check: %s %s\n' "${CHECK_IDS[$i]}" "$(check_job "${CHECK_IDS[$i]}")"
        printf '  re-run just this check:\n    %s\n' "$(check_rerun "${CHECK_IDS[$i]}")"
      fi
    done
    if (( KEEP_GOING == 0 )); then
      printf '  time to first failure: %s (M2 locally; CI spends this per job)\n' \
        "$(_fmt_ms "$tff_ms")"
    fi
    printf '  full gate: ./scripts/gate.sh\n'
    return 0
  fi
  if (( FAST )); then
    printf '%sGATE RESULT: PASS (FAST — NOT the full gate)%s — %d checks ran, %d skipped, %s\n' \
      "$GREEN" "$RESET" "$passed" "$skipped" "$(_fmt_ms "$total_ms")"
    printf '  skipped: security-audit (needs network), coverage floor (pytest ran without --cov)\n'
    printf '  before pushing: ./scripts/gate.sh\n'
    return 0
  fi
  printf '%sGATE RESULT: PASS%s — %d checks, %s\n' \
    "$GREEN" "$RESET" "$passed" "$(_fmt_ms "$total_ms")"
}

run_all() {
  local total=0 i id
  for i in "${!CHECK_IDS[@]}"; do
    if is_enabled "${CHECK_IDS[$i]}"; then total=$((total + 1)); fi
  done

  local idx=0 passed=0 failed=0 skipped=0 failed_id=''
  local total_ms=0 tff_ms=0 start_ms elapsed_ms rc

  for i in "${!CHECK_IDS[@]}"; do
    id="${CHECK_IDS[$i]}"
    if ! is_enabled "$id"; then
      skipped=$((skipped + 1))
      printf '%s[skip] %-17s %s — skipped by --fast (not run, not hidden)%s\n' \
        "$DIM" "$id" "$(check_job "$id")" "$RESET"
      continue
    fi
    idx=$((idx + 1))
    printf '%s[%d/%d] %s%s  %s\n' "$BOLD" "$idx" "$total" "$id" "$RESET" "$(check_label "$id")"

    start_ms="$(_now_ms)"
    if run_check "$id"; then rc=0; else rc=$?; fi
    elapsed_ms=$(($(_now_ms) - start_ms))
    total_ms=$((total_ms + elapsed_ms))

    if (( rc == 0 )); then
      passed=$((passed + 1))
      printf '  %s✓ passed%s %s\n\n' "$GREEN" "$RESET" "$(_fmt_ms "$elapsed_ms")"
      continue
    fi

    failed=$((failed + 1))
    if [[ -z "$failed_id" ]]; then failed_id="$id"; tff_ms="$total_ms"; fi
    printf '  %s✗ FAILED %s %s%s (%s)\n' \
      "$RED" "$id" "$RESET" "$(check_label "$id")" "$(_fmt_ms "$elapsed_ms")"
    printf '    re-run just this check:\n      %s\n' "$(check_rerun "$id")"
    if (( KEEP_GOING == 0 )); then
      printf '%s  fail-fast: stopping here. --keep-going runs the rest.%s\n' "$DIM" "$RESET"
      break
    fi
  done

  summary "$passed" "$failed" "$skipped" "$total_ms" "$tff_ms" "$failed_id"
  if (( failed > 0 )); then return "$EXIT_FAILED"; fi
  return 0
}

parse_args() {
  while (($# > 0)); do
    case "$1" in
      --fast) FAST=1 ;;
      --keep-going) KEEP_GOING=1 ;;
      --list) LIST_ONLY=1 ;;
      -h | --help) usage; exit 0 ;;
      *)
        printf 'gate: unknown option %s\n\n' "$1" >&2
        usage >&2
        exit "$EXIT_USAGE"
        ;;
    esac
    shift
  done
  if (( FAST && KEEP_GOING )); then
    printf 'gate: --fast and --keep-going together are ambiguous; pick one.\n' >&2
    exit "$EXIT_USAGE"
  fi
}

main() {
  parse_args "$@"
  if (( LIST_ONLY )); then print_list; return 0; fi

  if ! UV="$(resolve_uv)"; then
    die_no_uv
    exit "$EXIT_USAGE"
  fi
  # mypy_ratchet.sh calls bare `uv`, so a mise-provided uv must be on PATH too.
  PATH="$(dirname "$UV"):$PATH"
  export PATH
  trap cleanup_audit_file EXIT

  announce
  run_all
}

main "$@"
