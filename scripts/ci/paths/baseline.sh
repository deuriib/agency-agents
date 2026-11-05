#!/usr/bin/env bash
# Baseline "documented path" as it exists on main before this runbook's Phase 3.
#
# Every command below is traceable to README.md or CONTRIBUTING.md and nothing
# else. Steps a newcomer must guess are marked GUESSED so the friction inventory
# can charge them to the docs rather than to the subject.
#
# Referenced documentation:
#   README.md "Prefer the command line?" — "requires Python 3.13+ and uv; inside
#     the repo run with `uv run python -m agency_agents`"
#   README.md "Option 2: Use with Claude Code" — `python -m agency_agents install
#     --tool claude-code`
#   CONTRIBUTING.md checklist steps 6-8 — `uv run python -m agency_agents lint`,
#     `uv run pytest`, `uv run python -m agency_agents verify <tool>`
#
# The harness exports REF; a direct invocation of this file may not.
REF="${REF:-main}"

# Step 1 — clone. Documented implicitly by CONTRIBUTING "Fork the repository".
run_step "clone" \
  git clone --branch "${REF}" /src/repo.bundle repo

cd repo || exit 1

# Step 2 — obtain uv. NOT documented: README only says "requires ... uv".
# GUESSED: the newcomer must know about astral.sh/uv and its install script.
run_step "install-uv (undocumented)" \
  bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1 && export PATH="$HOME/.local/bin:$PATH" && uv --version'

export PATH="$HOME/.local/bin:$PATH"

# Step 3 — sync dependencies. NOT documented as a step: `uv run` does it
# implicitly. GUESSED by anyone who does not already know uv semantics.
run_step "uv-sync (undocumented)" uv sync --frozen

# Step 4 — run the CLI the README documents, from inside the repo.
run_step "cli-install-agents" \
  uv run python -m agency_agents install --tool claude-code --scope user --no-interactive

# Step 5 — the console script the package declares in pyproject.toml.
# A developer who installed the package expects `agency-agents` to answer.
# The baseline answers and is recorded either way: a failure here is evidence,
# not a harness error.
run_step "console-script --help" \
  bash -c 'uv run agency-agents --help'
