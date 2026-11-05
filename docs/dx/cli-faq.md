# CLI FAQ — five questions the new commands raise

Every command was run in this repo; each exit code is what it printed. Inside a clone use `uv run` — it puts the project venv on `PATH`, so nothing stale can shadow the command.

## 1. How do I install just the team a runbook describes?

```bash
uv run agency-agents install --list runbooks                                           # exit 0, 42 rows
uv run agency-agents install --runbook developer-experience-platform --tool claude-code
```

The slug is **not** the file name — `strategy/runbooks/scenario-developer-experience-platform.md` has
slug `developer-experience-platform`; `--list` prints slug first, doc path second. Exit 0 prints all
five roster groups and writes 15 agents; `--dry-run` plans without writing. `--runbook` is a *selector*:
adding `--division engineering` exits 1, `❌ --runbook cannot be combined with --division.`

## 2. Why is there no `agency-agents runbooks` subcommand?

There is no such subcommand: `uv run agency-agents runbooks --help` exits **2** with `No such command
'runbooks'.` D-002 (`docs/dx/m7-tool-decisions.md:252`) scored A — `install --runbook <slug>` — against
B, a `runbooks` group, and adopted **A at 83.0/100 vs 73.5**: `install()` is one long procedural
function, so a group would duplicate its body and lose `--dry-run`, `--scope` and the opencode warning.
Revisit trigger, any **one**: a second verb (`show`/`pin`/`diff`/`search`); `install` past **12 flags**
(it has 11); `--runbook` composing with `--agents-file`. Review at handover + 90 days, hard backstop 12
months. `golden-path.md:91` still reads "replaced by `agency-agents runbooks install`".

## 3. How do I browse instead of remembering flags?

```bash
uv run agency-agents tui --tool claude-code      # needs a real terminal; a pipe exits 1
```

Keys verified against `browser.apply_key` — the on-screen footer names only six of them:

| Key | Effect |
| --- | --- |
| `up`/`down`, `c-p`/`c-n` · `pageup`/`pagedown`, `c-b`/`c-f` | move one row · move ten rows |
| `tab` · `c-a` · `c-x` · `c-u` | toggle a row · select all visible · clear · reset the filter |
| printable char · `backspace`/`c-h` | widen the filter · narrow it |
| `enter`/`c-m` · `escape`/`c-c`/`c-q` | install the selection · leave (selection kept) |

All 22 behaviours were exercised against the model and pass; check one with no terminal: `uv run python -c "from agency_agents.infrastructure.browser import BrowserModel,apply_key; print(apply_key(BrowserModel(rows=[]),'enter'))"`

## 4. `agency-agents` or `python -m agency_agents`?

Both exit 0; the help differs only in the usage line, so `diff` of the two outputs exits 1 there.

- `agency-agents` is the console script `pyproject.toml:16` declares — what bootstrap phase 5 and
golden-path step 4 type. It needs the venv: `uv run`, or `source .venv/bin/activate`, else `not found`.
- `python -m agency_agents` runs `__main__.py`, bypassing that script — the escape hatch for defect D1:
`uv run python -c "from agency_agents import main"` → `ImportError`, exit 1, while `-m` works. A stale
`agency-agents` earlier on `PATH` wins, so `uv run agency-agents …` is the unshadowable form.

## 5. What does `lint` failing mean, and what changed?

`uv run python -m agency_agents lint` (exit 0) checks `tools.json`, divisions, `runbooks.json` and agent
frontmatter; **any** inconsistency is now fatal and names the file or catalog entry to fix. Before defect
D2 (`docs/dx/baseline.md:99`) it printed `❌ Tools Consistency Errors` and exited **0**, so CI gated on a
green run full of red text. `bash scripts/ci/assert_lint_fails.sh` (exit 0) proves the gate fails: it
injects a schema-valid tool naming an unregistered `format`, asserts a non-zero exit, restores `tools.json` via a `trap`.
