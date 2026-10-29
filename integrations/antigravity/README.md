# Antigravity Integration

Installs the full Agency roster as Antigravity skills. Each agent is prefixed
with `agency-` to avoid conflicts with existing skills.

## Install

```bash
./scripts/install.sh --tool antigravity
```

This copies files from `integrations/antigravity/` to
`~/.gemini/config/skills/` (global). For project-scoped skills, Antigravity
also reads `<project>/.agents/skills/`.

Every agent is rendered as a subagent (`subagent: true`) except
`agents-orchestrator`, which the converter promotes to the main agent
(`mainAgent: true`). That promotion is a render-level policy
(`PRIMARY_AGENT_SLUGS` in `src/agency_agents/core/converter.py`), not a
frontmatter field.

## Activate a Skill

In Antigravity, activate an agent by its slug:

```
Use the agency-frontend-developer skill to review this component.
```

Available slugs follow the pattern `agency-<agent-name>`, e.g.:
- `agency-frontend-developer`
- `agency-backend-architect`
- `agency-reality-checker`
- `agency-growth-hacker`

## Regenerate

After modifying agents, regenerate the skill files:

```bash
./scripts/convert.sh --tool antigravity
```

## File Format

Each skill is a `SKILL.md` file with Antigravity-compatible frontmatter:

```yaml
---
name: agency-frontend-developer
description: Expert frontend developer specializing in...
risk: low
source: community
date_added: '2026-03-08'
---
```
