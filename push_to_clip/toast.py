"""Best-effort desktop toast notification.

The toast is a nicety, never a requirement: every failure is swallowed so a
missing notifier can never break the actual clipboard copy.

Windows uses the bundled ``toast.ps1`` (shipped as package data), which
self-registers an AppUserModelId under HKCU on every run — without a
registered AppId, Windows accepts the toast but never renders a banner.
It must run under Windows PowerShell 5.1 (``powershell.exe``): the WinRT
projection it relies on is not available in PowerShell 7 (``pwsh``).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys


def notify(
    title: str,
    message: str,
    *,
    source: str | None = None,
    target: str | None = None,
    urgent: bool = False,
) -> None:
    """Show a desktop notification if the platform supports one. Never raises.

    ``source``/``target`` add a routing line ("From: … → For: …") so that, in
    multi-agent or multi-terminal workflows, you can see where the clipboard
    content came from and where it is meant to go.

    ``urgent`` (Windows 11 only) marks the toast as an "important
    notification" that can break through Do Not Disturb / Focus Assist after
    a one-time "Allow" confirmation by the user.
    """
    try:
        if sys.platform == "darwin":
            subprocess.run(
                ["osascript", "-e",
                 f'display notification {_q(_with_route(message, source, target))} '
                 f'with title {_q(title)}'],
                check=False,
            )
        elif sys.platform.startswith("win"):
            _win_toast(title, message, source, target, urgent)
        elif shutil.which("notify-send"):
            subprocess.run(
                ["notify-send", title, _with_route(message, source, target)],
                check=False,
            )
    except Exception:
        pass  # toast is best-effort by design


def _q(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def _with_route(message: str, source: str | None, target: str | None) -> str:
    parts = []
    if source:
        parts.append(f"From: {source}")
    if target:
        parts.append(f"For: {target}")
    return message + ("\n" + " → ".join(parts) if parts else "")


def _win_toast(
    title: str,
    message: str,
    source: str | None,
    target: str | None,
    urgent: bool,
) -> None:
    script = os.path.join(os.path.dirname(__file__), "toast.ps1")
    if not os.path.exists(script):
        return
    cmd = [
        "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", script, "-Title", title, "-Message", message,
    ]
    if source:
        cmd += ["-Source", source]
    if target:
        cmd += ["-Target", target]
    if urgent:
        cmd.append("-Urgent")
    subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
