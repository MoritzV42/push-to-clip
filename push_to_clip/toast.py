"""Best-effort desktop toast notification.

The toast is a nicety, never a requirement: every failure is swallowed so a
missing notifier can never break the actual clipboard copy.
"""

from __future__ import annotations

import shutil
import subprocess
import sys


def notify(title: str, message: str) -> None:
    """Show a desktop notification if the platform supports one. Never raises."""
    try:
        if sys.platform == "darwin":
            subprocess.run(
                ["osascript", "-e",
                 f'display notification {_q(message)} with title {_q(title)}'],
                check=False,
            )
        elif sys.platform.startswith("win"):
            _win_toast(title, message)
        elif shutil.which("notify-send"):
            subprocess.run(["notify-send", title, message], check=False)
    except Exception:
        pass  # toast is best-effort by design


def _q(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def _win_toast(title: str, message: str) -> None:
    # Lightweight WinRT toast via PowerShell; silently no-ops if unavailable.
    script = (
        "$ErrorActionPreference='SilentlyContinue';"
        "[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]>$null;"
        "$t=[Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
        "[Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
        f"$x=$t.GetElementsByTagName('text');$x[0].AppendChild($t.CreateTextNode('{title}'))>$null;"
        f"$x[1].AppendChild($t.CreateTextNode('{message}'))>$null;"
        "$n=[Windows.UI.Notifications.ToastNotification]::new($t);"
        "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('push-to-clip').Show($n);"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", script],
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
