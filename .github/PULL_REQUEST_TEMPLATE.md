## What does this PR do?

<!-- One paragraph. What changes, and why now? -->

Closes #

## Type of change

<!-- The PR title must follow Conventional Commits: feat, fix, docs, style,
     refactor, perf, test, build, ci, chore. The release changelog is generated
     from it, so a vague title becomes a vague changelog entry. -->

- [ ] `feat` — new capability
- [ ] `fix` — defect
- [ ] `docs` — documentation only
- [ ] `refactor` — no behaviour change
- [ ] `ci` / `build` / `chore` — tooling

## Test evidence

<!-- Paste the command you ran and its result. A PR without evidence is a
     promise, and promises are not reviewable. -->

```
$ uv run pytest -q
...
```

## Agent changes (only if this PR touches agent files)

- **Agent name**:
- **Division**:
- **Overlap checked against**:

## Checklist

- [ ] Title follows Conventional Commits
- [ ] Linked to an issue
- [ ] Tests added or updated for the behaviour change
- [ ] `uv run ruff check .` passes
- [ ] `uv run python -m agency_agents lint` passes
- [ ] No secrets, tokens, or personal data in the diff
- [ ] Deviations from the plan are written down, not left implicit
