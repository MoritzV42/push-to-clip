# Install push-to-clip (AI agent prompt)

> Paste this whole file to your AI coding agent (Claude Code, Cursor, Copilot Chat, …).
> It will install `push-to-clip` tailored to your machine and verify it works.

---

**Task: install the `push-to-clip` CLI for me and confirm it works.**

`push-to-clip` copies text, files, or piped input to the system clipboard. It is a pure
Python (stdlib-only) tool, installable from PyPI. Please:

1. **Detect my OS and Python.** Confirm Python ≥ 3.8 is available (`python --version` or
   `python3 --version`). If missing, tell me how to install it for my OS and stop.

2. **Install it in an isolated environment** (preferred):
   ```bash
   pipx install push-to-clip
   ```
   If `pipx` isn't installed, either install pipx first (`python -m pip install --user pipx && python -m pipx ensurepath`) or fall back to:
   ```bash
   python -m pip install --user push-to-clip
   ```

3. **Linux only — ensure a clipboard backend exists.** Check for `wl-copy` (Wayland),
   `xclip`, or `xsel`. If none is present, tell me the install command for my distro
   (e.g. `sudo apt install wl-clipboard` or `xclip`) and ask me to run it. On Windows and
   macOS nothing extra is needed.

4. **Verify.** Run a round-trip test and show me the result:
   ```bash
   echo "push-to-clip works ✅" | push-to-clip --json
   ```
   Expect `{"ok": true, "chars": ..., "source": "stdin"}`. Then tell me to press
   paste (Ctrl/Cmd-V) somewhere to confirm the text is on my clipboard.

5. **Show me the basics** once it works:
   - `push-to-clip "text"` — copy a string
   - `cmd | push-to-clip` — copy piped output
   - `push-to-clip --file path` — copy a file
   - short alias: `ptc`

If anything fails, show the exact error and the smallest fix for my platform. Do not
change my shell config beyond what `pipx ensurepath` does, and ask before installing
system packages.
