"""FastAPI + WebSocket server for Window Commander."""

import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from window_manager import discover_windows, move_window, focus_window, inject_text, minimize_window
from layouts import apply_layout, get_available_layouts
from transcriber import transcribe_audio
import overlay


# Connected WebSocket clients
connected_clients: set[WebSocket] = set()

# Track which window is the "active target" for voice
active_target_hwnd: int | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background tasks on startup."""
    overlay.start()
    print("  Overlay started — terminals will glow when selected")
    task = asyncio.create_task(broadcast_window_state())
    yield
    task.cancel()
    overlay.stop()


app = FastAPI(title="Window Commander", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def broadcast_window_state():
    """Periodically broadcast window state to all connected clients."""
    while True:
        if connected_clients:
            windows = discover_windows()
            message = json.dumps({
                "type": "window_state",
                "windows": [w.to_dict() for w in windows],
                "active_target": active_target_hwnd,
            })
            disconnected = set()
            for client in connected_clients:
                try:
                    await client.send_text(message)
                except Exception:
                    disconnected.add(client)
            connected_clients -= disconnected
        await asyncio.sleep(1)


def _set_active_target(hwnd: int | None, process_name: str = ""):
    """Set the active target window and update overlay."""
    global active_target_hwnd
    active_target_hwnd = hwnd

    if hwnd and overlay.is_terminal(process_name):
        overlay.set_target(hwnd, "green")
    elif hwnd:
        # Non-terminal windows get a subtle blue highlight
        overlay.set_target(hwnd, "blue")
    else:
        overlay.set_target(None, "off")


# --- REST endpoints ---

@app.get("/health")
def health():
    return {"status": "ok", "service": "window-commander"}


@app.get("/windows")
def list_windows():
    """List all discovered windows."""
    windows = discover_windows()
    return {"windows": [w.to_dict() for w in windows]}


@app.get("/layouts")
def list_layouts():
    """List available layout presets."""
    return {"layouts": get_available_layouts()}


@app.post("/layout/apply")
def apply_layout_endpoint(body: dict):
    """Apply a layout to specified windows.

    Body: { "layout": "2x2", "hwnds": [123, 456, 789, ...] }
    """
    layout_name = body.get("layout")
    hwnds = body.get("hwnds", [])

    if not layout_name:
        return {"error": "layout is required"}
    if not hwnds:
        return {"error": "hwnds list is required"}

    result = apply_layout(layout_name, hwnds)
    return {"result": result}


@app.post("/window/move")
def move_window_endpoint(body: dict):
    """Move/resize a single window.

    Body: { "hwnd": 123, "x": 0, "y": 0, "width": 960, "height": 540 }
    """
    hwnd = body.get("hwnd")
    if not hwnd:
        return {"error": "hwnd is required"}

    success = move_window(
        hwnd,
        body.get("x", 0),
        body.get("y", 0),
        body.get("width", 800),
        body.get("height", 600),
    )
    return {"success": success}


@app.post("/window/focus")
def focus_window_endpoint(body: dict):
    """Focus a window. Body: { "hwnd": 123 }"""
    hwnd = body.get("hwnd")
    if not hwnd:
        return {"error": "hwnd is required"}
    success = focus_window(hwnd)
    return {"success": success}


@app.post("/window/minimize")
def minimize_window_endpoint(body: dict):
    """Minimize a window. Body: { "hwnd": 123 }"""
    hwnd = body.get("hwnd")
    if not hwnd:
        return {"error": "hwnd is required"}
    success = minimize_window(hwnd)
    return {"success": success}


@app.post("/text/inject")
def inject_text_endpoint(body: dict):
    """Inject text into a window (clipboard paste).

    Body: { "hwnd": 123, "text": "hello world" }
    """
    hwnd = body.get("hwnd")
    text = body.get("text", "")
    if not hwnd:
        return {"error": "hwnd is required"}
    if not text:
        return {"error": "text is required"}
    success = inject_text(hwnd, text)
    return {"success": success}


@app.post("/voice/transcribe")
def transcribe_endpoint(body: dict):
    """Transcribe audio and optionally inject into active window.

    Body: { "audio": "<base64>", "format": "wav", "inject": true }
    """
    audio = body.get("audio", "")
    fmt = body.get("format", "wav")
    should_inject = body.get("inject", True)

    if not audio:
        return {"error": "audio is required"}

    result = transcribe_audio(audio, fmt)

    if result["success"] and should_inject and active_target_hwnd:
        inject_text(active_target_hwnd, result["text"])
        result["injected_to"] = active_target_hwnd

    return result


# --- WebSocket ---

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket for real-time window state + commands from phone."""
    await ws.accept()
    connected_clients.add(ws)
    print(f"Client connected. Total: {len(connected_clients)}")

    # Send initial state
    windows = discover_windows()
    await ws.send_text(json.dumps({
        "type": "window_state",
        "windows": [w.to_dict() for w in windows],
        "active_target": active_target_hwnd,
    }))

    # Send available layouts
    await ws.send_text(json.dumps({
        "type": "layouts",
        "layouts": get_available_layouts(),
    }))

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            response = handle_ws_message(msg)
            await ws.send_text(json.dumps(response))
    except WebSocketDisconnect:
        connected_clients.discard(ws)
        print(f"Client disconnected. Total: {len(connected_clients)}")


def handle_ws_message(msg: dict) -> dict:
    """Handle incoming WebSocket commands from the phone app."""
    action = msg.get("action")

    if action == "get_windows":
        windows = discover_windows()
        return {
            "type": "window_state",
            "windows": [w.to_dict() for w in windows],
            "active_target": active_target_hwnd,
        }

    elif action == "apply_layout":
        layout = msg.get("layout")
        hwnds = msg.get("hwnds", [])
        if layout and hwnds:
            result = apply_layout(layout, hwnds)
            return {"type": "layout_applied", "result": result}
        return {"type": "error", "message": "layout and hwnds required"}

    elif action == "move_window":
        success = move_window(
            msg["hwnd"], msg["x"], msg["y"], msg["width"], msg["height"]
        )
        return {"type": "window_moved", "success": success}

    elif action == "focus_window":
        hwnd = msg["hwnd"]
        process_name = msg.get("process_name", "")
        success = focus_window(hwnd)
        if success:
            _set_active_target(hwnd, process_name)
        return {
            "type": "window_focused",
            "success": success,
            "is_terminal": overlay.is_terminal(process_name),
        }

    elif action == "select_target":
        # Select a window as voice target without focusing it
        hwnd = msg["hwnd"]
        process_name = msg.get("process_name", "")
        _set_active_target(hwnd, process_name)
        return {
            "type": "target_selected",
            "hwnd": hwnd,
            "is_terminal": overlay.is_terminal(process_name),
        }

    elif action == "clear_target":
        _set_active_target(None)
        return {"type": "target_cleared"}

    elif action == "voice_start":
        # Phone started listening — turn overlay to red (listening)
        overlay.set_color("listening")
        return {"type": "voice_status", "status": "listening"}

    elif action == "voice_stop":
        # Phone stopped listening — back to green
        overlay.set_color("green")
        return {"type": "voice_status", "status": "ready"}

    elif action == "voice_transcribe":
        # Receive audio from phone, transcribe with Whisper, inject into terminal
        audio = msg.get("audio", "")
        fmt = msg.get("format", "m4a")
        overlay.set_color("blue")  # Processing

        result = transcribe_audio(audio, fmt)

        if result["success"] and active_target_hwnd:
            inject_text(active_target_hwnd, result["text"], press_enter=True)
            result["injected_to"] = active_target_hwnd

        overlay.set_color("green")  # Back to ready
        return {"type": "voice_result", **result}

    elif action == "inject_text":
        hwnd = msg.get("hwnd", active_target_hwnd)
        if hwnd:
            success = inject_text(hwnd, msg["text"])
            return {"type": "text_injected", "success": success}
        return {"type": "error", "message": "No target window"}

    elif action == "get_layouts":
        return {"type": "layouts", "layouts": get_available_layouts()}

    else:
        return {"type": "error", "message": f"Unknown action: {action}"}
