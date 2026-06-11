# Changelog

## 0.2.0 — 2026-06-11

### Windows toast rebuilt: actually visible now

- **New `toast.ps1` package resource** replaces the previous inline PowerShell
  one-liner. The old toast used an unregistered AppUserModelId — Windows
  accepted the notification but never rendered a banner.
- **Zero-setup self-registration:** `toast.ps1` registers its AppUserModelId
  (`MoritzV42.PushToClip`) under HKCU on every run — idempotent, no admin
  rights, nothing to configure after install.
- **New `--urgent` / `-u` flag:** marks the toast as a Windows 11 *important
  notification* (`scenario="urgent"`) so it breaks through Do Not Disturb /
  Focus Assist. Windows asks once ("Allow important notifications?"); after
  that, urgent toasts stay visible even while Do Not Disturb is on.
- **Routing line support:** `toast.ps1` (and `push_to_clip.toast.notify()`)
  accept optional `Source`/`Target` values rendered as a third line
  ("From: … → For: …") — useful in multi-agent / multi-terminal workflows.
- **Injection-safe invocation:** title/message are passed as real arguments to
  `powershell.exe -File` instead of being interpolated into a command string.
- Toast expires from the Notification Center after 5 minutes.
- README: toast screenshot, troubleshooting section (Do Not Disturb,
  PowerShell 7 WinRT pitfall, UTF-8 BOM).

## 0.1.0 — 2026-06-07

- Initial release: cross-platform clipboard CLI (`push-to-clip` / `ptc`),
  zero dependencies — Win32 via ctypes, `pbcopy` on macOS,
  `wl-copy`/`xclip`/`xsel` on Linux. `--file`, stdin piping, `--json`,
  `--quiet`, basic desktop toast.
