"""Probes v5: H3 root cause + verified one-line fix, and SIGINT inside the dialog.

    uv run python project-tasks/tui-review/reverify_run5.py
"""

from __future__ import annotations

import os
import signal
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from reverify_probe import REPO, run_in_pty  # noqa: E402

VENV_CLI = str(REPO / ".venv" / "bin" / "agency-agents")
PY = str(REPO / ".venv" / "bin" / "python")


def home() -> str:
    return tempfile.mkdtemp(prefix="aa-home-")


PROTOTYPE = r'''
import sys
from prompt_toolkit.application import Application, get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.widgets import Button, CheckboxList, Dialog, Label

values = [("claude-code", "Claude Code (claude-code)"), ("codex", "Codex (codex)")]
checkbox = CheckboxList(values=values, default_values=[])
bindings = KeyBindings()
bindings.add("tab")(focus_next)
bindings.add("s-tab")(focus_previous)

# THE FIX: one handler per key, not one two-key sequence.
@bindings.add("escape")
@bindings.add("c-c")
def _cancel(event):
    event.app.exit(exception=KeyboardInterrupt())

dialog = Dialog(
    title="Install into which tools?",
    body=HSplit([Label(text="Space toggles, Tab moves, Enter confirms, Esc cancels."), checkbox], padding=1),
    buttons=[
        Button(text="Ok", handler=lambda: get_app().exit(result=checkbox.current_values)),
        Button(text="Cancel", handler=lambda: get_app().exit(result=None)),
    ],
    with_background=True,
)
app = Application(layout=Layout(dialog), key_bindings=bindings, mouse_support=True, full_screen=True)
try:
    print("RESULT", app.run())
except KeyboardInterrupt:
    print("CANCELLED")
    sys.exit(1)
'''

SEQUENCE_ONLY = PROTOTYPE.replace(
    '''@bindings.add("escape")
@bindings.add("c-c")''',
    '''@bindings.add("escape", "c-c")''',
)


def main() -> None:
    print("=== H3 root cause: 'escape','c-c' is a two-key SEQUENCE, not two alternatives ===")
    for label, src, keys in (
        ("sequence variant, esc alone", SEQUENCE_ONLY, [(2.0, "\x1b")]),
        ("sequence variant, ctrl-c alone", SEQUENCE_ONLY, [(2.0, "\x03")]),
        ("fixed variant, esc alone", PROTOTYPE, [(2.0, "\x1b")]),
        ("fixed variant, ctrl-c alone", PROTOTYPE, [(2.0, "\x03")]),
        ("fixed variant, tab+enter (Ok)", PROTOTYPE, [(2.0, "\t"), (0.5, "\r")]),
    ):
        path = Path(tempfile.mkdtemp()) / "dlg.py"
        path.write_text(src)
        r = run_in_pty([PY, str(path)], keys=keys, size=(100, 30),
                       env_extra={"HOME": home()}, timeout=12)
        state = "FROZEN" if r.timed_out else f"exit={r.exit_code}"
        lines = [ln.strip() for ln in r.plain().splitlines() if ln.strip()]
        print(f"   {label:32s} {state:10s} {lines[-1][:70] if lines else ''}")

    print("\n=== M2b: SIGINT while the tool dialog is open ===")
    r = run_in_pty([VENV_CLI, "tui"],
                   keys=[(2.5, "\t"), (0.8, "\r")],
                   signals=[(4.0, signal.SIGINT)],
                   size=(100, 30), env_extra={"HOME": home()}, timeout=16)
    state = "FROZEN(timeout)" if r.timed_out else (
        f"signal={r.signal_no}" if r.signal_no is not None else f"exit={r.exit_code}")
    print(f"   dialog + SIGINT at t=4s -> {state} after {r.seconds:.1f}s")


if __name__ == "__main__":
    main()
