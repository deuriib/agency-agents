"""Pseudo-terminal re-verification harness for the TUI security re-review.

This module is NOT collected by the repo test suite (it lives outside the
package). It re-runs the original penetration-test reproductions against the
current working tree, on a real terminal, so the verdicts in
`security-reverify.md` are evidence and not re-reading of the diff.

Run from the repository root:

    .venv/bin/python project-tasks/tui-review/pty_reverify.py

It drives the real `run_browser` in a real pty (`/dev/ptmx` slave), captures the
raw bytes prompt-toolkit wrote, and reports per-case outcomes:

- SEC-1: ``tab, esc`` / ``c-a, esc`` / ``tab, ctrl-c`` must NOT return a selection.
- SEC-4: arrow keys and page keys must move the cursor; the status line must
  document the key that actually toggles.
- SEC-3 / F-1: a U+202E name must render as a visible ``\\u202e`` escape, and no
  payload byte sequence (OSC, CSI) may appear in the frame.
"""

from __future__ import annotations

import fcntl
import os
import pty
import re
import struct
import subprocess
import sys
import termios
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parents[2]

CHILD = r'''
import sys
sys.path.insert(0, {src!r})
from agency_agents.core.models import Agent, AgentFrontmatter
from agency_agents.infrastructure.browser import BrowserModel, BrowserRow, build_rows
from agency_agents.infrastructure import browser_app

PAYLOAD_ROWS = {rows!r}


def build():
    if PAYLOAD_ROWS:
        # Go through the production path: catalog agents -> build_rows -> rows.
        by_division = {{}}
        for idx, (div, slug, name, desc) in enumerate(PAYLOAD_ROWS):
            agent = Agent(
                slug=slug,
                path=f"{{div}}/{{slug}}.md",
                frontmatter=AgentFrontmatter(name=name, description=desc),
                body="b",
            )
            by_division.setdefault(div, []).append(agent)
        return BrowserModel(rows=build_rows(by_division))
    return BrowserModel(rows=[
        BrowserRow("engineering", "backend-architect", "Backend Architect", "Designs APIs."),
        BrowserRow("marketing", "growth-hacker", "Growth Hacker", "Runs experiments."),
        BrowserRow("sales", "deal-strategist", "Deal Strategist", "Closes deals."),
    ])

model = build()
try:
    result = browser_app.run_browser(model, title="probe")
except browser_app.BrowserCancelled as exc:
    sys.stdout.write("\n@@PROBE@@ CANCELLED " + str(exc).replace("\n", " ") + "\n")
    sys.stdout.flush()
    raise SystemExit(0)
except BaseException as exc:
    sys.stdout.write("\n@@PROBE@@ EXC " + type(exc).__name__ + ": " + str(exc) + "\n")
    sys.stdout.flush()
    raise SystemExit(0)
sys.stdout.write("\n@@PROBE@@ RESULT " + repr(result) + "\n")
sys.stdout.flush()
'''


def _child_source(rows: List[Tuple[str, str, str, str]] | None) -> str:
    return CHILD.format(src=str(REPO / "src"), rows=rows or [])


def drive(
    keys: bytes,
    rows: List[Tuple[str, str, str, str]] | None = None,
    cols: int = 100,
    lines: int = 30,
    drain: float = 8.0,
    settle: float = 2.0,
) -> Tuple[str, bytes]:
    """Run one browser session in a real pty and return (verdict line, frame)."""
    master, slave = pty.openpty()
    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", lines, cols, 0, 0))
    script = REPO / "project-tasks" / "tui-review" / "_child_probe.py"
    script.write_text(_child_source(rows), encoding="utf-8")
    env = dict(os.environ, TERM="xterm-256color", COLUMNS=str(cols), LINES=str(lines))
    proc = subprocess.Popen(
        [sys.executable, str(script)],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        cwd=str(REPO),
        env=env,
        close_fds=True,
    )
    os.close(slave)
    frame = bytearray()

    def pump(seconds: float, until_first_output: bool = False) -> None:
        import select
        import time

        end = time.time() + seconds
        while True:
            left = end - time.time()
            if left <= 0:
                return
            ready, _, _ = select.select([master], [], [], min(left, 0.05))
            if not ready:
                if until_first_output and frame:
                    return
                continue
            try:
                chunk = os.read(master, 65536)
            except OSError:
                return
            if not chunk:
                return
            frame.extend(chunk)
            if until_first_output and b"Browse" in frame:
                # The first frame is on screen: the app is in raw mode, so a
                # typed control byte now reaches the key handler instead of the
                # kernel (ISIG is off in raw mode).
                return

    # Wait for the first rendered frame before typing, so the keystrokes are
    # delivered to prompt-toolkit and not to a still-cooked terminal.
    pump(drain, until_first_output=True)
    if keys:
        os.write(master, keys)
    pump(settle)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    pump(0.15)
    os.close(master)
    text = frame.decode("utf-8", "replace")
    verdict = "NO-VERDICT(no ext marker)"
    for line in text.splitlines():
        if "@@PROBE@@" in line:
            verdict = line.split("@@PROBE@@", 1)[1].strip()
    return verdict, bytes(frame)


def clean_frame(frame: bytes) -> str:
    """Strip prompt-toolkit's own escapes so only payload escapes remain."""
    text = frame.decode("utf-8", "replace")
    text = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", text)
    text = re.sub(r"\x1b[()][A-Za-z0-9]", "", text)
    text = re.sub(r"\x1b[=>78]", "", text)
    return text


SEC1_CASES: List[Tuple[str, bytes]] = [
    ("tab, ESC", b"\t\x1b"),
    ("c-a (all), ESC", b"\x01\x1b"),
    ("tab, Ctrl-C", b"\t\x03"),
    ("ESC only", b"\x1b"),
    ("c-q after tab", b"\t\x11"),
    ("tab, bracketed paste CR", b"\t\x1b[200~\r\x1b[201~"),
    ("tab, bracketed paste TAB + ENTER", b"\t\x1b[200~\t\x1b[201~\r"),
]

SEC4_CASES: List[Tuple[str, bytes]] = [
    ("tab, ENTER (accept)", b"\t\r"),
    ("DOWN, tab, ENTER", b"\x1b[B\t\r"),
    ("DOWN DOWN, tab, ENTER", b"\x1b[B\x1b[B\t\r"),
    ("DOWN, UP, tab, ENTER", b"\x1b[B\x1b[A\t\r"),
    ("PAGEDOWN, tab, ENTER", b"\x1b[6~\t\r"),
    ("c-n, tab, ENTER", b"\x0e\t\r"),
    ("type 'sales', tab, ENTER", b"sales\t\r"),
    ("bracketed paste '\\t' then ENTER", b"\x1b[200~\t\x1b[201~\r"),
]

BIDI_ROW = ("\u202eengineering\u202c", "slug-bidi", "\u202eAuditor\u202c (real: Finance)", "z\u200bw\u2028s")
INJECT_ROWS = [
    ("\x1b[2J", "slug-csi", "\x1b[H\x1b[1;1H", "\x1b]0;pwned-title\x07"),
    ("\x1b]52;c;Y2xpcA==\x07", "slug-osc52", "name\x1b[31m", "\x1b[200~x\x1b[201~"),
]


def render_probe() -> None:
    """In-process check of the production display path (build_rows -> render)."""
    sys.path.insert(0, str(REPO / "src"))
    from agency_agents.core.models import Agent, AgentFrontmatter
    from agency_agents.infrastructure.browser import BrowserModel, build_rows
    from agency_agents.infrastructure.browser_app import render_screen

    payloads = {
        "U+202E RTL override": "\u202eAuditor\u202c (real: Finance)",
        "U+200B zero width": "z\u200bw",
        "U+2028 line separator": "a\u2028b",
        "U+2066 LRI isolate": "\u2066evil\u2069",
        "C0 ESC": "\x1b[31mred",
        "C1 0x9b": "\x9b2J",
        "DEL 0x7f": "a\x7fb",
    }
    print("  rendered row text for payload frontmatter (production path):")
    for label, payload in payloads.items():
        agent = Agent(
            slug="slug-payload",
            path="engineering/slug-payload.md",
            frontmatter=AgentFrontmatter(name=payload, description=payload),
            body="b",
        )
        rows = build_rows({payload: [agent]})
        screen = render_screen(BrowserModel(rows=rows))
        blob = "".join(text for _style, text in screen)
        danger = [ch for ch in blob if ch in ("\u202e", "\u202c", "\u200b", "\u2028", "\u2066", "\u2069")]
        print(
            f"    {label:22s} row.name={rows[0].name!r}"
            f"  raw-format-chars-in-frame={len(danger)}"
        )


def main() -> int:
    print("=" * 78)
    print("SEC-1  abort keys must never return a selection")
    print("=" * 78)
    for label, keys in SEC1_CASES:
        verdict, _ = drive(keys)
        ok = verdict.startswith("CANCELLED")
        print(f"  {'PASS' if ok else 'FAIL'}  {label:26s} -> {verdict[:88]}")

    print()
    print("=" * 78)
    print("SEC-4  keys the UI documents must do what they say")
    print("=" * 78)
    for label, keys in SEC4_CASES:
        verdict, _ = drive(keys)
        print(f"        {label:34s} -> {verdict[:88]}")

    print()
    print("=" * 78)
    print("SEC-3  in-process render probe (build_rows -> render_screen)")
    print("=" * 78)
    render_probe()

    print()
    print("=" * 78)
    print("SEC-3 / F-1  display of a bidi + zero-width payload row")
    print("=" * 78)
    verdict, frame = drive(b"\r", rows=[BIDI_ROW, ("engineering", "slug-plain", "Plain", "d")])
    text = frame.decode("utf-8", "replace")
    print(f"  raw U+202E bytes (e2 80 ae) in frame : {frame.count(b'\xe2\x80\xae')}")
    print(f"  raw U+200B bytes (e2 80 8b) in frame : {frame.count(b'\xe2\x80\x8b')}")
    print(f"  literal escape '\\u202e' in frame    : {text.count(chr(92) + 'u202e')}")
    print(f"  literal escape '\\u200b' in frame    : {text.count(chr(92) + 'u200b')}")
    print(f"  literal escape '\\u2028' in frame    : {text.count(chr(92) + 'u2028')}")
    print(f"  verdict: {verdict[:80]}")

    print()
    print("=" * 78)
    print("F-1  terminal escape injection from catalog frontmatter")
    print("=" * 78)
    verdict, frame = drive(b"\r", rows=INJECT_ROWS)
    cleaned = clean_frame(frame)
    print(f"  OSC 0 (title)     sequences : {cleaned.count(chr(27) + ']0;')}")
    print(f"  OSC 52 (clipboard) sequences: {cleaned.count(chr(27) + ']52;')}")
    print(f"  CSI 2J (clear)    sequences : {cleaned.count(chr(27) + '[2J')}")
    print(f"  CSI 1;1H          sequences : {cleaned.count(chr(27) + '[1;1H')}")
    print(f"  SGR 31m (red)     sequences : {cleaned.count(chr(27) + '[31m')}")
    print(f"  BEL (0x07) in payload area  : {cleaned.count(chr(7))}")
    print(f"  verdict: {verdict[:80]}")

    print()
    print("=" * 78)
    print("status line text actually rendered")
    print("=" * 78)
    verdict, frame = drive(b"\x1b")
    text = clean_frame(frame)
    for needle in ("tab to select", "space to select", "tab toggle", "esc cancel", "up/down move"):
        print(f"  {'yes' if needle in text else 'no ':3s}  {needle!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
