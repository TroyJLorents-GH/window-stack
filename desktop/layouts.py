"""Grid layout presets for window arrangement."""

from dataclasses import dataclass

from window_manager import get_monitor_workarea, move_window
from config import LAYOUT_GAP


@dataclass
class Slot:
    """A position in a layout grid."""
    x: int
    y: int
    width: int
    height: int


def _compute_grid(rows: int, cols: int, gap: int = LAYOUT_GAP) -> list[Slot]:
    """Compute grid slot positions for the primary monitor work area."""
    left, top, right, bottom = get_monitor_workarea()
    work_w = right - left
    work_h = bottom - top

    # Account for gaps
    cell_w = (work_w - gap * (cols + 1)) // cols
    cell_h = (work_h - gap * (rows + 1)) // rows

    slots = []
    for r in range(rows):
        for c in range(cols):
            sx = left + gap + c * (cell_w + gap)
            sy = top + gap + r * (cell_h + gap)
            slots.append(Slot(x=sx, y=sy, width=cell_w, height=cell_h))

    return slots


# Preset layout definitions: name -> (rows, cols)
PRESETS = {
    "2x1": (1, 2),      # 2 side by side
    "1x2": (2, 1),      # 2 stacked
    "2x2": (2, 2),      # 4 grid
    "3x1": (1, 3),      # 3 across
    "3x2": (2, 3),      # 6 grid
    "4x1": (1, 4),      # 4 across
    "4x2": (2, 4),      # 8 grid (4 top, 4 bottom)
    "1x1": (1, 1),      # fullscreen (minus taskbar)
}


def get_layout_slots(layout_name: str) -> list[Slot]:
    """Get slot positions for a named layout preset."""
    if layout_name not in PRESETS:
        raise ValueError(f"Unknown layout: {layout_name}. Available: {list(PRESETS.keys())}")
    rows, cols = PRESETS[layout_name]
    return _compute_grid(rows, cols)


def apply_layout(layout_name: str, hwnds: list[int]) -> dict:
    """Apply a layout to a list of window handles.

    Windows are placed in order: left-to-right, top-to-bottom.
    If there are more windows than slots, extras are ignored.
    If there are fewer windows than slots, empty slots remain.
    """
    slots = get_layout_slots(layout_name)
    results = {"placed": [], "skipped": [], "empty_slots": 0}

    for i, hwnd in enumerate(hwnds):
        if i >= len(slots):
            results["skipped"].append(hwnd)
            continue

        slot = slots[i]
        success = move_window(hwnd, slot.x, slot.y, slot.width, slot.height)
        if success:
            results["placed"].append({"hwnd": hwnd, "slot": i, "position": vars(slot)})
        else:
            results["skipped"].append(hwnd)

    results["empty_slots"] = max(0, len(slots) - len(hwnds))
    return results


def get_available_layouts() -> dict:
    """Return all available layouts with their descriptions."""
    return {
        name: {
            "rows": rows,
            "cols": cols,
            "total_slots": rows * cols,
            "description": f"{cols} columns x {rows} rows ({rows * cols} windows)",
        }
        for name, (rows, cols) in PRESETS.items()
    }
