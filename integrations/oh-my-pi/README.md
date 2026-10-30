# Oh My Pi Integration

Installs the full Agency roster as Oh My Pi subagents using the `gemini-md`
format.

## Install

```bash
python -m agency_agents install --tool oh-my-pi
```

User scope writes `~/.omp/agent/agents/<slug>.md`; project scope
(`--scope project`) writes `<project>/.omp/agents/<slug>.md`. Slugs come from
the agent name, so `Agents Orchestrator` becomes `agents-orchestrator.md`.

## Regenerate

```bash
python -m agency_agents convert --tool oh-my-pi
python -m agency_agents update-manifest oh-my-pi
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

Oh My Pi reads the agent by its slug from the agents directory.
