# Antigravity Integration

Installs the full Agency roster as Antigravity agents.

## Install

```bash
uv run python -m agency_agents install --tool antigravity
```

User scope writes to `~/.gemini/config/agents/<slug>.md`. Project scope
(`--scope project`) writes to `<project>/.agents/agents/<slug>.md`. Slugs come
from the agent name, so `Agents Orchestrator` becomes `agents-orchestrator.md`.

Every agent is rendered as a subagent (`subagent: true`) except
`agents-orchestrator`, which the converter promotes to the main agent
(`mainAgent: true`). That promotion is a render-level policy
(`PRIMARY_AGENT_SLUGS` in `src/agency_agents/core/converter.py`), not a
frontmatter field.

## Tool Declarations

Antigravity reads the allowed tools from the agent frontmatter, so the renderer
emits a role-specific `tools` list instead of passing through the source
agent's Claude-style tool names.

| Role | Tools |
| --- | --- |
| Main agent (`agents-orchestrator`) | `invoke_subagent`, `manage_subagents`, `send_message`, `manage_task`, plus every execution tool |
| Subagent (everyone else) | `view_file`, `write_to_file`, `replace_file_content`, `grep_search`, `find_by_name`, `list_dir`, `run_command` |

Subagents never receive `invoke_subagent`, `manage_subagents`, `send_message`,
or `manage_task`; delegation is reserved for the main agent.

## Activate an Agent

In Antigravity, activate an agent by its slug:

```
Use the frontend-developer agent to review this component.
```

Available slugs follow `<agent-name>`, e.g.:
- `frontend-developer`
- `backend-architect`
- `reality-checker`
- `growth-hacker`

## Regenerate

After modifying agents, regenerate the files and the hash manifest:

```bash
uv run python -m agency_agents convert --tool antigravity
uv run python -m agency_agents update-manifest antigravity
```

## File Format

Each agent is a markdown file with Antigravity-compatible frontmatter:

```yaml
---
name: frontend-developer
description: Expert frontend developer specializing in...
risk: low
source: community
date_added: '2026-03-08'
subagent: true
tools: [view_file, write_to_file, replace_file_content, grep_search, find_by_name, list_dir, run_command]
---
```

The main agent replaces `subagent: true` with `mainAgent: true` and adds the
delegation tools to the same `tools` list.
