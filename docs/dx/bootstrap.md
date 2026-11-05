# Bootstrap — one command, five checks (golden-path step 2)

`./scripts/bootstrap.sh` is the only supported way to prepare a clone, and it is
safe to run twice: the second run is a no-op. It ends by printing the next command.

| # | Phase | Why it exists |
| --- | --- | --- |
| 1 | Refuses outside a git working tree | Steps 1 and 2 fail for different reasons (handoff note H1): a missing clone is network or credentials, a failed bootstrap is toolchain. The script asks for `git clone`, so the two are never confused. |
| 2 | Acquires `uv`, installing only when absent | `uv` was the first guessed step: `README.md` says the CLI "requires `uv`" and names no command. A `uv` on `PATH`, in `~/.local/bin` or in `~/.cargo/bin` is reused, never re-downloaded. |
| 3 | Makes a Python 3.13+ interpreter resolve via `uv python` | `requires-python = ">=3.13"` and Ubuntu 24.04 ships 3.12. uv installs a managed interpreter, so bootstrap needs no sudo and no python.org trip. |
| 4 | Runs `uv sync --frozen` | CI runs exactly this. A local sync that re-resolved the lockfile would hide the drift CI then rejects. |
| 5 | Runs `agency-agents --help` | The console script from `pyproject.toml [project.scripts]` is what a developer types. `python -m` passing while the script is broken is the defect that produced the baseline. |

`mise` is optional: nothing in the script calls it. `mise.toml` holds the pins
(`uv 0.12.12`, `python 3.13`) that CI uses; bootstrap only needs them to be true.

## On success

```bash
./scripts/gate.sh
```

## When it fails

Every failure exits non-zero and prints three answers: what failed, the command
that fixes it, and what to do when that fails too — then `bash -x ./scripts/bootstrap.sh`
with the output pasted into an issue.

| Message | What it means |
| --- | --- |
| `not a git working tree` | You are not in a clone. Clone it: a ZIP download ships no `uv.lock` and cannot bootstrap. |
| `git is not installed` | Install git, then re-run. |
| `could not provide a Python` | The interpreter download was blocked; check `HTTPS_PROXY`. |
| `uv sync --frozen failed` | Lockfile drift (`uv lock --check`), network, or a `uv` older than the pin (`uv self update`). |
| `the console script did not answer` | A repository defect, not your machine: `pyproject.toml` `[project.scripts]` maps `agency-agents` to `agency_agents.cli.main:main`, and that callable must exist. Report it with the output above. (This is the exact defect that shipped once — see `baseline.md` D1.) |

It does not install git hooks (`mise run hooks`), install agents into a tool (step
4), or configure `mise`. It owns the toolchain and nothing else.
