#!/usr/bin/env bash
# Bootstrap — golden-path step 2: the only supported way to prepare a clone.
#
# One command takes a fresh `git clone` to "ready to run the gate":
#   1  refuse to run outside a git working tree — closes handoff note H1: a clone
#      failure is a network/credential problem, a bootstrap failure is a toolchain
#      one, so the two are not diagnosable by the same person in the same context
#   2  acquire uv, installing it only when it is genuinely absent
#   3  make a Python 3.13+ interpreter resolve, through `uv python` (never sudo)
#   4  run `uv sync --frozen` — identical dependency resolution to CI
#   5  prove the installed `agency-agents` console script actually answers
#
# Usage: ./scripts/bootstrap.sh
# Exit:  0 ready (and it prints the next command) | 1 a step failed, and the message
#        names what failed, the command that fixes it, and what to do if that fails.
# Safe to run twice: the second run is a no-op, not an error.
#
# Pins: mise.toml (uv 0.12.12, python 3.13) and .python-version. CI runs
# `uv sync --frozen`, so bootstrap runs `uv sync --frozen`: a local sync that
# re-resolved the lockfile would hide exactly the drift CI then rejects. mise is
# optional and never invoked here — a machine without it bootstraps identically.
set -euo pipefail

REPO_URL="https://github.com/msitarzewski/agency-agents.git"
ISSUES_URL="https://github.com/msitarzewski/agency-agents/issues"
UV_INSTALL_SH="https://astral.sh/uv/install.sh"
UV_INSTALL_PS1="https://astral.sh/uv/install.ps1"
UV_DOCS_URL="https://docs.astral.sh/uv/getting-started/installation/"
GATE_COMMAND="./scripts/gate.sh"
PYTHON_FALLBACK="3.13"
CLONE_COMMAND="git clone ${REPO_URL} agency-agents && cd agency-agents"
PHASE_TOTAL=5

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
START_EPOCH="$(date +%s)"
OS_NAME="$(uname -s 2>/dev/null || echo unknown)"
UV_BIN=""
PYTHON_RESOLVED=""
phase_current=0

# --- output helpers ---------------------------------------------------------

phase() {
  phase_current=$((phase_current + 1))
  printf '\n=== [%d/%d] %s\n' "${phase_current}" "${PHASE_TOTAL}" "$1"
}

detail() {
  printf '    %s\n' "$1"
}

pass() {
  printf '    ok: %s\n' "$1"
}

# Every failure answers the same three questions: what broke, the command that
# fixes it, and what to do when that command does not work either. A bare
# "failed" is a ticket, and a ticket is the thing bootstrap exists to remove.
fail() {
  printf '\n!!! bootstrap failed: %s\n\n' "$1" >&2
  printf '    fix           : %s\n' "$2" >&2
  printf '    if that fails : %s\n' "$3" >&2
  printf '    diagnose      : bash -x ./scripts/bootstrap.sh   then paste the output into %s\n\n' \
    "${ISSUES_URL}" >&2
  exit 1
}

# --- phase 1: this must be a git checkout (handoff note H1) -----------------

require_git_checkout() {
  if ! command -v git >/dev/null 2>&1; then
    fail "git is not installed, so this is not a git checkout" \
      "install git from https://git-scm.com/downloads" \
      "Debian/Ubuntu: sudo apt-get install -y git | macOS: xcode-select --install | Windows: https://git-scm.com/download/win, then re-run ./scripts/bootstrap.sh"
  fi
  local inside
  inside="$(git -C "${ROOT_DIR}" rev-parse --is-inside-work-tree 2>/dev/null || true)"
  if [ "${inside}" != "true" ]; then
    fail "not a git working tree: ${ROOT_DIR}" \
      "${CLONE_COMMAND}" \
      "that is a network or credential problem, not a toolchain problem: check 'git ls-remote ${REPO_URL}' and your GitHub access. bootstrap needs a clone, not a downloaded ZIP."
  fi
  pass "git checkout: ${ROOT_DIR}"
}

# --- phase 2: uv ------------------------------------------------------------

is_windows_shell() {
  case "${OS_NAME}" in
  MINGW* | MSYS* | CYGWIN*) return 0 ;;
  esac
  return 1
}

# uv on PATH wins. Otherwise look where every installer variant drops a single
# binary, so a uv installed earlier in this machine's life is reused, not
# re-downloaded. Prints the path and succeeds when it finds one.
find_uv() {
  if command -v uv >/dev/null 2>&1; then
    command -v uv
    return 0
  fi
  local dir name
  for dir in "${HOME}/.local/bin" "${HOME}/.cargo/bin" "${XDG_BIN_HOME:-}"; do
    [ -n "${dir}" ] || continue
    for name in uv uv.exe; do
      if [ -x "${dir}/${name}" ]; then
        printf '%s\n' "${dir}/${name}"
        return 0
      fi
    done
  done
  return 1
}

uv_version() {
  "${UV_BIN}" --version 2>/dev/null | head -n 1 || true
}

# The installer prints its own progress on purpose: a silent minute is what makes
# a newcomer believe the script hung.
install_uv() {
  if is_windows_shell && command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -NoProfile -ExecutionPolicy ByPass -c "irm ${UV_INSTALL_PS1} | iex"
    return
  fi
  if command -v curl >/dev/null 2>&1; then
    curl -LsSf "${UV_INSTALL_SH}" | sh
    return
  fi
  if command -v wget >/dev/null 2>&1; then
    wget -qO- "${UV_INSTALL_SH}" | sh
    return
  fi
  fail "uv is missing and neither curl nor wget exists to fetch the installer" \
    "install curl, then re-run ./scripts/bootstrap.sh   (Debian/Ubuntu: sudo apt-get install -y curl | macOS: curl ships with the OS | Windows: irm ${UV_INSTALL_PS1} | iex in PowerShell)" \
    "install uv by hand from ${UV_DOCS_URL} (a single binary) and re-run ./scripts/bootstrap.sh"
}

ensure_uv() {
  local found
  if ! found="$(find_uv)"; then
    detail "uv is absent; installing it (this is the step no document named)"
    if ! install_uv; then
      fail "the uv installer did not finish, so uv is still absent" \
        "curl -LsSf ${UV_INSTALL_SH} | sh   |   Windows PowerShell: irm ${UV_INSTALL_PS1} | iex" \
        "download uv by hand from ${UV_DOCS_URL}, put the binary on PATH, and re-run ./scripts/bootstrap.sh"
    fi
    found="$(find_uv)" ||
      fail "uv was installed but no binary appeared in ~/.local/bin or ~/.cargo/bin" \
        "export PATH=\"\$HOME/.local/bin:\$PATH\" && ./scripts/bootstrap.sh" \
        "install it once by hand from ${UV_DOCS_URL}, then re-run ./scripts/bootstrap.sh"
  fi
  UV_BIN="${found}"
  PATH="$(dirname "${UV_BIN}"):${PATH}"
  export PATH
  pass "uv: $(uv_version) (${UV_BIN})"
}

# --- phase 3: a Python 3.13+ interpreter ------------------------------------

python_pin() {
  local pin=""
  if [ -f "${ROOT_DIR}/.python-version" ]; then
    pin="$(head -n 1 "${ROOT_DIR}/.python-version" | tr -d '[:space:]')"
  fi
  [ -n "${pin}" ] || pin="${PYTHON_FALLBACK}"
  printf '%s\n' "${pin}"
}

ensure_python() {
  local want resolved
  want="$(python_pin)"
  # --no-project: the question is "does this machine have the interpreter uv
  # would use", not "what does this project's venv currently point at".
  if resolved="$("${UV_BIN}" python find --no-project "${want}" 2>/dev/null)"; then
    PYTHON_RESOLVED="${resolved}"
    pass "python ${want}: ${resolved}"
    return
  fi
  detail "no Python ${want} yet; uv installs a managed interpreter (no sudo, no python.org trip)"
  if ! "${UV_BIN}" python install "${want}"; then
    fail "uv could not provide a Python ${want} interpreter" \
      "uv python install ${want}" \
      "check HTTPS_PROXY or the corporate proxy and that github.com is reachable, then re-run. If downloads are blocked outright, install Python ${want} from python.org; uv picks it up on the next run."
  fi
  resolved="$("${UV_BIN}" python find --no-project "${want}")" ||
    fail "Python ${want} was installed but uv cannot resolve it" \
      "uv python find --no-project ${want}" \
      "read the error above; if uv lists the interpreter but not on PATH, add its bin directory and re-run ./scripts/bootstrap.sh"
  pass "python ${want}: ${resolved}"
  PYTHON_RESOLVED="${resolved}"
}

# --- phase 4: dependency sync, frozen like CI -------------------------------

sync_environment() {
  if [ ! -f "${ROOT_DIR}/uv.lock" ]; then
    fail "uv.lock is missing from ${ROOT_DIR}, so --frozen has nothing to resolve" \
      "${CLONE_COMMAND}" \
      "a clone always ships uv.lock: a missing lockfile means a ZIP download or a partial checkout. bootstrap needs a git clone."
  fi
  detail "uv sync --frozen   (the exact command CI runs; the lockfile is never re-resolved)"
  if ! "${UV_BIN}" sync --frozen; then
    fail "uv sync --frozen failed, so the environment did not build" \
      "uv lock --check   then re-run ./scripts/bootstrap.sh   (if it reports drift: uv lock, commit uv.lock, re-run)" \
      "network or TLS: check HTTPS_PROXY and that https://pypi.org is reachable. Corrupt cache: uv cache clean. uv too old for this lockfile: uv self update (mise.toml pins 0.12.12)."
  fi
  pass "environment synced from uv.lock"
}

# --- phase 5: the console script is the thing under test --------------------

# The installed entry point, not `python -m agency_agents`: a developer who
# installs the package reaches for `agency-agents`, so a broken shim has to
# surface here instead of at step 4 of the golden path.
verify_console_script() {
  local output=""
  detail "agency-agents --help   (the installed console script)"
  if output="$("${UV_BIN}" run --no-sync --frozen agency-agents --help 2>&1)"; then
    if [ -n "${output}" ]; then
      printf '%s\n' "${output}" | sed -n '1,2s/^/    | /p'
    fi
    pass "console script answered (exit 0)"
    return
  fi
  printf '\n    the console script did not answer. its output was:\n\n'
  printf '%s\n' "${output}" | sed 's/^/    | /'
  printf '\n'
  fail "agency-agents --help exited non-zero: the console script did not answer" \
    "uv sync --frozen && ./scripts/bootstrap.sh   (re-check once the entry point is fixed)" \
    "this is a repository defect, not your machine: pyproject.toml [project.scripts] maps agency-agents = \"agency_agents:main\", and that callable must exist and be callable. Report it at ${ISSUES_URL} with the output above; until it is fixed, uv run python -m agency_agents --help is the working surface."
}

# --- done -------------------------------------------------------------------

print_next_steps() {
  printf '\n=== bootstrap complete in %ss\n' "$(($(date +%s) - START_EPOCH))"
  detail "uv      : $(uv_version)"
  detail "python  : ${PYTHON_RESOLVED}"
  detail "venv    : ${ROOT_DIR}/.venv"
  printf '\n    next command (golden-path step 3, the gate CI runs):\n\n        %s\n\n' \
    "${GATE_COMMAND}"
}

main() {
  cd "${ROOT_DIR}"

  phase "checking this is a git checkout"
  require_git_checkout

  phase "acquiring uv"
  ensure_uv

  phase "resolving Python $(python_pin)+"
  ensure_python

  phase "syncing dependencies"
  sync_environment

  phase "verifying the console script"
  verify_console_script

  print_next_steps
}

main
