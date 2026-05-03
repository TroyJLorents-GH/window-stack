# Window Commander

Voice-controlled window manager for AI agent terminals. Hold a key (or phone button), speak, release. Text pastes into Cursor / Claude Code / Codex / VS Code with auto-Enter.

Hands-free coding from anywhere in the house.

## What's in the box

- **Desktop agent** (Python, Windows) — receives voice, manages windows, injects text
- **Phone client** (Expo / React Native) — PTT button, drag-and-drop window layouts
- **Keyboard client** (Python, Windows) — same PTT, no phone needed, system tray app
- **Marketing site** (Next.js) — landing page + waitlist

## Quick start

### Option A — keyboard PTT (no phone)

```bash
cd desktop
pip install -r requirements.txt
# put OPENAI_API_KEY in desktop/.env
python keyboard_client.py
```

Hold `Right Ctrl`, speak, release. Text appears in your AI terminal.

Cycle target window: `Ctrl+Alt+→` / `Ctrl+Alt+←`.
Lock target: `Ctrl+Alt+Space`.
Edit `keybindings.json` to remap.

### Option B — phone PTT

```bash
# terminal 1
cd desktop
python main.py

# terminal 2
cd mobile
npx expo start
```

Scan QR with Expo Go on your phone. Same WiFi as desktop.

### Option C — both

Run `main.py` and `keyboard_client.py` together. Phone and keyboard share targets via LAN.

## Requirements

- Windows 10/11 (desktop agent uses Win32 layered windows)
- Python 3.11+
- Node 20+ (for mobile or website)
- OpenAI API key for Whisper (~$0.006/min). Falls back to free Google STT if missing.

## How voice works

`hold key → record 16kHz mono → release → Whisper transcribe → clipboard paste + Enter into focused window`

Target window glows cyan when locked, red when listening, blue when transcribing.

## Folders

```
desktop/   Python agent, server, keyboard client, overlay, transcriber
mobile/    Expo app for phone PTT + window layouts
website/   Next.js marketing site (cyan-on-black)
```

## Status

v0.1 — keyboard PTT works, phone PTT works, website built. Not yet packaged for distribution. Whisper API required (no local model yet).

## License

MIT.
