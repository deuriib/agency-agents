"""Child probe: drive the real `run_browser` on a real pty and print the exact
selection. Written by `final_gate_pty.py`; not part of the repo suite.
"""

from __future__ import annotations

import sys

from agency_agents.infrastructure import browser_app
from agency_agents.infrastructure.browser import BrowserModel, BrowserRow

model = BrowserModel(
    rows=[
        BrowserRow("backend", "backend-architect", "Backend Architect", "Designs APIs."),
        BrowserRow("growth", "growth-hacker", "Growth Hacker", "Runs experiments."),
        BrowserRow("sales", "deal-strategist", "Deal Strategist", "Closes deals."),
    ]
)

try:
    result = browser_app.run_browser(model, title="probe")
except browser_app.BrowserCancelled as exc:
    sys.stdout.write(f"\n@@SEL@@ CANCELLED {str(exc).splitlines()[0]}\n")
    sys.stdout.flush()
    raise SystemExit(0)
except BaseException as exc:  # noqa: BLE001 - probe must report, not crash
    sys.stdout.write(f"\n@@SEL@@ EXC {type(exc).__name__}: {exc}\n")
    sys.stdout.flush()
    raise SystemExit(0)

sys.stdout.write(f"\n@@SEL@@ RESULT {result!r}\n")
sys.stdout.flush()
