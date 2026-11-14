"""Re-verification harness for `resilience.md` (C1, H1-H3, M1-M6, L1-L5).

Drives the *real* CLI inside a pseudo-terminal so the interactive layer is
exercised for real, not stubbed. Every scenario is a (command, keystrokes,
winsize) triple; the runner reports exit status, whether the alternate screen was
left (`ESC[?1049l`), and how long the process lived (a timeout means "frozen").

    uv run python project-tasks/tui-review/reverify_probe.py
"""

from __future__ import annotations

import fcntl
import os
import pty
import re
import select
import signal
import struct
import sys
import termios
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[2]
ALT_SCREEN_LEAVE = "\x1b[?1049l"


@dataclass
class Result:
    name: str
    exit_code: Optional[int]
    seconds: float
    output: str
    timed_out: bool
    signal_no: Optional[int] = None

    @property
    def left_alt_screen(self) -> bool:
        return ALT_SCREEN_LEAVE in self.output

    def plain(self) -> str:
        """Output with ANSI/OSC sequences stripped, for message assertions."""
        text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", self.output)
        text = re.sub(r"\x1b\][^\x07\x1b]*(\x07|\x1b\\\\)", "", text)
        text = re.sub(r"\x1b[()][0-9A-B]", "", text)
        return text.replace("\r", "")


def run_in_pty(
    argv: Sequence[str],
    keys: Sequence[Tuple[float, str]] = (),
    size: Tuple[int, int] = (80, 24),
    timeout: float = 12.0,
    env_extra: Optional[dict] = None,
    signals: Sequence[Tuple[float, int]] = (),
) -> Result:
    """Run `argv` under a pty, send `keys` at the given delays, capture output."""
    cols, rows = size
    env = dict(os.environ)
    env.pop("COLUMNS", None)
    env.pop("LINES", None)
    env["TERM"] = "xterm-256color"
    env["NO_COLOR"] = ""
    if env_extra:
        env.update(env_extra)

    pid, fd = pty.fork()
    if pid == 0:  # child
        try:
            fcntl.ioctl(
                sys.__stdout__.fileno(),
                termios.TIOCSWINSZ,
                struct.pack("HHHH", rows, cols, 0, 0),
            )
        except Exception:
            pass
        os.execvpe(argv[0], list(argv), env)
        os._exit(127)

    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))

    started = time.time()
    chunks: List[bytes] = []
    pending = list(keys)
    pending_signals = list(signals)
    status: Optional[int] = None
    timed_out = False
    next_send = started + (pending[0][0] if pending else 1e9)

    while True:
        now = time.time()
        if status is None and now - started > timeout:
            timed_out = True
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            os.waitpid(pid, 0)
            break
        if pending_signals and now - started >= pending_signals[0][0]:
            _, signum = pending_signals.pop(0)
            try:
                os.kill(pid, signum)
            except ProcessLookupError:
                pass
        if pending and now >= next_send:
            _, payload = pending.pop(0)
            try:
                os.write(fd, payload.encode())
            except OSError:
                pass
            next_send = now + (pending[0][0] if pending else 1e9)
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                data = os.read(fd, 65536)
            except OSError:
                data = b""
            if not data:
                break
            chunks.append(data)
        if status is None:
            wpid, wstatus = os.waitpid(pid, os.WNOHANG)
            if wpid == pid:
                status = wstatus
                # drain
                deadline = time.time() + 1.0
                while time.time() < deadline:
                    r, _, _ = select.select([fd], [], [], 0.05)
                    if not r:
                        continue
                    try:
                        data = os.read(fd, 65536)
                    except OSError:
                        break
                    if not data:
                        break
                    chunks.append(data)
                break

    elapsed = time.time() - started
    os.close(fd)
    if status is None and not timed_out:
        _, status = os.waitpid(pid, 0)

    exit_code = None
    signal_no = None
    if status is not None:
        if os.WIFEXITED(status):
            exit_code = os.WEXITSTATUS(status)
        elif os.WIFSIGNALED(status):
            signal_no = os.WTERMSIG(status)

    return Result(
        name="",
        exit_code=exit_code,
        seconds=elapsed,
        output=b"".join(chunks).decode("utf-8", "replace"),
        timed_out=timed_out,
        signal_no=signal_no,
    )
