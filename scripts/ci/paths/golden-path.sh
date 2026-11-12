#!/usr/bin/env bash
# The golden path as documented in docs/dx/golden-path.md, executed literally.
#
# Five steps, one owner each, and no step that a newcomer has to guess. This file
# is the instruction set the clean-room harness runs; it is not a convenience
# wrapper, so every line here must be a line the docs actually publish.
#
# $REF is exported by the harness.

REF="${REF:-main}"

# Step 1 — get the code. Owner: Platform Engineer.
# Prerequisites are git and a shell; bootstrap supplies everything else.
run_step "get-the-code" \
  git clone --branch "${REF}" /src/repo.bundle agency-agents

cd agency-agents || exit 1

# Step 2 — bootstrap. Owner: Platform Engineer -> Developer Tooling Engineer (H1).
# One command: uv, a managed Python 3.13, uv sync --frozen, and a check that the
# installed console script actually answers.
run_step "bootstrap" ./scripts/bootstrap.sh

# Step 3 — run the gate. Owner: Developer Tooling Engineer.
# Cheapest check first, fail-fast, and the same checks CI runs.
run_step "gate" ./scripts/gate.sh

# Step 4 — install your work. Owner: DevOps Automator.
# The installed console script, not `python -m`: that is the surface a developer
# types, and it is the one that was broken.
export PATH="${PWD}/.venv/bin:${PATH}"
run_step "install-your-work" \
  agency-agents install --tool claude-code --scope user --no-interactive

# Step 5 — prove it landed. Owner: SRE (Site Reliability Engineer).
# The tree is healthy: every rendered artifact matches the SHA-256 manifest.
run_step "prove-it-landed" agency-agents verify --all

# Observation, not a developer step: the Evidence Collector asserts that the
# install is visible on disk. It is measured separately so the step count the
# document publishes (five developer commands) is never confused with the number
# of things this harness measures.
run_step "observe-installed-agents" \
  bash -c 'expected=299; written=$(find "$HOME/.claude/agents" -name "*.md" | wc -l); echo "installed agents: ${written}"; test "${written}" -ge "${expected}"'
