#!/usr/bin/env python3
"""Structural gate for NEXUS runbook docs.

`agency_agents lint` proves the roster is *installable* (slugs resolve, docs exist,
sizes fit the mode). It does not prove the doc is a *runbook*. This script does, and
it is the mechanical half of the dev-QA loop: a runbook that cannot answer "what is
the scenario, who is on the roster, what gates exist, how do we know it worked, and
how does it fail" is a scenario sketch, not deployable doctrine.

Usage:
    python scripts/ci/check_runbook_structure.py            # every registered doc
    python scripts/ci/check_runbook_structure.py FILE...    # specific docs
    python scripts/ci/check_runbook_structure.py --json     # machine-readable

Legacy debt is handled with a baseline, mirroring `scripts/ci/mypy_ratchet.sh`:
docs listed in `scripts/ci/runbook-structure-baseline.txt` are allowed to fail, but
the baseline may only shrink — a baselined doc that starts passing fails the build
until it is removed from the file. New runbooks are never allowed into the baseline.

Exit code 1 on any violation. No dependencies beyond the standard library.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNBOOKS_JSON = ROOT / "strategy" / "runbooks.json"
BASELINE = ROOT / "scripts" / "ci" / "runbook-structure-baseline.txt"

REQUIRED_SECTIONS = (
    "scenario",
    "agent roster",
    "key decisions",
    "success criteria",
    "common pitfalls",
)

# A runbook may not be shorter than this. Below it, the phase detail is a summary.
MIN_WORDS = 350

MODES = ("NEXUS-Micro", "NEXUS-Sprint", "NEXUS-Full")

# Agent-count bands from strategy/nexus-strategy.md section 2. A runbook outside its
# band is not really that mode: a 14-agent "Sprint" has no orchestration capacity,
# and a 14-agent "Micro" cannot run in days. Legacy docs in the baseline are the
# reason this lives here with a ratchet rather than in the install lint.
# Micro and Sprint have real numbers in the doctrine. Full is defined only as "All",
# which is unbounded, so its floor is the empirical floor of the program runbooks the
# catalog actually ships. The band's job is to catch a mislabelled mode, not to rank
# programs by size: a 21-agent full program is not a Sprint.
MODE_BANDS = {
    "NEXUS-Micro": (5, 10),
    "NEXUS-Sprint": (15, 25),
    "NEXUS-Full": (20, 40),
}


def registered() -> dict[str, dict]:
    """Map doc path -> runbook entry."""
    data = json.loads(RUNBOOKS_JSON.read_text(encoding="utf-8"))
    return {entry["doc"]: entry for entry in data["runbooks"]}


def sections(text: str) -> list[str]:
    return [m.group(1).strip().lower() for m in re.finditer(r"^##\s+(.+)$", text, re.MULTILINE)]


def check_tables(name: str, text: str) -> list[str]:
    """Every markdown table must keep the column count of its header row.

    A row with one pipe too many is silently dropped by most renderers, which is how a
    roster loses an agent that the registry still thinks is installed.
    """
    errors: list[str] = []
    block: list[tuple[int, str]] = []

    def flush() -> None:
        if len(block) < 2:
            block.clear()
            return
        expected = block[0][1].count("|")
        for lineno, row in block[1:]:
            if row.count("|") != expected:
                errors.append(
                    f"{name}:{lineno}: table row has {row.count('|')} pipes, header has {expected}."
                )
        block.clear()

    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            block.append((number, stripped))
        else:
            flush()
    flush()
    return errors


def roster_row_count(text: str) -> int:
    """Count agent rows inside the `## Agent Roster` section's tables."""
    lines = text.splitlines()
    in_roster = False
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_roster = stripped.lower().startswith("## agent roster")
            continue
        if not in_roster or not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells or all(set(c) <= {"-", ":"} for c in cells):
            continue  # separator row
        if cells[0].lower() == "agent":
            continue  # header row
        count += 1
    return count


def check_doc(path: Path, entry: dict | None) -> list[str]:
    errors: list[str] = []
    name = path.name
    text = path.read_text(encoding="utf-8")

    if text.lstrip().startswith("---"):
        errors.append(f"{name}: has YAML frontmatter. Runbooks are doctrine, not agents.")

    found = sections(text)
    for required in REQUIRED_SECTIONS:
        if required not in found:
            errors.append(f"{name}: missing '## {required.title()}' section.")

    errors.extend(check_tables(name, text))

    # At least one execution-phase section beyond the required ones.
    execution = [s for s in found if "execution" in s or "week" in s or "day" in s or "phase" in s]
    if not execution:
        errors.append(f"{name}: no execution section (## Week/Phase/Day ... Execution).")

    words = len(text.split())
    if words < MIN_WORDS:
        errors.append(f"{name}: {words} words, below the {MIN_WORDS}-word floor for usable phase detail.")

    gate_hits = len(re.findall(r"quality gate", text, re.IGNORECASE))
    if gate_hits == 0:
        errors.append(f"{name}: no 'Quality Gate' anywhere. A runbook without a gate cannot fail.")

    if not re.search(r"^\|\s*Metric\s*\|", text, re.MULTILINE | re.IGNORECASE):
        errors.append(f"{name}: no '## Success Criteria' metric table (expected a '| Metric |' header).")

    if entry is None:
        return errors

    mode = entry["mode"]
    if mode not in text:
        errors.append(f"{name}: does not mention its registered mode '{mode}'.")
    else:
        for other in MODES:
            if other != mode and other in text:
                errors.append(f"{name}: mentions '{other}' but is registered as '{mode}'.")

    band = MODE_BANDS.get(mode)
    roster_size = sum(len(group["agents"]) for group in entry["roster"])
    if band and not band[0] <= roster_size <= band[1]:
        errors.append(
            f"{name}: rosters {roster_size} agents; {mode} is {band[0]}-{band[1]} "
            f"per strategy/nexus-strategy.md."
        )

    # The doc's roster table must deploy the same set the registry will install.
    documented = roster_row_count(text)
    if documented != roster_size:
        errors.append(
            f"{name}: Agent Roster tables list {documented} agents, runbooks.json registers "
            f"{roster_size}."
        )

    # Every roster group should surface in the doc as a heading or table, so a reader
    # can match the prose to what the installer will deploy.
    for group in entry["roster"]:
        label = group["group"].split("(")[0].strip()
        if label.lower() not in text.lower():
            errors.append(f"{name}: roster group '{label}' never appears in the doc.")

    return errors


def load_baseline(path: Path) -> set[str]:
    """Doc filenames excused from the gate. One per line, '#' comments allowed."""
    if not path.is_file():
        return set()
    names: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.add(line)
    return names


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    args = [a for a in argv if not a.startswith("-")]
    baseline = load_baseline(BASELINE)

    catalog = registered()
    if args:
        targets = [(Path(a), catalog.get(Path(a).as_posix())) for a in args]
    else:
        targets = [(ROOT / doc, entry) for doc, entry in sorted(catalog.items())]

    results: dict[str, list[str]] = {}
    for path, entry in targets:
        if not path.is_file():
            results[str(path)] = [f"{path.name}: file does not exist."]
            continue
        results[str(path)] = check_doc(path, entry)

    failures = {k: v for k, v in results.items() if v}
    excused = {k: v for k, v in failures.items() if Path(k).name in baseline}
    # Only docs actually examined can "now pass". Running a single file must not
    # accuse the whole baseline of having been fixed.
    checked_names = {Path(k).name for k in results}
    unexpected_pass = sorted(name for name in baseline if name in checked_names and name not in {Path(k).name for k in failures})

    blocking = {k: v for k, v in failures.items() if Path(k).name not in baseline}

    if as_json:
        print(
            json.dumps(
                {
                    "checked": len(results),
                    "baselined": sorted(name for name in baseline),
                    "blocking": blocking,
                    "ratchet_violations": unexpected_pass,
                },
                indent=2,
            )
        )
    else:
        for path, errs in blocking.items():
            print(f"\n✗ {Path(path).name}")
            for err in errs:
                print(f"    - {err}")
        if excused:
            print(f"\n~ {len(excused)} doc(s) excused by baseline (legacy debt, must shrink):")
            for path in sorted(excused):
                print(f"    {Path(path).name}")
        if unexpected_pass:
            print("\n✗ Baseline ratchet: these now pass the gate and must leave the baseline file:")
            for name in unexpected_pass:
                print(f"    {name}")
        passed = len(results) - len(failures)
        print(f"\n{passed}/{len(results)} runbook docs passed; {len(blocking)} blocking failure(s).")

    return 1 if blocking or unexpected_pass else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
