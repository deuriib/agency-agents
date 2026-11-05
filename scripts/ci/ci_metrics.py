#!/usr/bin/env python3
"""Reproducible CI metrics source for the Developer Experience Platform runbook.

This is the stored query behind M2 (CI time to first failure), M3 (CI pipeline
duration) and M4 (flake rate). It reads GitHub Actions history through the `gh`
CLI and prints percentiles, so a gate never rests on a remembered number.

Metric definitions live in
`strategy/runbooks/scenario-developer-experience-platform.md` under Definitions:

- M2: run start to the first failed job reporting a failing step, p50 and p90.
      Green runs contribute no sample, so M2 is reported only when the window
      holds at least one failed run.
- M3: run start to terminal status of the whole workflow, p50 and p90.
- M4: a run that fails and is re-run to green with no commit in between.
      Flake rate = flakes / runs over the window, per workflow.

Usage:
    python scripts/ci/ci_metrics.py                 # default: 20 runs per workflow
    python scripts/ci/ci_metrics.py --limit 100     # baseline window
    python scripts/ci/ci_metrics.py --json          # machine-readable snapshot
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Workflows that gate a merge. Release and Dependency Graph are excluded: they
# are triggered by the release train, not by a developer's change.
GATING_WORKFLOWS = ("CI", "Project Quality Check")


def _gh(args: List[str]) -> Any:
    """Run a gh command and parse its JSON stdout."""
    proc = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def _parse_ts(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _percentile(values: List[float], fraction: float) -> Optional[float]:
    """Nearest-rank percentile; small windows do not support interpolation."""
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = max(1, min(len(ordered), round(fraction * len(ordered))))
    return ordered[rank - 1]


def fetch_runs(workflow: str, branch: str, limit: int) -> List[Dict[str, Any]]:
    """Fetch completed runs for one workflow, newest first."""
    return _gh(
        [
            "run",
            "list",
            f"--workflow={workflow}",
            f"--branch={branch}",
            f"--limit={limit}",
            "--json",
            "databaseId,status,conclusion,createdAt,updatedAt,headSha,event,attempt",
        ]
    )


def first_failure_seconds(run_id: int) -> Optional[float]:
    """M2 for a single run: start to the first failing job reporting a failure.

    Only failed runs carry a sample. A run whose jobs are unavailable (logs
    expired, permissions) is reported as None and counted as UNMEASURED rather
    than silently dropped.
    """
    detail = _gh(["run", "view", str(run_id), "--json", "createdAt,jobs"])
    started = _parse_ts(detail.get("createdAt"))
    if started is None:
        return None
    failing = [
        job for job in detail.get("jobs") or [] if job.get("conclusion") == "failure"
    ]
    if not failing:
        return None
    # The first failing step inside the first failing job that reports one.
    earliest: Optional[datetime] = None
    for job in failing:
        for step in job.get("steps") or []:
            if step.get("conclusion") == "failure":
                ts = _parse_ts(step.get("completedAt") or step.get("startedAt"))
                if ts and (earliest is None or ts < earliest):
                    earliest = ts
                break
        if earliest is None:
            job_done = _parse_ts(job.get("completedAt"))
            if job_done:
                earliest = job_done
    if earliest is None:
        return None
    return (earliest - started).total_seconds()


def summarise(runs: List[Dict[str, Any]], workflow: str) -> Dict[str, Any]:
    """Compute M3 duration percentiles and the M4 flake count for one workflow."""
    completed = [r for r in runs if r.get("conclusion") in ("success", "failure")]
    durations: List[float] = []
    for run in completed:
        start = _parse_ts(run.get("createdAt"))
        end = _parse_ts(run.get("updatedAt"))
        if start and end:
            durations.append((end - start).total_seconds())

    # M4: a failure followed by a success on the same commit is a flake, because
    # nothing changed in between except the re-run.
    by_sha: Dict[str, List[Dict[str, Any]]] = {}
    for run in completed:
        by_sha.setdefault(run.get("headSha") or "", []).append(run)
    flakes = 0
    for sha, group in by_sha.items():
        if not sha:
            continue
        conclusions = [r.get("conclusion") for r in sorted(group, key=lambda r: r.get("createdAt") or "")]
        if "failure" in conclusions and "success" in conclusions:
            flakes += 1

    failures = [r for r in completed if r.get("conclusion") == "failure"]
    m2_samples: List[float] = []
    m2_unmeasured = 0
    for run in failures:
        seconds = first_failure_seconds(int(run["databaseId"]))
        if seconds is None:
            m2_unmeasured += 1
        else:
            m2_samples.append(seconds)

    return {
        "workflow": workflow,
        "window_runs": len(completed),
        "m3_p50_seconds": _percentile(durations, 0.50),
        "m3_p90_seconds": _percentile(durations, 0.90),
        "m2_samples": len(m2_samples),
        "m2_unmeasured": m2_unmeasured,
        "m2_p50_seconds": _percentile(m2_samples, 0.50),
        "m2_p90_seconds": _percentile(m2_samples, 0.90),
        "failures": len(failures),
        "flakes": flakes,
        "m4_flake_rate_pct": (round(100.0 * flakes / len(completed), 2) if completed else None),
    }


def _fmt_seconds(value: Optional[float]) -> str:
    if value is None:
        return "UNMEASURED"
    if value < 90:
        return f"{value:.0f}s"
    return f"{value / 60:.1f}m"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=20, help="runs per workflow window")
    parser.add_argument("--branch", default="main", help="default branch to read")
    parser.add_argument("--json", action="store_true", help="emit a JSON snapshot")
    args = parser.parse_args(argv)

    snapshot = []
    for workflow in GATING_WORKFLOWS:
        runs = fetch_runs(workflow, args.branch, args.limit)
        snapshot.append(summarise(runs, workflow))

    if args.json:
        print(json.dumps({"branch": args.branch, "limit": args.limit, "workflows": snapshot}, indent=2))
        return 0

    print(f"# CI metrics — branch={args.branch} window={args.limit} runs per workflow")
    print()
    print("| Workflow | Runs | M2 p50 | M2 p90 | M3 p50 | M3 p90 | Failures | Flakes | M4 rate |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in snapshot:
        m4 = row["m4_flake_rate_pct"]
        print(
            f"| {row['workflow']} | {row['window_runs']} "
            f"| {_fmt_seconds(row['m2_p50_seconds'])} "
            f"| {_fmt_seconds(row['m2_p90_seconds'])} "
            f"| {_fmt_seconds(row['m3_p50_seconds'])} "
            f"| {_fmt_seconds(row['m3_p90_seconds'])} "
            f"| {row['failures']} | {row['flakes']} "
            f"| {'UNMEASURED' if m4 is None else f'{m4}%'} |"
        )
    print()
    for row in snapshot:
        if row["m2_unmeasured"]:
            print(
                f"note: {row['workflow']} has {row['m2_unmeasured']} failed run(s) whose "
                "job timings are unavailable; M2 is UNMEASURED for those, not zero."
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
