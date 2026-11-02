# Security Policy

## Supported versions

Security fixes are released against the latest published tag. Older tags are
not patched; upgrade to the newest release.

| Version | Supported |
| ------- | --------- |
| latest `vX.Y.Z` | yes |
| anything older | no |

## Reporting a vulnerability

**Do not open a public issue for a security problem.**

Report it privately through
[GitHub Security Advisories](https://github.com/deuriib/agency-agents/security/advisories/new).
That channel is private, tracks the fix, and lets us request a CVE if one is
warranted.

Please include:

- the affected version or commit,
- the command or file involved,
- a minimal reproduction,
- the impact you believe it has.

## Response timeline

- Acknowledgement: within 48 hours
- Initial assessment: within 7 days
- Fix or mitigation: depends on severity, agreed with the reporter

## What is in scope

This repository ships a Python CLI (`agency_agents`) and a catalog of Markdown
agent definitions.

- **`src/agency_agents/`** — the CLI, parser, validator, converter, installer,
  hash manager and TUI. Vulnerabilities here are in scope.
- **`scripts/`** — repository tooling, including the label sync script.
- **`.github/workflows/`** — CI and release automation. Supply-chain issues in
  the workflows are in scope and are treated as high severity.
- **Agent Markdown files** — not executable. A crafted agent file is only a
  problem if the CLI mishandles it, and that is in scope. Prompt-injection
  attempts embedded in an agent definition are a content problem: report them
  and they will be removed.

## What is out of scope

- Vulnerabilities in third-party AI tools that consume the generated files.
- Anything requiring an attacker to already control the user's machine.
- Reports produced solely by an automated scanner without a demonstration of
  impact.

## Repository security controls

These are enforced today and verifiable in the repository:

- **Branch protection** — `main` requires a pull request and a passing
  `ci/required` status check; force-push and deletion are blocked.
  Applied from `scripts/github/ruleset.json`.
- **Dependency auditing** — `pip-audit` runs on every pull request against the
  exported runtime requirements.
- **Static analysis** — CodeQL runs on every pull request, every push to
  `main`, and weekly.
- **Dependency updates** — Dependabot tracks the `github-actions` and `uv`
  ecosystems weekly.
- **Secret scanning and push protection** — enabled at the repository level.
- **Pinned actions** — every `uses:` in `.github/workflows/` is pinned to a
  40-character commit SHA, kept current by Dependabot.
- **Least privilege** — every workflow declares an explicit `permissions:`
  block.

## Handling secrets

Never commit API keys, tokens, or credentials. Never place secrets in agent
Markdown files. If a secret reaches a commit, rotate it first and then rewrite
history; deleting the commit is not enough.
