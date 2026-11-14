"""Focused probes, v3: dialog two-phase (H3), arrow-key install proof (M5), EOF (M3).

    uv run python project-tasks/tui-review/reverify_run3.py
"""

from __future__ import annotations

import os
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
    print(f"[{name:32s}] {state:16s} {r.seconds:5.1f}s {extra}")


def tail(r, n=2):
    lines = [ln.strip() for ln in r.plain().splitlines() if ln.strip()]
    return " | ".join(lines[-n:])


def after_alt(r) -> str:
    text = r.plain()
    idx = text.rfind(ALT_SCREEN_LEAVE)
    return text[idx + len(ALT_SCREEN_LEAVE):] if idx != -1 else text


def installed(home_dir: str):
    base = Path(home_dir) / ".claude" / "agents"
    if not base.exists():
        return ["<no dir>"]
    return sorted(p.name for p in base.iterdir())


def main() -> None:
    print("=== M5: does Down actually move the cursor? (real install into temp HOME) ===")
    for label, keys in (
        ("tab+enter", [(2.5, "\t"), (0.6, "\r")]),
        ("down+tab+enter", [(2.5, "\x1b[B"), (0.6, "\t"), (0.6, "\r")]),
        ("pagedown+tab+enter", [(2.5, "\x1b[6~"), (0.6, "\t"), (0.6, "\r")]),
        ("ctrl-n+tab+enter", [(2.5, "\x0e"), (0.6, "\t"), (0.6, "\r")]),
    ):
        h = home()
        r = run_in_pty([VENV_CLI, "tui", "--tool", "claude-code"], keys=keys,
                       size=(100, 30), env_extra={"HOME": h}, timeout=25)
        files = installed(h)
        print(f"   {label:20s} exit={r.exit_code} files={files} msg={tail(r, 1)[:60]}")

    print("\n=== M3: EOF while the browser runs (stdin/stdout claim to be ttys) ===")
    script = Path(tempfile.mkdtemp()) / "m3.py"
    script.write_text(
        "import sys, os\n"
        "from unittest import mock\n"
        "from prompt_toolkit.application import create_app_session\n"
        "from prompt_toolkit.input import create_pipe_input\n"
        "from prompt_toolkit.output import DummyOutput\n"
        "from agency_agents.infrastructure.browser import BrowserModel, BrowserRow\n"
        "from agency_agents.infrastructure import browser_app as ba\n"
        "m = BrowserModel(rows=[BrowserRow('d','a','A','desc')])\n"
        "with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):\n"
        "    with mock.patch.object(sys.stdin, 'isatty', lambda: True), \\\n"
        "         mock.patch.object(sys.stdout, 'isatty', lambda: True), \\\n"
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

    print("\n=== H3: tool dialog, reached after selecting an agent (no detected tool) ===")
    def dialog(label, keys):
        h = home()
        r = run_in_pty([VENV_CLI, "tui"], keys=[(2.5, "\t"), (0.8, "\r")] + keys,
                       size=(100, 30), env_extra={"HOME": h}, timeout=16)
        show(f"H3 {label}", r, f"files={installed(h)} msg={tail(r, 2)[-60:]}")

    dialog("esc", [(2.5, "\x1b")])
    dialog("ctrl-c", [(2.5, "\x03")])
    dialog("esc then ctrl-c", [(2.5, "\x1b"), (0.6, "\x03")])
    dialog("esc esc", [(2.5, "\x1b"), (0.6, "\x1b")])
    dialog("tab,enter (Ok, none picked)", [(2.5, "\t"), (0.6, "\r")])
    dialog("tab,tab,enter (Cancel)", [(2.5, "\t"), (0.5, "\t"), (0.6, "\r")])
    dialog("space,tab,enter (pick+Ok)", [(2.5, " "), (0.5, "\t"), (0.6, "\r")])
    dialog("enter on list", [(2.5, "\r")])

    print("\n=== H3b: dialog in a legal-but-cramped 60x20 terminal ===")
    h = home()
    r = run_in_pty([VENV_CLI, "tui"], keys=[(2.5, "\t"), (0.8, "\r"), (2.5, "\x1b"), (0.6, "\x03")],
                   size=(60, 20), env_extra={"HOME": h}, timeout=18)
    show("H3b 60x20", r, f"files={installed(h)} msg={tail(r, 1)[-60:]}")


if __name__ == "__main__":
    main()
