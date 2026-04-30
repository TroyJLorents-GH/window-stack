"""Standalone desktop PTT client. No phone needed.

Hold PTT key (default Right Ctrl) → record mic → release → Whisper → paste into
target window + Enter. Cycle target with Ctrl+Alt+Left/Right. Lock with
Ctrl+Alt+Space.

Usage:
    python keyboard_client.py
"""

import base64
import io
import json
import os
import sys
import threading
import time
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from pynput import keyboard
from PIL import Image, ImageDraw
import pystray

import overlay
from transcriber import transcribe_audio
from window_manager import discover_windows, inject_text


load_dotenv()

CONFIG_PATH = Path(__file__).parent / "keybindings.json"
SAMPLE_RATE = 16000
CHANNELS = 1


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class PTTClient:
    def __init__(self):
        self.config = load_config()
        self.recording = False
        self.frames: list[np.ndarray] = []
        self.stream: sd.InputStream | None = None
        self.record_started_at: float = 0

        self.targets: list = []
        self.target_index = 0
        self.target_locked = False
        self.paused = False

        self.refresh_targets()
        if self.targets:
            self._set_target(self.targets[0].hwnd)

        overlay.start()

    def refresh_targets(self):
        allowed = {p.lower() for p in self.config.get("target_processes", [])}
        all_windows = discover_windows()
        self.targets = [
            w for w in all_windows
            if w.process_name and w.process_name.lower() in allowed
            and not w.is_minimized
        ]
        if not self.targets:
            self.targets = all_windows[:10]

    def _set_target(self, hwnd: int):
        overlay.set_target(hwnd, "green")

    def cycle(self, direction: int):
        if self.target_locked:
            return
        self.refresh_targets()
        if not self.targets:
            return
        self.target_index = (self.target_index + direction) % len(self.targets)
        target = self.targets[self.target_index]
        self._set_target(target.hwnd)
        print(f"[target] {target.process_name} — {target.title[:60]}")

    def toggle_lock(self):
        self.target_locked = not self.target_locked
        print(f"[lock] {'locked' if self.target_locked else 'unlocked'}")

    def current_target_hwnd(self) -> int | None:
        if not self.targets:
            return None
        return self.targets[self.target_index].hwnd

    def start_recording(self):
        if self.recording or self.paused:
            return
        self.recording = True
        self.frames = []
        self.record_started_at = time.time()

        def cb(indata, _frames, _time_info, _status):
            self.frames.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            callback=cb,
        )
        self.stream.start()
        overlay.set_color("listening")
        print("[rec] start")

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        elapsed_ms = (time.time() - self.record_started_at) * 1000

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        min_ms = self.config.get("min_record_ms", 250)
        if elapsed_ms < min_ms:
            print(f"[rec] too short ({elapsed_ms:.0f}ms < {min_ms}ms)")
            overlay.set_color("green")
            return

        threading.Thread(target=self._process_audio, daemon=True).start()

    def _process_audio(self):
        try:
            overlay.set_color("blue")
            audio = np.concatenate(self.frames, axis=0) if self.frames else None
            if audio is None or len(audio) == 0:
                overlay.set_color("green")
                return

            buf = io.BytesIO()
            with wave.open(buf, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio.tobytes())
            audio_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

            print("[rec] transcribing...")
            result = transcribe_audio(audio_b64, format="wav")

            if not result.get("success"):
                print(f"[rec] failed: {result.get('error')}")
                overlay.set_color("green")
                return

            text = result["text"].strip()
            if not text:
                overlay.set_color("green")
                return

            print(f"[rec] → {text}")

            hwnd = self.current_target_hwnd()
            if hwnd:
                press_enter = self.config.get("press_enter_after_paste", True)
                inject_text(hwnd, text, press_enter=press_enter)
            else:
                print("[rec] no target window")

            overlay.set_color("green")
        except Exception as e:
            print(f"[rec] error: {e}")
            overlay.set_color("green")


def parse_ptt_key(s: str):
    s = s.strip().lower()
    mapping = {
        "ctrl_r": keyboard.Key.ctrl_r,
        "ctrl_l": keyboard.Key.ctrl_l,
        "alt_r": keyboard.Key.alt_r,
        "alt_l": keyboard.Key.alt_l,
        "shift_r": keyboard.Key.shift_r,
        "shift_l": keyboard.Key.shift_l,
        "caps_lock": keyboard.Key.caps_lock,
        "scroll_lock": keyboard.Key.scroll_lock,
        "f13": keyboard.Key.f13,
        "f14": keyboard.Key.f14,
        "f15": keyboard.Key.f15,
        "f16": keyboard.Key.f16,
        "pause": keyboard.Key.pause,
    }
    return mapping.get(s, keyboard.Key.ctrl_r)


def make_tray_icon(client: PTTClient, stop_event: threading.Event):
    img = Image.new("RGB", (64, 64), (13, 13, 13))
    d = ImageDraw.Draw(img)
    d.ellipse((16, 16, 48, 48), fill=(34, 211, 238))

    def on_quit(_icon, _item):
        stop_event.set()
        _icon.stop()

    def on_pause(icon, _item):
        client.paused = not client.paused
        icon.title = f"Window Commander {'(paused)' if client.paused else ''}"

    def on_refresh(_icon, _item):
        client.refresh_targets()
        if client.targets:
            client._set_target(client.targets[0].hwnd)
            client.target_index = 0

    menu = pystray.Menu(
        pystray.MenuItem("Window Commander PTT", lambda _i, _it: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Pause / Resume", on_pause),
        pystray.MenuItem("Refresh targets", on_refresh),
        pystray.MenuItem("Quit", on_quit),
    )
    return pystray.Icon("window-commander", img, "Window Commander", menu)


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not set. Whisper will fall back to offline.")

    client = PTTClient()
    cfg = client.config
    ptt_key = parse_ptt_key(cfg.get("ptt", "ctrl_r"))

    print(f"[init] PTT={cfg.get('ptt')} cycle_next={cfg.get('cycle_next')} "
          f"cycle_prev={cfg.get('cycle_prev')} lock={cfg.get('lock_target')}")
    print(f"[init] {len(client.targets)} target windows discovered")

    cycle_next = keyboard.HotKey(
        keyboard.HotKey.parse(cfg.get("cycle_next", "<ctrl>+<alt>+<right>")),
        lambda: client.cycle(1),
    )
    cycle_prev = keyboard.HotKey(
        keyboard.HotKey.parse(cfg.get("cycle_prev", "<ctrl>+<alt>+<left>")),
        lambda: client.cycle(-1),
    )
    lock_target = keyboard.HotKey(
        keyboard.HotKey.parse(cfg.get("lock_target", "<ctrl>+<alt>+<space>")),
        client.toggle_lock,
    )

    def on_press(key):
        try:
            cycle_next.press(listener.canonical(key))
            cycle_prev.press(listener.canonical(key))
            lock_target.press(listener.canonical(key))
        except Exception:
            pass
        if key == ptt_key and not client.recording:
            client.start_recording()

    def on_release(key):
        try:
            cycle_next.release(listener.canonical(key))
            cycle_prev.release(listener.canonical(key))
            lock_target.release(listener.canonical(key))
        except Exception:
            pass
        if key == ptt_key and client.recording:
            client.stop_recording()

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    stop_event = threading.Event()
    icon = make_tray_icon(client, stop_event)

    print("[init] ready. Hold PTT key to talk.")
    try:
        icon.run()
    finally:
        listener.stop()
        overlay.stop()


if __name__ == "__main__":
    main()
