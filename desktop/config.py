"""Configuration for Window Commander desktop agent."""

HOST = "0.0.0.0"
PORT = 8765
WS_PATH = "/ws"

# Minimum window size to include in discovery (filters out tiny hidden windows)
MIN_WINDOW_WIDTH = 100
MIN_WINDOW_HEIGHT = 50

# Gap between windows in layouts (pixels)
LAYOUT_GAP = 4

# Taskbar reserve (pixels from bottom)
TASKBAR_HEIGHT = 48
