# Oh My Pi Integration

Installs the full Agency roster as Oh My Pi (OMP) task agents using the
`oh-my-pi-md` format.

## Install

```bash
python -m agency_agents install --tool oh-my-pi
```

User scope writes `~/.omp/agent/agents/<slug>.md`; project scope
(`--scope project`) writes `<project>/.omp/agents/<slug>.md`. Slugs come from
the agent name, so `Agents Orchestrator` becomes `agents-orchestrator.md`.

OMP also scans `agents/` inside enabled extension packages and Claude
marketplace plugins, but it deliberately skips foreign harness roots such as
`.claude/agents` and `.gemini/agents` — their frontmatter is not the OMP
task-agent contract. This integration writes to the native `.omp` roots only.

## Regenerate

```bash
python -m agency_agents convert --tool oh-my-pi
python -m agency_agents update-manifest oh-my-pi
```

## File Format

Each agent is a markdown file whose frontmatter is the OMP task-agent contract,
followed by the agent body:

```yaml
---
name: frontend-developer
description: "Expert frontend developer specializing in modern web technologies..."
tools: [read, write, edit, grep, glob, find, bash, web_search]
blocking: true
structured: false
autoloadSkills: ["*"]
---
```

OMP reads none of the source metadata (`color`, `emoji`, `vibe`, `version`,
`tags`), so the renderer rewrites the block instead of copying it. The fields,
in the order OMP's own agents declare them:

### `name`

The agent's slug, not its display name. OMP resolves a subagent by exact
`name` — it is what `task` dispatches against and what the `/agents` hub lists.
`main` and `sub` are reserved for the session sentinels and would be rejected.

### `description`

Required, and must be non-empty: OMP drops a definition whose `description` is
missing or empty. It is emitted as a quoted scalar because descriptions carry
colons, em dashes and quotes. An agent with no description of its own states its
name rather than the renderer inventing a claim about it.

### `tools`

An allowlist over OMP's builtin tool names, derived from the same render policy
as Antigravity:

| Agent | Tools |
| --- | --- |
| `agents-orchestrator`, `vasquez` | `task`, `wait`, `read`, `write`, `edit`, `grep`, `glob`, `find`, `bash`, `web_search` |
| every other agent | `read`, `write`, `edit`, `grep`, `glob`, `find`, `bash`, `web_search` |

The source agent's Claude-style `tools:` line is not translated — a tool name
OMP does not know is silently ignored, which would look like a granted
capability that never existed.

What a subagent actually receives is this allowlist intersected with what OMP
hands a child. Observed against 18.13.3: an installed agent lists those names
minus `find` (this install exposes no `find`, the main session included) and
OMP withholds `todo` from subagents even though the main session has it — which
is why `todo` is not declared. Plugins and MCP tools stay additive: `eval` and
the configured MCP servers arrive regardless of the allowlist.

### `spawns`

`"*"` for the two agents the render policy promotes — the orchestrator and
Vasquez, the process steward that convenes the reviews and gates. `spawns` is
reachable only through the `task` tool, so a specialist carries neither: a
specialist delegates nothing, and the only fan-out in the roster is those two.

### `blocking`

`false` for both delegating agents, so they keep dispatching without waiting at
each gating step; `true` for specialists, whose result is what the caller gates
on.

### `structured`

`false` everywhere. Structured results need an `output` schema, and no agent
ships one, so the flag would arm a `yield` tool with nothing to resolve.

### `autoloadSkills`

`["*"]`, the literal wildcard. Note what OMP does with it: `autoloadSkills` is
an exact-name list — names it cannot match are ignored, and there is no glob
expansion — so `"*"` injects no skills today. The key is emitted so the contract
stays visible per agent; it is not a claim that the roster's skills load.

## Verified Against OMP

The contract above was checked against OMP 18.13.3: `docs/task-agent-discovery.md`,
`discovery/helpers.ts` (`parseAgentFields`), `tools/builtin-names.ts`, and the
bundled agents `omp agents unpack` writes out. Rendered agents were then
installed and dispatched by a live session: a plain dispatch, a three-level
chain (parent → orchestrator → `scout`) that returned the exact bytes of a file,
and a read-back of the child's own tool list — the read-back is what pinned the
granted-tools list above.

`src/agency_agents/tests/unit/test_converter_oh_my_pi.py` pins the contract for
every agent in the roster; the CI staging job asserts the installed files.
