"""Win32 window discovery and manipulation."""

import ctypes
import ctypes.wintypes as wintypes
from dataclasses import dataclass

import win32con
import win32gui
import win32process

from config import MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH, TASKBAR_HEIGHT


@dataclass
class WindowInfo:
    hwnd: int
    title: str
    pid: int
    x: int
    y: int
    width: int
    height: int
    is_minimized: bool
    is_maximized: bool
    process_name: str = ""

    def to_dict(self) -> dict:
        return {
            "hwnd": self.hwnd,
            "title": self.title,
            "pid": self.pid,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "is_minimized": self.is_minimized,
            "is_maximized": self.is_maximized,
            "process_name": self.process_name,
        }


def get_process_name(pid: int) -> str:
    """Get process executable name from PID."""
    try:
        import psutil
        proc = psutil.Process(pid)
        return proc.name()
    except Exception:
        return ""


def get_monitor_workarea() -> tuple[int, int, int, int]:
    """Get primary monitor work area (excludes taskbar)."""
    monitor = ctypes.windll.user32.MonitorFromPoint(
        wintypes.POINT(0, 0), 1  # MONITOR_DEFAULTTOPRIMARY
    )
    info = wintypes.RECT()
    # Use SystemParametersInfo to get work area
    ctypes.windll.user32.SystemParametersInfoW(
        0x0030,  # SPI_GETWORKAREA
        0,
        ctypes.byref(info),
        0,
    )
    return info.left, info.top, info.right, info.bottom


def discover_windows() -> list[WindowInfo]:
    """Find all visible, real application windows."""
    windows: list[WindowInfo] = []

    def enum_callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True

        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True

        # Skip windows with no size or tiny windows
        try:
            rect = win32gui.GetWindowRect(hwnd)
        except Exception:
            return True

        x, y, right, bottom = rect
        width = right - x
        height = bottom - y

        if width < MIN_WINDOW_WIDTH or height < MIN_WINDOW_HEIGHT:
            return True

        # Skip tool windows, tooltips, etc.
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if ex_style & win32con.WS_EX_TOOLWINDOW:
            return True

        # Must be an app window (has WS_EX_APPWINDOW or no owner)
        owner = win32gui.GetWindow(hwnd, win32con.GW_OWNER)
        if owner and not (ex_style & win32con.WS_EX_APPWINDOW):
            return True

        # Get process info
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        is_minimized = bool(style & win32con.WS_MINIMIZE)
        is_maximized = bool(style & win32con.WS_MAXIMIZE)

        windows.append(
            WindowInfo(
                hwnd=hwnd,
                title=title,
                pid=pid,
                x=x,
                y=y,
                width=width,
                height=height,
                is_minimized=is_minimized,
                is_maximized=is_maximized,
                process_name=get_process_name(pid),
            )
        )
        return True

    win32gui.EnumWindows(enum_callback, None)
    return windows


def move_window(hwnd: int, x: int, y: int, width: int, height: int) -> bool:
    """Move and resize a window. Restores it first if minimized/maximized."""
    try:
        # Restore if minimized or maximized
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        if style & (win32con.WS_MINIMIZE | win32con.WS_MAXIMIZE):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        win32gui.SetWindowPos(
            hwnd,
            None,
            x,
            y,
            width,
            height,
            win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE,
        )
        return True
    except Exception as e:
        print(f"Failed to move window {hwnd}: {e}")
        return False


def focus_window(hwnd: int) -> bool:
    """Bring a window to the foreground."""
    try:
        # Restore if minimized
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception as e:
        print(f"Failed to focus window {hwnd}: {e}")
        return False


def minimize_window(hwnd: int) -> bool:
    """Minimize a window."""
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return True
    except Exception:
        return False


def inject_text(hwnd: int, text: str) -> bool:
    """Send text to a window by simulating keyboard input.

    Focuses the window first, then uses SendInput to type the text.
    For terminal windows, clipboard paste (Ctrl+V) is more reliable.
    """
    try:
        focus_window(hwnd)

        import time
        time.sleep(0.1)  # Brief pause for focus to take effect

        # Use clipboard paste for reliability (works with terminals)
        import win32clipboard

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()

        # Simulate Ctrl+V
        VK_CONTROL = 0x11
        VK_V = 0x56

        inputs = []

        # Key down: Ctrl
        ki_down_ctrl = ctypes.c_ulong(0)
        inputs.append((1, ctypes.c_ulong(VK_CONTROL), ctypes.c_ulong(0), ctypes.c_ulong(0)))

        # Use SendInput via ctypes for reliability
        import subprocess
        # Actually, let's use pyautogui-style approach with win32api
        import win32api
        win32api.keybd_event(VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(VK_V, 0, 0, 0)
        win32api.keybd_event(VK_V, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

        return True
    except Exception as e:
        print(f"Failed to inject text into {hwnd}: {e}")
        return False
