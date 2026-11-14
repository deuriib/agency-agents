"""Scenario runner for the re-verification of `resilience.md`.

    uv run python project-tasks/tui-review/reverify_run.py

Every scenario prints one line of evidence; nothing here is inferred.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from reverify_probe import REPO, run_in_pty  # noqa: E402

UV = shutil.which("uv") or "uv"


def cli(*args: str) -> list:
    return [UV, "run", "agency-agents", *args]


def home() -> str:
    d = tempfile.mkdtemp(prefix="aa-home-")
    return d


def show(name: str, r, extra: str = "") -> None:
    state = "FROZEN(timeout)" if r.timed_out else (
        f"signal={r.signal_no}" if r.signal_no is not None else f"exit={r.exit_code}"
    )
    print(
        f"[{name:26s}] {state:18s} {r.seconds:5.1f}s alt-screen-restored="
        f"{r.left_alt_screen!s:5s} {extra}"
    )


def last_lines(r, n: int = 6) -> str:
    text = r.plain()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return " | ".join(lines[-n:])


def main() -> None:
    print("=== M6: tiny terminal guard (40x15) ===")
    r = run_in_pty(cli("tui", "--tool", "claude-code"), size=(40, 15),
                   env_extra={"HOME": home()}, timeout=15)
    show("M6 40x15", r, last_lines(r, 3))

    print("\n=== M6b: COLUMNS env override in a large terminal (80x24) ===")
    r = run_in_pty(cli("tui", "--tool", "claude-code"),
                   keys=[(2.5, "\x1b")], size=(80, 24),
                   env_extra={"HOME": home(), "COLUMNS": "40", "LINES": "15"}, timeout=15)
    show("M6b COLUMNS=40", r, last_lines(r, 3))

    print("\n=== M4: --tool validated before the first frame ===")
    r = run_in_pty(cli("tui", "--tool", "bogus-tool"), keys=[(3.0, "\x1b")],
                   env_extra={"HOME": home()}, timeout=15)
    show("M4 unknown tool", r, last_lines(r, 3))

    print("\n=== M1a: browser Enter with nothing selected ===")
    r = run_in_pty(cli("tui", "--tool", "claude-code"), keys=[(2.5, "\r")],
                   env_extra={"HOME": home()}, timeout=15)
    show("M1a empty selection", r, last_lines(r, 3))

    print("\n=== M1b: browser Esc with a selection ===")
    r = run_in_pty(cli("tui", "--tool", "claude-code"), keys=[(2.5, "\t"), (0.4, "\x1b")],
                   env_extra={"HOME": home()}, timeout=15)
    show("M1b esc after tab", r, last_lines(r, 3))

    print("\n=== M5: arrow keys must move the cursor (dry-run plan) ===")
    r_tab = run_in_pty(cli("tui", "--tool", "claude-code", "--dry-run"),
                       keys=[(2.5, "\t"), (0.4, "\r")], env_extra={"HOME": home()}, timeout=20)
    r_down = run_in_pty(cli("tui", "--tool", "claude-code", "--dry-run"),
                        keys=[(2.5, "\x1b[B"), (0.4, "\t"), (0.4, "\r")],
                        env_extra={"HOME": home()}, timeout=20)
    plan = lambda r: [ln for ln in r.plain().splitlines() if "/" in ln and " - " in ln]
    print("   tab+enter plan   :", plan(r_tab)[:3])
    print("   down+tab+enter   :", plan(r_down)[:3])
    show("M5 tab only", r_tab, "")
    show("M5 down+tab", r_down, "")

    print("\n=== M2: SIGINT while the browser is up ===")
    r = run_in_pty(cli("tui", "--tool", "claude-code"), signals=[(3.0, signal.SIGINT)],
                   env_extra={"HOME": home()}, timeout=20)
    show("M2 SIGINT", r, last_lines(r, 3))

    print("\n=== C1: exception raised by the key handler ===")
    script = Path(tempfile.mkdtemp()) / "c1.py"
    script.write_text(
        "import sys\n"
        "import agency_agents.infrastructure.browser_app as ba\n"
        "from agency_agents.infrastructure.browser import BrowserModel, BrowserRow\n"
        "m = BrowserModel(rows=[BrowserRow('d', 'a', 'A', 'desc')])\n"
        "orig = ba.apply_key\n"
        "n = {'i': 0}\n"
        "def boom(model, key):\n"
        "    n['i'] += 1\n"
        "    if n['i'] >= 2:\n"
        "        raise RuntimeError('boom from apply_key')\n"
        "    return orig(model, key)\n"
        "ba.apply_key = boom\n"
        "try:\n"
        "    print('RETURN', ba.run_browser(m))\n"
        "except ba.BrowserCancelled as e:\n"
        "    print('CANCELLED:', e)\n"
        "    sys.exit(1)\n"
    )
    r = run_in_pty([UV, "run", "python", str(script)],
                   keys=[(3.0, "x"), (0.6, "y"), (0.6, "\r")],
                   env_extra={"HOME": home()}, timeout=25)
    show("C1 handler raises", r, last_lines(r, 3))

    print("\n=== M3: EOF on stdin (pipe closed) ===")
    script2 = Path(tempfile.mkdtemp()) / "m3.py"
    script2.write_text(
        "import sys\n"
        "from unittest import mock\n"
        "from prompt_toolkit.application import create_app_session\n"
        "from prompt_toolkit.input import create_pipe_input\n"
        "from prompt_toolkit.output import DummyOutput\n"
        "from agency_agents.infrastructure.browser import BrowserModel, BrowserRow\n"
        "from agency_agents.infrastructure import browser_app as ba\n"
        "m = BrowserModel(rows=[BrowserRow('d','a','A','desc')])\n"
        "with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):\n"
        "    with mock.patch('shutil.get_terminal_size', lambda *a, **k: __import__('os').terminal_size((80,24))):\n"
        "        pipe.close()\n"
        "        try:\n"
        "            print('RETURN', ba.run_browser(m))\n"
        "        except ba.BrowserCancelled as e:\n"
        "            print('CANCELLED:', e)\n"
        "        except BaseException as e:\n"
        "            print('ESCAPED:', type(e).__name__, e)\n"
    )
    out = subprocess.run([UV, "run", "python", str(script2)], capture_output=True, text=True,
                         cwd=REPO, timeout=180)
    print("   ", (out.stdout + out.stderr).strip().splitlines()[-1:])

    print("\n=== L2: choose_tools with piped stdin/stdout ===")
    script3 = Path(tempfile.mkdtemp()) / "l2.py"
    script3.write_text(
        "from agency_agents.infrastructure import browser_app as ba\n"
        "from agency_agents.infrastructure.catalog import CatalogManager\n"
        "from agency_agents.cli.main import resolve_catalog_root\n"
        "tools = CatalogManager(resolve_catalog_root()).load_tools().tools\n"
        "try:\n"
        "    print('RETURN', ba.choose_tools(tools, scope='user'))\n"
        "except ba.BrowserCancelled as e:\n"
        "    print('CANCELLED:', e)\n"
        "except BaseException as e:\n"
        "    print('ESCAPED:', type(e).__name__, e)\n"
    )
    out = subprocess.run([UV, "run", "python", str(script3)], capture_output=True, text=True,
                         cwd=REPO, timeout=180, stdin=subprocess.DEVNULL)
    text = out.stdout
    print("    lines written to pipe:", len(text.splitlines()),
          "| last:", text.strip().splitlines()[-1:] , "| boxes:", text.count("┌") + text.count("\x1b"))
    print("    stderr tail:", (out.stderr.strip().splitlines() or [""])[-1])

    print("\n=== H1: one unexpected exception must not abort the batch ===")
    script4 = Path(tempfile.mkdtemp()) / "h1.py"
    script4.write_text(
        "from rich.console import Console\n"
        "from agency_agents.cli.main import _install_agents\n"
        "class F:\n"
        "    def install_all_for_tool(self, agents, tool, **kw):\n"
        "        if tool == 't2':\n"
        "            raise PermissionError(13, 'Permission denied')\n"
        "        print('INSTALLED', tool)\n"
        "f = _install_agents(Console(), F(), [], ['t1', 't2', 't3'], 'user')\n"
        "print('FAILURES', f)\n"
    )
    out = subprocess.run([UV, "run", "python", str(script4)], capture_output=True, text=True,
                         cwd=REPO, timeout=180)
    print("   ", " | ".join((out.stdout + out.stderr).strip().splitlines()[-5:]))


if __name__ == "__main__":
    main()
