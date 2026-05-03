# Window Commander — Agent Guide

Phone-controlled window manager + voice PTT for AI agent terminals. Speak into phone OR keyboard, text pastes into Claude Code / Cursor / Codex / VS Code with auto-Enter.

## Repo layout

```
window-commander/
├── desktop/        Python desktop agent (FastAPI + Win32 + Whisper)
├── mobile/         Expo React Native PWA-ready app
├── website/        Next.js 16 marketing site (cyan-on-black, glaido-derived)
├── PWA_SPEC.md     Plan for migrating mobile/ from Expo to PWA
└── run commands.md Per-folder dev startup commands
```

## Three independent runnables

| Folder | Command | Purpose |
|---|---|---|
| `desktop/` | `python main.py` | WebSocket server for phone client |
| `desktop/` | `python keyboard_client.py` | Standalone keyboard PTT (no phone) |
| `mobile/` | `npx expo start` | Phone client (scan QR with Expo Go) |
| `website/` | `npm run dev` | Marketing site (localhost:3000) |

`main.py` and `keyboard_client.py` can run together or separately. They share `transcriber.py`, `window_manager.py`, `overlay.py`.

## Key files

### Desktop (`desktop/`)
- `server.py` — FastAPI WebSocket, phone protocol. `inject_text(...press_enter=True)` at line 300.
- `window_manager.py` — Win32 window discovery + injection. `inject_text(hwnd, text, press_enter)` at line 176.
- `overlay.py` — Layered window tint (green = locked, red = recording, blue = transcribing).
- `transcriber.py` — OpenAI Whisper API primary, Google STT + Sphinx fallback. Reads `OPENAI_API_KEY` from `.env`.
- `keyboard_client.py` — pynput hotkeys + sounddevice mic + pystray tray. Standalone. Reuses transcriber/overlay/window_manager.
- `keybindings.json` — PTT key, cycle combos, target process allowlist. Editable, no rebuild.
- `config.py` — HOST/PORT, taskbar/window dimensions.

### Mobile (`mobile/`)
- `App.tsx` — Expo entry.
- `src/` — components, WebSocket client, PTT button.
- Uses `expo-av` MediaRecorder for m4a → base64 → WS to `desktop/server.py`.

### Website (`website/`)
- Next.js 16.2.4, React 19, Tailwind v4, App Router, Turbopack.
- `app/globals.css` — design tokens. Cyan `#22d3ee` on `#0d0d0d`. Hover `#67e8f9`. Glow rgba `34, 211, 238`.
- `components/` — Nav, Hero, Features, HowItWorks, Download, Waitlist, Footer.
- `app/api/waitlist/route.ts` — POST email handler (currently logs only, not wired to Resend yet).
- See `website/AGENTS.md` — Next.js 16 has breaking changes from training data, read `node_modules/next/dist/docs/` before edits.

## Voice flow (both clients)

```
[hold PTT] → record 16kHz mono → release
          → base64 WAV → transcribe_audio() → Whisper API
          → inject_text(target_hwnd, text, press_enter=True)
          → SetForegroundWindow + clipboard SetText + Ctrl+V + Enter
```

Phone client: PTT button in mobile app, audio over WS.
Keyboard client: hold `Right Ctrl` (default), audio captured via `sounddevice`.

## Auto-Enter

`window_manager.inject_text(..., press_enter=True)` sends VK_RETURN (lines 205-209) after Ctrl+V. Toggle in `keybindings.json` via `press_enter_after_paste`.

## Target window cycling

`keyboard_client.py` filters discovered windows against `target_processes` allowlist in `keybindings.json`. Defaults: cursor.exe, claude.exe, code.exe, windsurf.exe, codex.exe, terminals. `Ctrl+Alt+→/←` cycles. `Ctrl+Alt+Space` locks (freezes target).

## Conventions

- Win32 API via `pywin32`. Don't use `ctypes.windll` directly unless `pywin32` lacks the call.
- Reuse `transcriber.transcribe_audio(audio_b64, format)` — don't re-implement Whisper calls.
- Reuse `overlay.set_target(hwnd, color)` / `overlay.set_color(color)` — don't spawn second overlay window.
- Brand color cyan `#22d3ee`. Don't introduce new accent colors without coordinating across website + overlay.
- Sentence case headlines on website. Mono uppercase for eyebrows/badges. Lime/green is gone — replaced with cyan.

## Environment

- `OPENAI_API_KEY` in `desktop/.env` — required for Whisper. Falls back to Google STT/Sphinx if missing.
- Python 3.11+ (uses `int | None` union syntax).
- Windows-only desktop (uses `pywin32`, layered windows). Mac support not yet planned.
- Phone and desktop must be on same LAN.

## Distribution status

- Desktop: not yet packaged. PyInstaller next.
- Mobile: Expo Go works for testing. PWA migration spec in `PWA_SPEC.md`.
- Website: not yet deployed. Vercel target.

## Roadmap pointers

See `PWA_SPEC.md` for mobile-without-Expo plan. Memory entry: `project_window_commander.md`.
