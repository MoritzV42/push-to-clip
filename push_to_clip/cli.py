"""Command-line entry point for push-to-clip."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .clipboard import ClipboardError, set_clipboard
from .toast import notify


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="push-to-clip",
        description="Copy text, a file, or piped input to your system clipboard - "
                    "cross-platform, zero dependencies.",
        epilog="Examples:\n"
               "  push-to-clip \"hello world\"\n"
               "  echo $RESULT | push-to-clip\n"
               "  push-to-clip --file notes.md\n"
               "  some-command | ptc --quiet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("text", nargs="*", help="Text to copy. If omitted, reads stdin.")
    parser.add_argument("-f", "--file", help="Copy the contents of this file.")
    parser.add_argument("-n", "--no-toast", action="store_true",
                        help="Do not show a desktop toast.")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Suppress the stdout confirmation.")
    parser.add_argument("--json", action="store_true",
                        help="Print a machine-readable JSON result.")
    parser.add_argument("-V", "--version", action="version",
                        version=f"push-to-clip {__version__}")
    return parser


def _resolve_input(args: argparse.Namespace, parser: argparse.ArgumentParser):
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as handle:
                return handle.read(), f"file:{args.file}"
        except OSError as exc:
            parser.error(f"cannot read {args.file}: {exc.strerror}")
    if args.text:
        return " ".join(args.text), "args"
    if not sys.stdin.isatty():
        return sys.stdin.read(), "stdin"
    parser.error("no input — pass text, use --file, or pipe via stdin")


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    content, source = _resolve_input(args, parser)

    try:
        set_clipboard(content)
    except ClipboardError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}))
        else:
            print(f"push-to-clip: {exc}", file=sys.stderr)
        return 1

    chars = len(content)
    if not args.no_toast:
        notify("push-to-clip", f"Copied {chars} characters to your clipboard")
    if args.json:
        print(json.dumps({"ok": True, "chars": chars, "source": source}))
    elif not args.quiet:
        # Plain ASCII so the status line can never crash on legacy consoles
        # (e.g. Windows cp1252) — the clipboard write itself is full Unicode.
        print(f"copied {chars} characters to your clipboard")
    return 0


if __name__ == "__main__":
    sys.exit(main())
