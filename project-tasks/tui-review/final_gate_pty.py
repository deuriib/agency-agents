"""Independent pty gate for the final production-readiness review.

Not collected by the repo suite (outside the package). It drives the *real CLI*
(`agency-agents tui --dry-run`) on a real pseudo-terminal so the verdicts in
`reality-check-final.md` are observed behaviour, not a re-reading of the diff.

Run from the repository root:

    .venv/bin/python project-tasks/tui-review/final_gate_pty.py

Each case prints one line: `CASE <name> exit=<code> <PASS|FAIL> <detail>`.
"""

from __future__ import annotations

import fcntl
import os
import pty
import re
import select
import struct
import subprocess
import sys
import termios
import time
from pathlib import Path
from typing import List, Tuple

REPO = Path(__file__).resolve().parents[2]
VENV_PY = REPO / ".venv" / "bin" / "python"
CHILD = [str(VENV_PY), "-m", "agency_agents"]


def drive(argv: List[str], keys: bytes, cols: int = 100, lines: int = 24,
          drain: float = 12.0, settle: float = 3.0) -> Tuple[int, str]:
    """Run one CLI session on a real pty; return (exit_code, cleaned frame)."""
    master, slave = pty.openpty()
    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", lines, cols, 0, 0))
    env = dict(os.environ, TERM="xterm-256color", COLUMNS=str(cols), LINES=str(lines))
    # "@script" runs a standalone child module instead of the packaged CLI.
    command = [str(VENV_PY), argv[1]] if argv[0] == "@script" else CHILD + argv
    proc = subprocess.Popen(
        command, stdin=slave, stdout=slave, stderr=slave,
        cwd=str(REPO), env=env, close_fds=True,
    )
    os.close(slave)
    frame = bytearray()

    def pump(seconds: float, until: bytes | None = None) -> None:
        end = time.time() + seconds
        while True:
            left = end - time.time()
            if left <= 0:
                return
            ready, _, _ = select.select([master], [], [], min(left, 0.05))
            if not ready:
                if until is not None and until in frame:
                    return
                continue
            try:
                chunk = os.read(master, 65536)
            except OSError:
                return
            if not chunk:
                return
            frame.extend(chunk)
            if until is not None and until in frame:
                return

    # Wait for the first frame: in raw mode the terminal no longer eats the
    # control bytes we are about to type.
    pump(drain, until=b"Browse agents")
    if keys:
        os.write(master, keys)
    pump(settle)
    try:
        code = proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        code = -9
    pump(0.3)
    os.close(master)
    text = frame.decode("utf-8", "replace")
    text = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", text)
    text = re.sub(r"\x1b[()][A-Za-z0-9]", "", text)
    text = re.sub(r"\x1b[=>78]", "", text)
    return code, text


CASES: List[Tuple[str, List[str], bytes, int, int, int, List[Tuple[str, bool]]]] = [
    # name, argv, keys, cols, rows, expected_exit, [(needle, must_be_present)]
    (
        "A accept-2nd-row", ["tui", "--dry-run"], b"\x1b[B\t\r", 100, 24, 0,
        [("Dry run complete", True), ("1 agents", True)],
    ),
    (
        "A2 enter-nothing-selected", ["tui", "--dry-run"], b"\r", 100, 24, 1,
        [("Nothing selected", True), ("Dry run complete", False)],
    ),
    (
        "A3 invalid-tool-before-browse", ["tui", "--tool", "[/x]", "--dry-run"], b"", 100, 24, 1,
        [("Unknown tool", True), ("Browse agents", False)],
    ),
    (
        "A4 invalid-scope-before-browse", ["tui", "--scope", "[/x]", "--dry-run"], b"", 100, 24, 1,
        [("Invalid scope", True), ("Browse agents", False)],
    ),
    (
        "B esc-with-selection", ["tui", "--dry-run"], b"\t\x1b", 100, 24, 1,
        [("cancelled", True), ("Dry run complete", False), ("Installed", False)],
    ),
    (
        "C ctrl-c-with-selection", ["tui", "--dry-run"], b"\t\x03", 100, 24, 1,
        [("cancelled", True), ("Dry run complete", False)],
    ),
    (
        "D filter-then-accept", ["tui", "--dry-run"], b"growth\t\r", 100, 24, 0,
        [("growth-hacker", True), ("Dry run complete", True)],
    ),
    (
        "E 24-row-help-line-visible", ["tui", "--dry-run"], b"\x1b", 100, 24, 1,
        [("esc cancel", True), ("enter install", True)],
    ),
    (
        "F 19-row-refused", ["tui", "--dry-run"], b"", 100, 19, 1,
        [("needs at least 60x20", True)],
    ),
    (
        "G paste-cr-does-not-install", ["tui", "--dry-run"], b"\t\x1b[200~\r\x1b[201~\x1b", 100, 24, 1,
        [("Dry run complete", False), ("cancelled", True)],
    ),
    (
        "H2 60x20-boundary-accepts", ["tui", "--dry-run"], b"\t\r", 60, 20, 0,
        [("Dry run complete", True), ("1 agents", True)],
    ),
    (
        "H3 59-cols-refused", ["tui", "--dry-run"], b"", 59, 24, 1,
        [("needs at least 60x20", True), ("Browse agents", False)],
    ),
    (
        "H4 20-rows-help-visible", ["tui", "--dry-run"], b"\x1b", 80, 20, 1,
        [("esc cancel", True)],
    ),
    (
        "H bare-install-esc", ["install"], b"\x1b", 100, 24, 1,
        [("cancelled", True), ("Dry run complete", False)],
    ),
]


def main() -> int:
    failures = 0
    for name, argv, keys, cols, rows, expected_code, checks in CASES:
        code, text = drive(argv, keys, cols=cols, lines=rows)
        problems = []
        for needle, present in checks:
            if present and needle not in text:
                problems.append(f"missing:{needle!r}")
            if not present and needle in text:
                problems.append(f"unexpected:{needle!r}")
        if "Traceback (most recent call last)" in text:
            problems.append("traceback")
        if code != expected_code:
            problems.append(f"exit={code} expected={expected_code}")
        verdict = "PASS" if not problems else "FAIL"
        failures += bool(problems)
        print(f"CASE {name} exit={code} {verdict} {'; '.join(problems) or 'ok'}")
    probes = [
        ("P1 down-tab-enter", b"\x1b[B\t\r", "RESULT ['growth-hacker']"),
        ("P2 down-down-tab-enter", b"\x1b[B\x1b[B\t\r", "RESULT ['deal-strategist']"),
        ("P3 pagedown-tab-enter", b"\x1b[6~\t\r", "RESULT ['deal-strategist']"),
        ("P4 c-a-esc", b"\x01\x1b", "CANCELLED"),
        ("P5 tab-enter", b"\t\r", "RESULT ['backend-architect']"),
        ("P6 c-q-after-tab", b"\t\x11", "CANCELLED"),
    ]
    for name, keys, needle in probes:
        code, text = drive(["@script", str(REPO / "project-tasks/tui-review/_sel_probe.py")],
                           keys, cols=100, lines=30)
        line = next((l for l in text.splitlines() if "@@SEL@@" in l), "NO-VERDICT")
        ok = needle in line
        failures += not ok
        print(f"PROBE {name} {line.strip().split('@@SEL@@')[-1].strip()!r} "
              f"{'PASS' if ok else 'FAIL'} (want {needle!r})")
    total = len(CASES) + len(probes)
    print(f"SUMMARY {total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
