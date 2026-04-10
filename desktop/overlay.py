"""Full-window colored overlay that tints the active terminal window.

Colors:
  - GREEN: Terminal is selected and ready for voice input
  - RED: Actively listening / recording speech
  - BLUE: Processing transcription
  - OFF: No terminal selected
"""

import ctypes
import ctypes.wintypes as wintypes
import threading
import time

import win32con
import win32gui

# Overlay state
_overlay_hwnd = None
_overlay_thread = None
_running = False
_target_hwnd = None
_color = "green"  # "green", "blue", "listening", or "off"

# Opacity per color (0-255). Lower = more subtle tint.
OPACITY = {
    "green": 45,
    "blue": 50,
    "listening": 55,
}

# RGB colors (for SetLayeredWindowAttributes alpha blend)
COLORS_RGB = {
    "green": (0, 255, 136),
    "blue": (59, 130, 246),
    "listening": (239, 68, 68),
}

# Terminal process names to highlight
TERMINAL_PROCESSES = {
    "windowsterminal.exe",
    "cmd.exe",
    "powershell.exe",
    "pwsh.exe",
    "conhost.exe",
    "alacritty.exe",
    "wezterm-gui.exe",
    "mintty.exe",
    "claude.exe",
}


def is_terminal(process_name: str) -> bool:
    """Check if a process is a terminal/command-line app."""
    return process_name.lower() in TERMINAL_PROCESSES


def set_target(hwnd: int | None, color: str = "green"):
    """Set which window to highlight and what color."""
    global _target_hwnd, _color
    _target_hwnd = hwnd
    _color = color


def set_color(color: str):
    """Change the overlay color (green/blue/listening/off)."""
    global _color
    _color = color


def _get_window_rect(hwnd: int) -> tuple[int, int, int, int] | None:
    """Get window rect, returns None if window is gone."""
    try:
        if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
            return None
        rect = win32gui.GetWindowRect(hwnd)
        return rect
    except Exception:
        return None


def _create_overlay_window():
    """Create a transparent, click-through overlay window."""
    wc = win32gui.WNDCLASS()
    wc.lpfnWndProc = {
        win32con.WM_DESTROY: lambda hwnd, msg, wp, lp: win32gui.PostQuitMessage(0),
        win32con.WM_PAINT: _on_paint,
    }
    wc.lpszClassName = "WindowCommanderOverlay"
    wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
    wc.hbrBackground = 0

    try:
        win32gui.RegisterClass(wc)
    except Exception:
        pass

    style = win32con.WS_POPUP
    ex_style = (
        win32con.WS_EX_LAYERED
        | win32con.WS_EX_TRANSPARENT
        | win32con.WS_EX_TOPMOST
        | win32con.WS_EX_TOOLWINDOW
    )

    hwnd = win32gui.CreateWindowEx(
        ex_style,
        "WindowCommanderOverlay",
        "WC Overlay",
        style,
        0, 0, 1, 1,
        0, 0, 0, None,
    )

    # Start with green tint at low opacity
    win32gui.SetLayeredWindowAttributes(
        hwnd, 0, OPACITY["green"], win32con.LWA_ALPHA
    )

    return hwnd


def _on_paint(hwnd, msg, wp, lp):
    """Fill the entire overlay with the current color."""
    dc, ps = win32gui.BeginPaint(hwnd)

    rect = win32gui.GetClientRect(hwnd)
    if rect[2] > 0 and rect[3] > 0:
        rgb = COLORS_RGB.get(_color, COLORS_RGB["green"])
        color_ref = rgb[0] | (rgb[1] << 8) | (rgb[2] << 16)
        brush = win32gui.CreateSolidBrush(color_ref)
        win32gui.FillRect(dc, rect, brush)
        win32gui.DeleteObject(brush)

    win32gui.EndPaint(hwnd, ps)
    return 0


def _overlay_loop():
    """Main loop: position the overlay on top of the target window."""
    global _overlay_hwnd, _running

    _overlay_hwnd = _create_overlay_window()
    _running = True

    last_rect = None
    last_color = None

    while _running:
        try:
            if _target_hwnd and _color != "off":
                rect = _get_window_rect(_target_hwnd)
                if rect:
                    x, y, right, bottom = rect
                    w = right - x
                    h = bottom - y

                    if rect != last_rect or _color != last_color:
                        # Position overlay exactly on top of the window
                        win32gui.SetWindowPos(
                            _overlay_hwnd,
                            win32con.HWND_TOPMOST,
                            x, y, w, h,
                            win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW,
                        )

                        # Update opacity and repaint if color changed
                        if _color != last_color:
                            opacity = OPACITY.get(_color, 45)
                            win32gui.SetLayeredWindowAttributes(
                                _overlay_hwnd, 0, opacity, win32con.LWA_ALPHA
                            )
                            win32gui.InvalidateRect(_overlay_hwnd, None, True)
                            win32gui.UpdateWindow(_overlay_hwnd)

                        last_rect = rect
                        last_color = _color

                    win32gui.ShowWindow(_overlay_hwnd, win32con.SW_SHOWNOACTIVATE)
                else:
                    win32gui.ShowWindow(_overlay_hwnd, win32con.SW_HIDE)
                    last_rect = None
            else:
                win32gui.ShowWindow(_overlay_hwnd, win32con.SW_HIDE)
                last_rect = None
                last_color = None

            win32gui.PumpWaitingMessages()
            time.sleep(0.05)

        except Exception as e:
            print(f"Overlay error: {e}")
            time.sleep(0.1)

    try:
        win32gui.DestroyWindow(_overlay_hwnd)
    except Exception:
        pass


def start():
    """Start the overlay in a background thread."""
    global _overlay_thread
    if _overlay_thread and _overlay_thread.is_alive():
        return
    _overlay_thread = threading.Thread(target=_overlay_loop, daemon=True)
    _overlay_thread.start()


def stop():
    """Stop the overlay."""
    global _running
    _running = False
