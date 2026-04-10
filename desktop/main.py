"""Window Commander — Desktop Agent entry point.

Starts the FastAPI server that manages windows and communicates with the phone app.

Usage:
    python main.py
    python main.py --port 8765
    python main.py --host 0.0.0.0 --port 8765
"""

import argparse
import socket

import uvicorn

from config import HOST, PORT


def get_local_ip() -> str:
    """Get the machine's local network IP for phone connection."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    parser = argparse.ArgumentParser(description="Window Commander Desktop Agent")
    parser.add_argument("--host", default=HOST, help=f"Host to bind (default: {HOST})")
    parser.add_argument("--port", type=int, default=PORT, help=f"Port (default: {PORT})")
    args = parser.parse_args()

    local_ip = get_local_ip()

    print("=" * 50)
    print("  Window Commander — Desktop Agent")
    print("=" * 50)
    print(f"  REST API:   http://{local_ip}:{args.port}")
    print(f"  WebSocket:  ws://{local_ip}:{args.port}/ws")
    print(f"  Health:     http://{local_ip}:{args.port}/health")
    print()
    print("  Connect your phone app to this address.")
    print("=" * 50)

    uvicorn.run("server:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
