# push-to-clip

**Copy text, files, or piped output to your system clipboard — from one command, on any OS.**

`push-to-clip` is a tiny, dependency-free CLI that writes whatever you give it to the
system clipboard. Pipe a command's output, pass a string, or point it at a file — it
lands on your clipboard on **Windows, macOS, and Linux**, with an optional desktop toast.

It's the natural companion to [secret-paste](https://github.com/MoritzV42/secret-paste):
where *secret-paste* gets values **into** your AI coding agent without leaking them to the
transcript, `push-to-clip` gets results **out** — so your agent (or any script) can put a
ready-to-paste prompt, snippet, or token straight onto your clipboard.

```bash
push-to-clip "hello world"           # copy a string
echo "$RESULT" | push-to-clip        # copy piped output
push-to-clip --file notes.md         # copy a file's contents
some-command | ptc --quiet           # short alias, no chatter
```

## Why

- **Cross-platform, one command.** No more remembering `clip` vs `pbcopy` vs `xclip` vs `wl-copy`.
- **Zero dependencies.** Pure Python standard library — Win32 clipboard via `ctypes`,
  native helpers on macOS/Linux. Clone and run.
- **Agent-friendly.** Deterministic exit codes and `--json` output make it trivial for an
  AI coding agent or CI step to copy something to *your* clipboard and confirm it.
- **Unicode-safe.** Emoji, umlauts, CJK — all preserved.

## Install

### Option A — let your AI coding agent do it (recommended)
Open [`SETUP.md`](./SETUP.md) and paste it to your agent (Claude Code, Cursor, …). It
detects your OS, installs `push-to-clip`, wires up a clipboard backend on Linux if needed,
and verifies it works — tailored to your machine.

### Option B — manual
```bash
pipx install push-to-clip      # isolated, recommended
# or
pip install push-to-clip
```
On **Linux**, install one clipboard backend once: `wl-clipboard` (Wayland), `xclip`, or `xsel`.

## Usage

| Command | What it does |
|---|---|
| `push-to-clip "text"` | Copy a literal string |
| `cmd \| push-to-clip` | Copy piped stdin |
| `push-to-clip -f FILE` | Copy a file's contents |
| `… \| ptc -q` | Short alias, no stdout confirmation |
| `… \| push-to-clip --json` | `{"ok": true, "chars": N, "source": "stdin"}` |
| `push-to-clip -n …` | Skip the desktop toast |

Exit code is `0` on success, `1` if the clipboard could not be written (with a clear reason).

## How it works

- **Windows** — Win32 `OpenClipboard`/`SetClipboardData` (`CF_UNICODETEXT`) via `ctypes`.
- **macOS** — pipes to `pbcopy`.
- **Linux** — tries `wl-copy`, then `xclip`, then `xsel`.

No network, no telemetry, nothing leaves your machine.

<!-- PORTFOLIO-LINKS:START -->
## More open-source tools by Moritz Voigt

- **[secret-paste](https://github.com/MoritzV42/secret-paste)** — Paste API keys & tokens to your AI coding agent without ever putting them in the chat transcript. Local-only, cross-platform.
- **[push-to-clip](https://github.com/MoritzV42/push-to-clip)** — Copy text, files, or piped output to your system clipboard, from one command, on any OS. *(this repo)*
- **[memoryball-studio](https://github.com/MoritzV42/memoryball-studio)** — Batch-prep a whole photo folder for the Memory Orb display ball: auto-cropped, face-aware, the right format — locally.
- **[ingpad](https://github.com/MoritzV42/ingpad)** — The engineer's scratch pad: solve technical exercises on one canvas with per-step Given / Sought / Approach, stylus fields, and an AI tutor.

All MIT-licensed, free, built in public → **[moritzvoigt.infinityspace42.de](https://moritzvoigt.infinityspace42.de)**
<!-- PORTFOLIO-LINKS:END -->

## License

MIT © Moritz Voigt
