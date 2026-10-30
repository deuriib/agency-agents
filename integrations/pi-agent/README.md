# Pi Agent Integration

Installs the full Agency roster as Pi Agent subagents using the `gemini-md`
format.

## Install

```bash
python -m agency_agents install --tool pi-agent
```

User scope writes `~/.pi/agent/agents/<slug>.md`; project scope
(`--scope project`) writes `<project>/.pi/agents/<slug>.md`. Slugs come from the
agent name, so `Agents Orchestrator` becomes `agents-orchestrator.md`.

## Regenerate

```bash
python -m agency_agents convert --tool pi-agent
python -m agency_agents update-manifest pi-agent
```

## File Format

Each agent is a markdown file with YAML frontmatter and the agent body:

```yaml
---
name: frontend-developer
description: Expert frontend developer specializing in...
color: cyan
---
```

Pi Agent reads the agent by its slug from the agents directory.
