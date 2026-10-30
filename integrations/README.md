# 🔌 Integrations

The Agency ships one renderer per tool format. `tools.json` is the single
source of truth for formats, install kinds, destinations, and slugs; this page
explains how to install and regenerate the artifacts.

## Supported Tools

| Tool | Format | Destination |
| --- | --- | --- |
| `claude-code` | `identity` | `~/.claude/agents/<slug>.md` |
| `copilot` | `identity` | `~/.copilot/agents/<slug>.md` + `~/.github/agents/<slug>.md` |
| `antigravity` | `antigravity-md` | `~/.gemini/config/agents/<slug>.md` (user), `.agents/agents/<slug>.md` (project) |
| `gemini-cli` | `gemini-md` | `~/.gemini/agents/<slug>.md` |
| `opencode` | `opencode-md` | `~/.config/opencode/agents/<slug>.md` (user), `.opencode/agents/<slug>.md` (project) |
| `openclaw` | `openclaw-workspace` | `~/.openclaw/agency-agents/<slug>/{SOUL,AGENTS,IDENTITY}.md` |
| `cursor` | `cursor-mdc` | `.cursor/rules/<slug>.mdc` (project only) |
| `aider` | `aider-conventions` | `CONVENTIONS.md` roster (project only) |
| `windsurf` | `windsurf-rules` | `.windsurfrules` roster (project only) |
| `kimi` | `kimi-agent` | `~/.config/kimi/agents/<slug>/{agent.yaml,system.md}` |
| `qwen` | `qwen-md` | `~/.qwen/agents/<slug>.md` (user), `.qwen/agents/<slug>.md` (project) |
| `codex` | `codex-toml` | `~/.codex/agents/<slug>.toml` |
| `vibe` | `vibe-toml` | `.vibe/agents/<slug>.toml` + `.vibe/prompts/<slug>.md` |
| `zcode` | `zcode-md` | `~/.zcode/agents/<slug>.md` (user), `.zcode/agents/<slug>.md` (project) |
| `osaurus` | `skill-md` | `~/.osaurus/skills/agency-<slug>/SKILL.md` |
| `dsh` | `skill-md` | `~/.dsh/skills/agency-<slug>/SKILL.md` |
| `pi-agent` | `gemini-md` | `~/.pi/agent/agents/<slug>.md` (user), `.pi/agents/<slug>.md` (project) |
| `oh-my-pi` | `gemini-md` | `~/.omp/agent/agents/<slug>.md` (user), `.omp/agents/<slug>.md` (project) |
| `hermes` | `hermes-router-plugin` | `~/.hermes/plugins/agency-agents-router` (built plugin) |

## Install

```bash
# Interactive wizard
python -m agency_agents install

# One tool, user scope (default)
python -m agency_agents install --tool antigravity

# Project-scoped tools (OpenCode, Cursor, Aider, Windsurf, Qwen, ...)
python -m agency_agents install --tool opencode --scope project
```

The installer renders each agent from the source markdown on the fly. There is
no separate conversion step to perform on a fresh clone.

Installing the full catalog (`--tool` omitted) skips tools that have no
destination for the chosen scope and prints the skip. Naming a tool explicitly
fails with exit code 1 instead of silently writing nothing.

## Regenerate Integration Files

```bash
# Every tool, written to integrations/<tool>/<slug>/
python -m agency_agents convert

# One tool
python -m agency_agents convert --tool antigravity
```

Generated directories are gitignored. After changing a renderer or an agent,
regenerate the hash manifest for the affected tool:

```bash
python -m agency_agents update-manifest antigravity
python -m agency_agents verify --all
```

## Antigravity

Each agent is a markdown file in `~/.gemini/config/agents/` (user) or
`.agents/agents/` (project). There is no `agency-` prefix. The renderer declares
the tool surface per role:

- `agents-orchestrator` is the main agent (`mainAgent: true`) and gets
  `invoke_subagent`, `manage_subagents`, `send_message`, and `manage_task`
  alongside the execution tools.
- Every other agent is a subagent (`subagent: true`) and receives execution
  tools only: `view_file`, `write_to_file`, `replace_file_content`,
  `grep_search`, `find_by_name`, `list_dir`, `run_command`.

```bash
python -m agency_agents install --tool antigravity
```

See [antigravity/README.md](antigravity/README.md) for details.

## Pi Agent and Oh My Pi

Both use the `gemini-md` renderer, so the output is the same agent markdown
shape as Gemini CLI, installed into their own directories:

```bash
python -m agency_agents install --tool pi-agent
python -m agency_agents install --tool oh-my-pi
```

Project scope writes `.pi/agents/` and `.omp/agents/` respectively.

## OpenClaw

Each agent becomes a workspace with `SOUL.md`, `AGENTS.md`, and `IDENTITY.md`.
Restart the gateway after installing if it is already running:

```bash
python -m agency_agents install --tool openclaw
openclaw gateway restart
```

## Kimi Code

Kimi uses a YAML agent spec plus a separate system prompt. After installing,
run an agent with `--agent-file`:

```bash
kimi --agent-file ~/.config/kimi/agents/frontend-developer/agent.yaml
```

## Hermes

Hermes is a built plugin, not a per-agent render. `convert` runs the builder and
fails the command if the build exits non-zero; `install` builds it into
`~/.hermes/plugins/agency-agents-router`.

```bash
python -m agency_agents install --tool hermes
```

See [hermes/README.md](hermes/README.md) for details.

## Per-tool guides

- [Claude Code](claude-code/README.md)
- [GitHub Copilot](github-copilot/README.md)
- [Antigravity](antigravity/README.md)
- [Gemini CLI](gemini-cli/README.md)
- [OpenCode](opencode/README.md)
- [OpenClaw](openclaw/README.md)
- [Cursor](cursor/README.md)
- [Aider](aider/README.md)
- [Windsurf](windsurf/README.md)
- [Kimi Code](kimi/README.md)
- [Qwen Code](qwen/README.md)
- [Codex](codex/README.md)
- [Mistral Vibe](vibe/README.md)
- [Hermes](hermes/README.md)
- [Pi Agent](pi-agent/README.md)
- [Oh My Pi](oh-my-pi/README.md)
