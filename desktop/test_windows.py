"""Quick test script to verify window discovery and layouts work."""

from window_manager import discover_windows, get_monitor_workarea
from layouts import get_available_layouts, get_layout_slots


def main():
    # Test monitor work area
    left, top, right, bottom = get_monitor_workarea()
    print(f"Monitor work area: ({left}, {top}) -> ({right}, {bottom})")
    print(f"  Size: {right - left} x {bottom - top}")
    print()

    # Test window discovery
    windows = discover_windows()
    print(f"Discovered {len(windows)} windows:")
    print("-" * 80)
    for w in windows:
        title = w.title[:50].encode("ascii", errors="replace").decode()
        print(f"  [{w.hwnd:>8}] {title:<50} {w.width}x{w.height} ({w.process_name})")
    print()

    # Test layouts
    print("Available layouts:")
    for name, info in get_available_layouts().items():
        print(f"  {name}: {info['description']}")

    # Show what a 2x2 layout would look like
    print()
    print("2x2 layout slot positions:")
    for i, slot in enumerate(get_layout_slots("2x2")):
        print(f"  Slot {i}: ({slot.x}, {slot.y}) {slot.width}x{slot.height}")


if __name__ == "__main__":
    main()
