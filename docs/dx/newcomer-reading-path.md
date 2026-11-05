# Newcomer Reading Path — agency-agents Python CLI

A source-derived order for reading this repository's CLI code, plus the couplings
and setup steps that are not visible from `README.md` or `CONTRIBUTING.md`.

Every statement below is traceable to a file that was read or a command that was
run; the command output is quoted where it matters. Nothing here is inferred
from naming or intent.

---

## One-line summary

`src/agency_agents/` is a Typer CLI that reads three JSON catalogs at the repo
root (`tools.json`, `divisions.json`, `strategy/runbooks.json`), parses the
frontmatter of the 298 agent `.md` files inside the 18 division directories,
renders each agent into one of 13 tool-specific formats through a renderer
registry, and writes the results either to `$HOME`/the project (install) or to
`integrations/<tool>/` (convert), with a SHA-256 manifest as the regression gate.

## Five-minute map

- **Primary tasks in code**: `lint` (validate catalogs + agent frontmatter),
  `install` (render + write per tool), `convert` (render + write to
  `integrations/`), `verify` / `update-manifest` (SHA-256 drift gate),
  `check-originality` (8-word shingle similarity over the roster).
- **Primary inputs**: `tools.json`, `divisions.json`, `strategy/runbooks.json`,
  the agent `.md` files, `convert-outputs.sha256`, and CLI flags
  (`--tool`, `--scope`, `--division`, `--agent`, `--agents-file`, `--dry-run`,
  `--list`, `--parallel`, `--jobs`).
- **Primary outputs**: files under `Path.home()` or the project root (install),
  files under `integrations/<tool>/` (convert), rewritten
  `convert-outputs.sha256` (update-manifest), exit codes (lint/verify).
- **Main code path**: `python -m agency_agents`
  → `cli/main.py:app` → `CatalogManager` loads the JSON catalogs
  → `MarkdownParser.create_agent` builds `Agent` objects
  → `ConverterEngine` picks a renderer by `tool.format`
  → `InstallationManager` writes to the paths in `tool.dest[scope]`
  → `HashManager` hashes the rendered content for `verify`.
- **If you only read three files first**: `src/agency_agents/cli/main.py`,
  `src/agency_agents/core/converter.py`, `src/agency_agents/infrastructure/installer.py`.

---

## 1. Read these ten files in this order

The ten follow the actual call path: package definition → boot → command surface
→ catalog schema → catalog data → domain object → parser → renderer dispatch →
write path → the gate that defines a valid repo. The remaining four Python modules
and two JSON catalogs are listed in Appendix A with why they can wait; they are
leaf consumers of the ten, not prerequisites for them.

### 1. `pyproject.toml`

**Why first:** it states what the package is, how it is built, what the Python
floor is, and — critically — which entry point the world is expected to call. A
newcomer who skips this file cannot explain why `uv run` is the documented way to
run anything here.

**Notice:**
- `[project.scripts] agency-agents = "agency_agents:main"` — this console script
  is broken: `src/agency_agents/__init__.py` defines only `__version__`, no
  `main`. Running it exits 1 with `ImportError: cannot import name 'main' from
  'agency_agents'` (verified). Only `python -m agency_agents` works.
- `requires-python = ">=3.13"` and `build-backend = "uv_build"`.
- `[tool.coverage.report] fail_under = 80`, and `[dependency-groups] dev`
  (pytest, ruff, mypy, pip-audit, pre-commit, yamllint, pyyaml) — the group that
  `uv run` installs by default, which is why the first `uv run` pulls 60 packages.

### 2. `src/agency_agents/__main__.py`

**Why second:** it is the boot file, four lines long, and it names the one module
that actually owns the CLI. Nothing else in the package is imported at start-up.

**Notice:**
- `from agency_agents.cli.main import app`
- `app()` under `if __name__ == "__main__"`.

`src/agency_agents/__init__.py` holds only a docstring and `__version__ = "1.8.0"`.

### 3. `src/agency_agents/cli/main.py`

**Why third:** it is the map of the whole system. Six commands, and every
downstream module appears in its import block — so after this file you know the
module names, the flag surface, and which layer each command touches.

**Notice:**
- `lint()` (line 34) — the only command that runs `LintEngine`, and the only one
  whose exit-code logic you must read carefully (see §2.1 and §3.1 row 10).
- The `install()` signature (line 195) — the complete flag set:
  `--tool`, `--interactive/--no-interactive`, `--scope`, `--parallel`, `--jobs`,
  `--division`, `--agent`, `--agents-file`, `--dry-run`, `--list`. There is no
  `--path` flag anywhere in `src/` (verified by grep), despite `CONTRIBUTING.md:252`.
- `_collect_by_division()` (line 99), `_per_agent_tools()` (line 350),
  `_resolve_targets()` (line 359) — the three helpers that decide *what* gets
  rendered and *which* tools the manifest covers.

### 4. `src/agency_agents/infrastructure/catalog.py`

**Why fourth:** it is the schema for the three JSON files the CLI depends on, and
it is where the working-directory assumption lives. Read it before the JSON, so
the JSON reads as a filled-in contract rather than a wall of keys.

**Notice:**
- `ToolDefinition` — 15 fields; the three that carry behaviour are `format`,
  `installKind`, `dest`. `slugFrom`, `accent`, `short`, `id`, `version`, `scope`
  and `detect.agentsDir` are not read by any code in `src/` except as
  presence checks or dead payload (verified by grep: `slugFrom`, `accent`, `short`
  → 0 hits outside tests; `detect.agentsDir` → 0 hits anywhere, only
  `detect.get("dirs")` is read, and only in `tui.py:95`).
- `RunbookDefinition` / `RunbookRosterGroup` — the machine-readable runbook rosters.
- `CatalogManager.load_tools()` / `load_divisions()` / `load_runbooks()` — plain
  `open(self.root_dir / "<name>.json")`. No search, no fallback: this is why the
  CLI must be run from the repo root (§3.1 row 4).

### 5. `tools.json`

**Why fifth:** now the schema has data. This one file explains why 19 tools, 13
renderers and 3 install mechanisms coexist, and it is the file a contributor
edits most.

**Notice:**
- `format` — a key into `_FORMAT_RENDERERS` in the converter, not a free label.
  The 19 tools declare 16 distinct format names: 13 resolve to a renderer, and 3
  (`aider-conventions`, `windsurf-rules`, `hermes-router-plugin`) exist only for
  the `roster`/`plugin` kinds. Three renderable formats are shared — `identity`
  by `claude-code` and `copilot`, `gemini-md` by `gemini-cli` and `pi-agent`,
  `skill-md` by `osaurus` and `dsh`.
- `installKind` — `per-agent` (16 tools), `roster` (`aider`, `windsurf`),
  `plugin` (`hermes`). This is the dispatch key in the installer.
- `dest` — per-scope lists of destination patterns with `{slug}` substitution.
  The *count and order* of these patterns is consumed positionally by the
  installer (§2.2).

### 6. `src/agency_agents/core/models.py`

**Why sixth:** every layer above and below passes `Agent` and `AgentFrontmatter`
around. Reading the model before the parser prevents the most common early
misreading: this is not the YAML of the source file, it is a seven-field
canonical projection of it.

**Notice:**
- `AgentFrontmatter` — `name` (required), `description`, `version` (default
  `"1.0.0"`), `tags`, `icon`, `vibe`, `color`, plus a declared `extra: Dict`.
- `AgentFrontmatter.to_yaml()` (line 29) — re-emits a fixed field order
  (`name`, `description`, `version`, `tags`, `icon`, `vibe`, `color`) then `extra`.
  This is why rendered output is not a byte copy of the source frontmatter.
- `slugify()` (line 77) — NFKD → ASCII → strip non-word → hyphenate. The slug is
  derived from `name`, never from the filename.

### 7. `src/agency_agents/core/parser.py`

**Why seventh:** it is 55 lines and it contains the single most surprising rule in
the codebase (see §2.5). After this file, `Agent` objects stop being abstract.

**Notice:**
- `MarkdownParser.FRONTMATTER_PATTERN` — `^---\s*\n(.*?)\n---\s*\n`, DOTALL.
- `MarkdownParser.parse()` (line 20) — `line.split(":", 1)` per line, no YAML
  library, then `AgentFrontmatter(**data)`; any validation failure returns
  `(None, content)`, i.e. the file is silently not an agent.
- `MarkdownParser.create_agent()` (line 45) — returns `None` for non-agents. The
  `None` return is what every caller uses to distinguish "README, skip" from
  "broken agent, fail" (`content.startswith("---")`).

### 8. `src/agency_agents/core/converter.py`

**Why eighth:** this is where `format` becomes an object. Every rendering decision
in the repo is one of the classes in this file; there is no per-tool special-casing
outside it.

**Notice:**
- `_FORMAT_RENDERERS` (line 292) — the 13-entry `format → renderer class` dict; the
  extension point every integration touches.
- `NON_RENDERABLE_FORMATS` (line 310) — `aider-conventions`, `windsurf-rules`,
  `hermes-router-plugin`: legal in `tools.json` for non-`per-agent` kinds only.
- `select_renderer()` (line 325) / `ConverterEngine.convert_agent_for_tool()`
  (line 369) — render output is `List[Tuple[filename, content]]`; unknown
  formats raise `UnknownFormatError` rather than falling back.

Also worth noticing on the first pass, because they are render-level policy rather
than agent content: `PRIMARY_AGENT_SLUGS = frozenset({"agents-orchestrator",
"vasquez"})` (line 64) and `is_primary_agent()` (line 67) — two agents get different
frontmatter purely because of their slug.

### 9. `src/agency_agents/infrastructure/installer.py`

**Why ninth:** it is the write half. By now you know what a rendered artifact is;
this file decides where it lands and under what name.

**Notice:**
- `install_all_for_tool()` (line 150) — the `installKind` dispatch: `plugin` →
  `install_plugin()`, `roster` → `install_roster()`, everything else → the
  per-agent loop.
- `install_agent_for_tool()` (line 62) — `outputs[i] if i < len(outputs) else
  outputs[0]`: dest patterns and renderer outputs are zipped **by index**.
- `resolve_path()` (line 22) and `check_collisions()` (line 36) — scope decides
  the base (`Path.home()` for `user`, `root_dir` for `project`); `dsh` alone has
  env overrides (`DSH_HOME`, `DSH_SKILLS_DIR`) and only in the write path.
  `prune_output()` (line 53) is a docstring plus `pass` — a no-op that looks
  load-bearing.

### 10. `src/agency_agents/core/validator.py`

**Why last of the ten:** `lint` is the gate every contributor is told to run, so
it should be the last thing you read — after you can predict what it will complain
about. It is also the file that defines what "the repo is consistent" means.

**Notice:**
- `check_divisions_consistency()` (line 38) + the hardcoded `ignore = {...}` set
  (line 49) — the source of truth for which top-level directories are *not*
  divisions.
- `check_tools_consistency()` (line 66) — key-vs-`kebab` equality, required fields,
  `per-agent` format must be in `registered_formats()`, non-per-agent formats must
  be renderable or in `NON_RENDERABLE_FORMATS`, and at least one `dest` scope.
- `check_runbooks_consistency()` (line 126) — slug shape, unique slug, `mode` in
  `RUNBOOK_MODE_CAPACITY`, doc under `strategy/runbooks/` and on disk, non-empty
  roster, every slug resolving to a real agent `.md`, `agents-orchestrator`
  required in every roster, no agent in two groups, roster ≤ mode capacity, and
  every `strategy/runbooks/*.md` registered.

---

## 2. The five things that will confuse you

### 2.1 `tools.json` `format` is a Python dict key, and `lint` prints its guard without failing on it

`_FORMAT_RENDERERS` (`converter.py:292`) is the only registry. `tools.json` says
`"format": "gemini-md"`; the converter resolves that string to
`GeminiMdRenderer`. There is no plugin discovery, no entry points, no string
matching elsewhere. Three consequences bite:

- **Formats are shared on purpose.** `identity` serves `claude-code` and `copilot`;
  `gemini-md` serves `gemini-cli` and `pi-agent`; `skill-md` serves `osaurus` and
  `dsh`. Editing one renderer edits several tools, and `tools.json`'s own `_note`
  states this ("`format` is the renderer contract: the same `format` name
  guarantees byte-identical output").
- **Three formats have no renderer at all** — `aider-conventions`,
  `windsurf-rules`, `hermes-router-plugin`, collected in `NON_RENDERABLE_FORMATS`
  (`converter.py:310`). They are only legal because their `installKind` is
  `roster` or `plugin`.
- **The guard does not fail the build.** `check_tools_consistency()` reports
  `Tool 'probe-tool' is per-agent but format 'no-such-format' has no renderer`
  in red, and `lint()` still exits 0. Verified by injecting such a tool into
  `tools.json` in a throwaway clone:

  ```
  ❌ Tools Consistency Errors:
    - Tool 'probe-tool' is per-agent but format 'no-such-format' has no renderer.
  Register it in converter._FORMAT_RENDERERS.
  ✓ Divisions are consistent.
  ...
  EXIT=0
  ```

  `cli/main.py:lint()` only raises `typer.Exit(code=1)` for agent-file issues and
  runbook errors. `tools.json`'s `_note` and `CONTRIBUTING.md:240,249` describe a
  failing gate; the code prints and continues.

### 2.2 `installKind` picks the handler, and the dest/output pairing is positional

`install_all_for_tool()` (`installer.py:150`) dispatches on `installKind`:

| `installKind` | Handler | Tools | What it does |
|---|---|---|---|
| `plugin` | `install_plugin()` (line 118) | `hermes` | `subprocess.run(["uv", "run", "python", "scripts/build-hermes-plugin.py", "--out", ...])` |
| `roster` | `install_roster()` (line 98) | `aider`, `windsurf` | one concatenated file (`CONVENTIONS.md`, `.windsurfrules`) |
| `per-agent` | the loop at line 189 | the other 16 | one renderer call per agent |

The per-agent loop then pairs `tool.dest[scope][i]` with `outputs[i]`, falling
back to `outputs[0]` when the renderer emits fewer files than the tool declares:

- `copilot` declares **two** `user` destinations
  (`.copilot/agents/{slug}.md`, `.github/agents/{slug}.md`) and its renderer
  (`IdentityRenderer`) emits **one** output → the same bytes are written twice.
- `vibe` declares two destinations and `VibeTomlRenderer` emits two outputs
  (`agent.toml`, `prompt.md`) → matched.
- `openclaw` declares three destinations and `OpenClawWorkspaceRenderer` emits
  three (`SOUL.md`, `AGENTS.md`, `IDENTITY.md`) → matched.

So the number and order of `dest` patterns is not decoration: it is a positional
contract with a specific renderer class. `slugPrefix` (`osaurus`, `dsh` →
`agency-`) is applied **only** in the installer (`installer.py:89`), so
`convert` writes `integrations/<tool>/<slug>/` without the prefix
(`cli/main.py`, the per-agent branch of `convert()`).

### 2.3 `divisions.json` drives five different things, and only two of them consult the disk

The division list is not just data for a UI. It is read by:

1. `LintEngine.check_divisions_consistency()` (`validator.py:38`) — compares its
   keys against top-level directories on disk, after subtracting a **hardcoded**
   `ignore = {"integrations", "strategy", "examples", "scripts", "src", "dist",
   "docs"}` set (line 49) and every dot-directory.
2. `cli/main.py:lint()` — the division keys decide *which* directories get their
   agent files linted at all.
3. `_collect_by_division()` (`cli/main.py:99`), used by `install`, `convert` and
   `--list` — a division that is in `divisions.json` but missing on disk is
   skipped silently; a directory that exists but is not a division is never
   scanned, so its agents never install.
4. `TUIWizard.select_divisions()` (`tui.py:181`) and `_count_agents()`
   (line 206) — the interactive team list and the per-team agent counts.
5. `LintEngine._agent_slug_index()` (`validator.py:109`) and
   `originality._agent_dirs()` (`originality.py:65`) — the runbook slug index and
   the similarity corpus are both built **only** from these directories.

Like the tools check, a divisions mismatch does not fail the run. Creating an
undefined top-level directory printed `❌ Division Consistency Errors: Directory
'probe-division' found on disk but not defined in divisions.json.` and exited 0.

`CONTRIBUTING.md:43` tells a contributor to "add it to `AGENT_DIRS` in both
`python -m agency_agents lint` and the hash-manifest verify". No symbol named
`AGENT_DIRS` exists anywhere in the repository — grep returns exactly one hit,
that doc line. The real mechanism is the `ignore` set above, plus
`cli/main.py:_per_agent_tools()` for the manifest, which filters on
`installKind == "per-agent"` and never looks at divisions.

### 2.4 The manifest hashes concatenated *content*, so filenames are invisible to it

`HashManager.agent_hash()` (`hash_manager.py:37`) is
`sha256("".join(content for _, content in outputs))`. The filename half of every
`(filename, content)` tuple is dropped, and so is the destination pattern.

- Renaming a rendered file, or moving it to a different `dest` pattern, does not
  change a single hash. Adding or removing a rendered file does.
- The format is versioned: `MANIFEST_VERSION = 3`, header comment
  `# convert-outputs manifest v3 …`, and each line is
  `agent\t<tool>\t<slug>\t<digest>`. A legacy 3-column (tool-less) line makes
  `parse_manifest()` raise `ManifestError` instead of comparing against the wrong
  tool.
- Only `per-agent` tools are covered: `_resolve_targets()` (`cli/main.py:359`)
  refuses `roster`/`plugin` tools, and `--all` means `_per_agent_tools()`. The
  current file has 4768 `agent` lines = 16 per-agent tools × 298 agents
  (verified by counting).
- `update_tool()` rereads the manifest and rewrites only the named tool's lines;
  `update_all()` recomputes everything from the per-agent set and drops anything
  else. `write_manifest()` sorts by `(tool, slug)`, so the file is deterministic.

### 2.5 The frontmatter is not parsed as YAML, so unknown keys vanish and lists are fatal

`MarkdownParser.parse()` (`parser.py:20`) splits each line on the first `:` and
passes the resulting flat dict to `AgentFrontmatter(**data)`. Pydantic's default
`extra` behaviour drops undeclared keys, and the model's `extra` field is a
*declared field named* `extra`, not a catch-all. Net effect, verified by running
the parser directly:

- `emoji: 🖥️` in `engineering/engineering-frontend-developer.md` → gone. The
  identity-rendered `claude-code` output has no `emoji` line, and the parser's
  `fm.extra` is `{}`.
- `tools: WebFetch, WebSearch, Read, Write, Edit` in
  `specialized/specialized-pricing-analyst.md` → gone, even though
  `QwenMdRenderer` explicitly reads `fm.extra.get("tools", "")` and maps it
  through `TOOL_NAME_MAP`. The rendered qwen file for that agent literally
  contains `tools: ` with nothing after it.
- `tags: [a, b]`, a block list, or a nested `services:` mapping fails validation
  the moment any value cannot coerce to the declared type, and `parse()` returns
  `None` — the agent disappears. `lint_agents()` (`validator.py:219`) turns that
  into `Invalid frontmatter or missing required fields (name)`, and `install` /
  `convert` raise `Cannot parse agent frontmatter: <path>`.
- Values keep their literal quoting: the repo's own comment in
  `OhMyPiRenderer._unwrapped` documents that `description: "Ships the thing."`
  arrives with the quote characters attached, which is why that renderer strips
  exactly one layer before re-quoting.

Practical consequence: the CONTRIBUTING template's `services:` block and
`emoji:` line are documentation of a shape the parser does not read.

---

## 3. Setup steps the docs omit

Target: clone → `uv run python -m agency_agents lint` exits 0.

What `README.md` and `CONTRIBUTING.md` actually say:

- `README.md:44` — "The Python CLI below installs the same agents (requires Python
  3.13+ and [uv](https://docs.astral.sh/uv/); inside the repo run with
  `uv run python -m agency_agents`)."
- `CONTRIBUTING.md:249` — "**Run `uv run python -m agency_agents lint`** - it must
  pass."
- `CONTRIBUTING.md:250` — run `uv run pytest src/agency_agents/tests`.
- `CONTRIBUTING.md:255` — run `uv run python -m agency_agents verify <tool>`.

Neither file contains the words `mise`, `pre-commit`, `uv sync`, or `venv`
(verified: grep returns no hits in either file), and neither has a development
setup or "getting started as a contributor" section.

### 3.1 Undocumented steps that are genuinely required

| # | Step | Doc line that omits it | Evidence |
|---|---|---|---|
| 1 | Install `uv` itself | `README.md:44` names it, gives no command; `CONTRIBUTING.md` never lists it as a prerequisite | Every documented command starts with `uv run`; `CONTRIBUTING.md:249` assumes it already works |
| 2 | Have a CPython **3.13** interpreter reachable, or allow uv to download one | `README.md:44` ("requires Python 3.13+") states the version, not how to obtain it | `.python-version` = `3.13`; `pyproject.toml` `requires-python = ">=3.13"`. With no 3.13 visible and downloads disabled: `error: No interpreter found for Python 3.13 in search path` / `hint: A managed Python download is available for Python 3.13, but Python downloads are set to 'never'` |
| 3 | Network access on the first run (dependency resolution **and** building the project itself) | Nothing in either doc says the first command downloads or builds anything | A fresh clone's first `uv run python -m agency_agents lint` printed `Using CPython 3.13.18 … Creating virtual environment at: .venv`, `Building agency-agents @ file://…`, `Installed 60 packages in 5.51s` |
| 4 | Run the command **from the repo root** | `CONTRIBUTING.md:249` gives the command with no working-directory precondition | From `docs/`: uncaught `FileNotFoundError: … '/…/docs/tools.json'` and exit 1. Cause: `cli/main.py` uses `Path(".").absolute()` and `CatalogManager` opens `root_dir / "tools.json"` with no search |
| 5 | `uv sync --frozen` (or accept uv's implicit sync) | `README.md:44` and `CONTRIBUTING.md:249` never mention a sync step | `.github/workflows/ci.yml` runs `uv sync --frozen` as its own step in all five jobs; `scripts/ci/paths/baseline.sh:34` (an untracked file present in this working tree) labels the same step "uv-sync (undocumented)". Verified benign: plain `uv run` syncs implicitly and left `uv.lock` byte-identical |
| 6 | `mise` — the pinned toolchain and every quality task | Neither doc mentions mise at all | `mise.toml` pins `python = "3.13"`, `uv = "0.12.12"` and defines `lint`, `types`, `test`, `coverage`, `verify`, `security`, `check`, `ci`, `hooks`, `install`, `convert`, `full-pipeline` |
| 7 | `uv run pre-commit install` (the hooks do not exist until you install them) | Neither doc mentions pre-commit | `.pre-commit-config.yaml` = 3 remote hook repos plus a `local` repo whose hook `agency-lint` has `entry: uv run python -m agency_agents lint`; `mise.toml` task `hooks` runs `uv run pre-commit install` |
| 8 | The runbook structural gate — `lint` alone is not the CI lint job | `CONTRIBUTING.md:249` presents `uv run python -m agency_agents lint` as the gate | `mise.toml` task `lint` runs four commands: `ruff`, `yamllint .github/`, `python -m agency_agents lint`, and `python scripts/ci/check_runbook_structure.py`. `.github/workflows/ci.yml` splits the same work across the `lint` job (ruff, catalog lint, runbook structure) and the `security` job (`yamllint -d relaxed .github/`, line 108). Verified independently: ruff exit 0, runbook structure `42/42 runbook docs passed`, exit 0 |
| 9 | `strategy/runbooks.json` is a lint input, not just app data | No doc tells you adding a runbook doc requires registering it | `validator.py:126` — every `strategy/runbooks/*.md` must be registered in `strategy/runbooks.json`. Verified: adding an unregistered doc there produced `Runbook doc 'strategy/runbooks/zz-probe.md' is not registered in strategy/runbooks.json` and **exit 1** |
| 10 | The default install scope writes into `$HOME`, and there is no way to redirect it | No doc states the default; `CONTRIBUTING.md:252` claims a `--path` flag that does not exist | `cli/main.py:install()` — `scope = scope or "user"`; `installer.resolve_path()` returns `self.user_home / path` for `user`. Grep for `--path` in `src/`: 0 hits |

### 3.2 Doc lines that name a step the code does not have

These are not omissions but mis-directions a newcomer will hit while trying to
follow the setup path:

- **`CONTRIBUTING.md:43`** — "add it to `AGENT_DIRS` in both `python -m
  agency_agents lint` and the hash-manifest verify". No `AGENT_DIRS` symbol
  exists; the division check is the `ignore` set at `validator.py:49`, and the
  manifest does not filter by division at all (`_per_agent_tools()` filters on
  `installKind`).
- **`CONTRIBUTING.md:252`** — the test suite "pins … that `--path` beats the
  tool's env var". No command in `src/` defines `--path`.
- **`CONTRIBUTING.md:255-256`** — `convert-outputs.sha256` "holds one line per
  (tool, agent) and one line per tool". The file on disk holds 4768 `agent` lines
  and 0 other entries (verified by counting), and `parse_manifest()` skips every
  line whose first field is not `agent`, with the comment "non-agent entries are
  not verified yet".
- **`CONTRIBUTING.md:41` and `:240`** — "validated in CI by `python -m
  agency_agents lint`" / "Run it - it names every place that must match", written
  with bare `python`. On a clean clone that fails before reaching any check:
  `…/python3: No module named agency_agents` (verified), because the package uses
  a `src/` layout and is only importable through the project venv.
- **`README.md:50, 74, 77-91`** — every install example is bare `python -m
  agency_agents …`. `README.md:44` carries the `uv run` caveat, but the
  copy-paste blocks below it do not, and none of them say "from the repo root".
- **`README.md:889`** — "On a fresh clone, generate the Gemini agent files before
  running the installer." No command is given for that step, and there is no
  standalone Gemini generator: `scripts/` contains `build-hermes-plugin.py`,
  `check_runbook_structure.py`, `ci_metrics.py`, `mypy_ratchet.sh`,
  `apply-ruleset.sh`, `sync_labels.py` — the only builder is Hermes. Gemini
  files are produced inside the install path by the `gemini-md` renderer.

### 3.3 Things the docs do get right, for contrast

- `CONTRIBUTING.md:255-264` correctly tells you that editing an agent causes
  manifest drift and that you regenerate with `update-manifest <tool>` (the code
  agrees: `hash_manager.update_tool()` preserves other tools' lines).
- `CONTRIBUTING.md:242-264` (the tool integration checklist) correctly identifies
  `tools.json` → `_FORMAT_RENDERERS` → an `installKind` handler in
  `installer.py` as the three code touchpoints.
- `README.md:115` correctly documents the opencode ~119-agent ceiling; the code
  implements it in `selection.AGENT_CAPS` / `agent_cap()` and
  `cli/main.py:_warn_tool_capacity()`.

---

## Appendix A — files read but deliberately not in the ten

| File | One-line responsibility | Why it can wait |
|---|---|---|
| `divisions.json` | 18 divisions → label/icon/color | Reading it before `validator.py` gives you no way to know it has five consumers (§2.3) |
| `strategy/runbooks.json` | 42 runbooks → `slug`/`mode`/`doc`/`roster[].agents[]` | Only meaningful once `validator.check_runbooks_consistency()` and `catalog.RunbookDefinition` are known |
| `core/selection.py` | `agent_aliases()`, `build_roster_index()`, `select_agents()`, `parse_agents_file()`, `AGENT_CAPS` | Pure filter layer; fails closed with `SelectionError` on unknown ids |
| `infrastructure/hash_manager.py` | manifest v3 generation/verification | Only after you have run `converter` and `installer` and know what an "output" is |
| `infrastructure/tui.py` | `TUIWizard`: tool/scope/team prompts, `InstallSelection`, `WizardCancelled` | Interactive front end for flags you already met in `install()` |
| `core/originality.py` | entity-neutralized 8-word shingle Jaccard over the roster | Standalone command; touches no install path |

## Appendix B — not verified

- Whether a `python -m agency_agents` run outside a git checkout behaves
  differently — every probe above used a git clone.
- The external app that consumes `tools.json`, `divisions.json` and
  `strategy/runbooks.json` (referenced from `CONTRIBUTING.md:244`), and therefore
  whether the fields the CLI ignores (`slugFrom`, `accent`, `short`, `id`) are
  consumed there.
- Windows/macOS behaviour, including the UTF-8 console reconfiguration at the top
  of `cli/main.py`.
- `mypy` ratchet, `pip-audit`, `yamllint` and the coverage floor were read but
  only `ruff` and `scripts/ci/check_runbook_structure.py` were executed.
- Whether a `python -m agency_agents` run can reorder `convert-outputs.sha256`
  versus the committed copy — `verify --all` was not executed in this pass.
