"""Focused probes: SIGINT (M2), EOF (M3), dialog escape hatch (H3), arrow keys (M5).

    uv run python project-tasks/tui-review/reverify_run2.py
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from reverify_probe import ALT_SCREEN_LEAVE, REPO, run_in_pty  # noqa: E402

VENV_CLI = str(REPO / ".venv" / "bin" / "agency-agents")
PY = str(REPO / ".venv" / "bin" / "python")


def home() -> str:
    return tempfile.mkdtemp(prefix="aa-home-")


def show(name, r, extra=""):
    state = "FROZEN(timeout)" if r.timed_out else (
        f"signal={r.signal_no}" if r.signal_no is not None else f"exit={r.exit_code}"
    )
    print(f"[{name:28s}] {state:18s} {r.seconds:5.1f}s alt-restored={r.left_alt_screen!s:5s} {extra}")


def tail(r, n=4):
    lines = [ln.strip() for ln in r.plain().splitlines() if ln.strip()]
    return " | ".join(lines[-n:])


def after_alt_screen(r) -> str:
    text = r.plain()
    idx = text.rfind(ALT_SCREEN_LEAVE)
    return text[idx + len(ALT_SCREEN_LEAVE):] if idx != -1 else text


def main() -> None:
    print("=== M2: SIGINT to the real CLI process (no uv wrapper) ===")
    for label, signum in (("SIGINT", signal.SIGINT), ("SIGTERM", signal.SIGTERM)):
        r = run_in_pty([VENV_CLI, "tui", "--tool", "claude-code"],
                       signals=[(3.0, signum)], env_extra={"HOME": home()}, timeout=20)
        show(f"M2 {label}", r, tail(r, 2))

    print("\n=== M2b: SIGINT to the process group (what a Ctrl-C-bearing wrapper does) ===")
    r = run_in_pty(["bash", "-c", f"exec {VENV_CLI} tui --tool claude-code"],
                   signals=[(3.0, signal.SIGINT)], env_extra={"HOME": home()}, timeout=20)
    show("M2b SIGINT exec", r, tail(r, 2))

    print("\n=== M3: EOFError out of application.run ===")
    script = Path(tempfile.mkdtemp()) / "m3.py"
    script.write_text(
        "import os\n"
        "from unittest import mock\n"
        "from prompt_toolkit.application import create_app_session\n"
        "from prompt_toolkit.input import create_pipe_input\n"
        "from prompt_toolkit.output import DummyOutput\n"
        "from agency_agents.infrastructure.browser import BrowserModel, BrowserRow\n"
        "from agency_agents.infrastructure import browser_app as ba\n"
        "m = BrowserModel(rows=[BrowserRow('d','a','A','desc')])\n"
        "with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):\n"
        "    with mock.patch.object(os, 'isatty', lambda fd: True), \\\n"
        "         mock.patch('shutil.get_terminal_size', lambda *a, **k: os.terminal_size((80,24))):\n"
        "        pipe.close()\n"
        "        try:\n"
        "            print('RETURN', ba.run_browser(m))\n"
        "        except ba.BrowserCancelled as e:\n"
        "            print('CANCELLED:', e)\n"
        "        except BaseException as e:\n"
        "            print('ESCAPED:', type(e).__name__, e)\n"
    )
    out = subprocess.run([PY, str(script)], capture_output=True, text=True, cwd=REPO, timeout=180)
    print("   ", ((out.stdout + out.stderr).strip().splitlines() or ["<none>"])[-1])

    print("\n=== M5: arrow keys in a real terminal (70x30) ===")
    for label, keys in (
        ("tab+enter", [(2.5, "\t"), (0.5, "\r")]),
        ("down+tab+enter", [(2.5, "\x1b[B"), (0.5, "\t"), (0.5, "\r")]),
        ("pagedown+tab+enter", [(2.5, "\x1b[6~"), (0.5, "\t"), (0.5, "\r")]),
    ):
        r = run_in_pty([VENV_CLI, "tui", "--tool", "claude-code", "--dry-run"],
                       keys=keys, size=(100, 30), env_extra={"HOME": home()}, timeout=25)
        body = after_alt_screen(r)
        plan = [ln.strip() for ln in body.splitlines() if "→" in ln or "->" in ln or "- " in ln]
        print(f"   {label:20s} exit={r.exit_code} plan-lines={len(plan)} first={plan[:2]}")

    print("\n=== H3: the tool dialog (no detected tool -> picker) ===")
    cases = [
        ("esc", [(2.5, "\x1b")]),
        ("ctrl-c", [(2.5, "\x03")]),
        ("esc then ctrl-c", [(2.5, "\x1b"), (0.5, "\x03")]),
        ("tab,enter (Ok)", [(2.5, "\t"), (0.5, "\r")]),
        ("tab,tab,enter (Cancel)", [(2.5, "\t"), (0.4, "\t"), (0.4, "\r")]),
        ("space,tab,enter (pick)", [(2.5, " "), (0.4, "\t"), (0.4, "\r")]),
        ("enter on list", [(2.5, "\r")]),
    ]
    for label, keys in cases:
        r = run_in_pty([VENV_CLI, "tui"], keys=keys, env_extra={"HOME": home()}, timeout=14)
        show(f"H3 dialog {label}", r, tail(r, 2))

    print("\n=== H3b: dialog in a small-but-legal terminal (60x20) ===")
    r = run_in_pty([VENV_CLI, "tui"], keys=[(2.5, "\t"), (0.5, "\r")],
                   size=(60, 20), env_extra={"HOME": home()}, timeout=14)
    show("H3b 60x20", r, tail(r, 2))


if __name__ == "__main__":
    main()
