"""Probes v4: H2 atomic writes, L3 --jobs, L4/plugin, H1 end-to-end, M1c, L1 layout.

    uv run python project-tasks/tui-review/reverify_run4.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from reverify_probe import REPO  # noqa: E402

VENV_CLI = str(REPO / ".venv" / "bin" / "agency-agents")
PY = str(REPO / ".venv" / "bin" / "python")


def run(cmd, cwd=REPO, env_extra=None, script=None, timeout=180):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        cmd if script is None else [PY, "-c", script],
        capture_output=True, text=True, cwd=str(cwd), env=env, timeout=timeout,
    )


def last(out, n=4):
    text = (out.stdout + out.stderr).strip().splitlines()
    return " | ".join(ln.strip() for ln in text[-n:])


def main() -> None:
    print("=== H2: atomic write — interrupted write must not leave a torn artifact ===")
    script = r'''
import tempfile, pathlib
from unittest import mock
from agency_agents.infrastructure.installer import InstallationManager
root = pathlib.Path("CATALOG")
home = pathlib.Path(tempfile.mkdtemp())
m = InstallationManager(root, home, project_root=root)
target = home / ".claude" / "agents" / "x.md"
real = pathlib.Path.write_text
def torn(self, *a, **k):
    real(self, "PARTIAL", encoding="utf-8")      # simulate a truncated write
    raise OSError(28, "No space left on device")
with mock.patch.object(pathlib.Path, "write_text", torn):
    try:
        m._atomic_write(target, "FULL CONTENT")
    except OSError as e:
        print("RAISED", e)
print("target exists:", target.exists(), "| content:", target.read_text() if target.exists() else None)
print("tmp leftovers:", sorted(p.name for p in target.parent.iterdir()))
'''
    script = script.replace("CATALOG", str(REPO))
    out = run(None, script=script)
    print("   ", last(out, 4))

    print("\n=== H2b: .tmp name is fixed (concurrent installs collide?) ===")
    script = r'''
import tempfile, pathlib, os
from agency_agents.infrastructure.installer import InstallationManager
root = pathlib.Path("CATALOG")
home = pathlib.Path(tempfile.mkdtemp())
m = InstallationManager(root, home, project_root=root)
p = home / "x.md"
m._atomic_write(p, "A")
import inspect
print("tmp name for", p.name, "->", p.with_name(p.name + ".tmp").name)
'''
    script = script.replace("CATALOG", str(REPO))
    out = run(None, script=script)
    print("   ", last(out, 2))

    print("\n=== L3: --jobs 0 (unvalidated) end-to-end ===")
    h = tempfile.mkdtemp()
    out = run([VENV_CLI, "install", "--tool", "claude-code", "--agent", "anthropologist",
               "--no-interactive", "--parallel", "--jobs", "0"], env_extra={"HOME": h})
    print(f"    exit={out.returncode} |", last(out, 4))

    print("\n=== L4 / F-05: install_plugin no longer a silent no-op ===")
    script = r'''
import tempfile, pathlib
from agency_agents.infrastructure.installer import InstallationManager
root = pathlib.Path("CATALOG")
home = pathlib.Path(tempfile.mkdtemp())
m = InstallationManager(root, home, project_root=root)
for kebab in ("claude-code", "nope"):
    try:
        m.install_plugin(kebab)
    except Exception as e:
        print(kebab, "->", type(e).__name__, e)
'''
    script = script.replace("CATALOG", str(REPO))
    out = run(None, script=script)
    print("   ", last(out, 3))

    print("\n=== F-05b: missing `uv` on PATH -> RuntimeError, not traceback ===")
    script = r'''
import tempfile, pathlib, subprocess
from agency_agents.infrastructure.installer import InstallationManager
root = pathlib.Path("CATALOG")
home = pathlib.Path(tempfile.mkdtemp())
m = InstallationManager(root, home, project_root=root)
def boom(*a, **k):
    raise FileNotFoundError(2, "No such file or directory", "uv")
subprocess.run = boom
try:
    m.install_plugin("hermes")
except Exception as e:
    print("->", type(e).__name__, e)
'''
    script = script.replace("CATALOG", str(REPO))
    out = run(None, script=script)
    print("   ", last(out, 2))

    print("\n=== H1 end-to-end: read-only project scope (permission failure) ===")
    ro = tempfile.mkdtemp(prefix="aa-ro-")
    h = tempfile.mkdtemp(prefix="aa-rohome-")
    os.chmod(ro, 0o555)
    out = run([VENV_CLI, "install", "--tool", "claude-code", "--scope", "project",
               "--no-interactive"], cwd=ro, env_extra={"HOME": h})
    os.chmod(ro, 0o755)
    print(f"    exit={out.returncode} |", last(out, 4))

    print("\n=== M1c: non-interactive paths that install nothing ===")
    h = tempfile.mkdtemp()
    out = run([VENV_CLI, "install", "--tool", "claude-code", "--agent", "does-not-exist",
               "--no-interactive"], env_extra={"HOME": h})
    print(f"    --agent does-not-exist       exit={out.returncode} |", last(out, 2))
    h = tempfile.mkdtemp()
    empty = Path(h) / "ids.txt"
    empty.write_text("# nothing here\n")
    out = run([VENV_CLI, "install", "--tool", "claude-code", "--agents-file", str(empty),
               "--no-interactive"], env_extra={"HOME": h})
    print(f"    --agents-file (comments only) exit={out.returncode} |", last(out, 2))

    print("\n=== L1: long description — is the detail pane wrapped? ===")
    script = r'''
from agency_agents.infrastructure.browser import BrowserModel, BrowserRow
from agency_agents.infrastructure import browser_app as ba
rows = [BrowserRow("d", "a", "A", "word " * 400)]
m = BrowserModel(rows=rows)
screen = ba.render_screen(m)
detail = [t for s, t in screen if "word word" in t]
print("detail fragments:", len(detail), "| longest:", max((len(t) for t in detail), default=0))
import inspect
src = inspect.getsource(ba.run_browser)
print("wrap_lines in Window:", "wrap_lines" in src)
'''
    out = run(None, script=script)
    print("   ", last(out, 2))

    print("\n=== test suite ===")
    out = run([str(REPO / ".venv" / "bin" / "pytest"), "-q"], timeout=900)
    print("   ", last(out, 3))


if __name__ == "__main__":
    main()
