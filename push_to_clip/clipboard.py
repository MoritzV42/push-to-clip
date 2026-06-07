"""Cross-platform clipboard writer — no third-party dependencies.

Windows uses the Win32 clipboard API via ctypes (Unicode-safe). macOS shells
out to ``pbcopy``. Linux tries ``wl-copy`` (Wayland), then ``xclip``, then
``xsel`` (X11). Every backend raises :class:`ClipboardError` on failure so the
CLI can report a clean, actionable message.
"""

from __future__ import annotations

import shutil
import subprocess
import sys


class ClipboardError(RuntimeError):
    """Raised when the clipboard could not be written on this platform."""


def set_clipboard(text: str) -> None:
    """Write ``text`` to the system clipboard. Raises ClipboardError on failure."""
    if sys.platform.startswith("win"):
        _set_windows(text)
    elif sys.platform == "darwin":
        _pipe_to(["pbcopy"], text)
    else:
        _set_linux(text)


def _pipe_to(cmd: list[str], text: str) -> None:
    try:
        subprocess.run(cmd, input=text.encode("utf-8"), check=True)
    except FileNotFoundError as exc:
        raise ClipboardError(f"`{cmd[0]}` not found") from exc
    except subprocess.CalledProcessError as exc:
        raise ClipboardError(f"`{cmd[0]}` failed (exit {exc.returncode})") from exc


def _set_linux(text: str) -> None:
    backends = (
        ["wl-copy"],
        ["xclip", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--input"],
    )
    for cmd in backends:
        if shutil.which(cmd[0]):
            _pipe_to(cmd, text)
            return
    raise ClipboardError(
        "no clipboard tool found — install one of: wl-clipboard (Wayland), "
        "xclip, or xsel (X11)"
    )


def _set_windows(text: str) -> None:
    import ctypes
    from ctypes import wintypes

    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.SetClipboardData.restype = wintypes.HANDLE
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]

    # UTF-16-LE, double-null terminated.
    data = text.encode("utf-16-le") + b"\x00\x00"

    if not user32.OpenClipboard(None):
        raise ClipboardError("could not open the Windows clipboard")
    try:
        user32.EmptyClipboard()
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not handle:
            raise ClipboardError("GlobalAlloc failed")
        locked = kernel32.GlobalLock(handle)
        if not locked:
            raise ClipboardError("GlobalLock failed")
        try:
            ctypes.memmove(locked, data, len(data))
        finally:
            kernel32.GlobalUnlock(handle)
        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            raise ClipboardError("SetClipboardData failed")
    finally:
        user32.CloseClipboard()
