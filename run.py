"""Application entry point for local development."""

from __future__ import annotations

import os
import socket

from app import create_app

app = create_app("development")


def _configured_port() -> int:
    """Return the requested local port or the default development port."""
    raw_port = os.getenv("PORT", os.getenv("FLASK_RUN_PORT", "5000"))
    try:
        port = int(raw_port)
    except ValueError:
        print(f"Invalid port '{raw_port}'. Falling back to 5000.")
        return 5000
    if 1 <= port <= 65535:
        return port
    print(f"Port {port} is outside the valid range. Falling back to 5000.")
    return 5000


def _available_port(host: str, preferred_port: int) -> int:
    """Return the preferred port or the next available local development port."""
    for port in range(preferred_port, min(preferred_port + 50, 65536)):
        if _is_port_available(host, port):
            return port
    raise RuntimeError("No available local port found between requested port and +49.")


def _is_port_available(host: str, port: int) -> bool:
    """Return whether the local development server can bind to the port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex((host, port)) != 0


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    preferred_port = _configured_port()
    port = _available_port(host, preferred_port)

    if port != preferred_port:
        print(f"Port {preferred_port} is busy. Starting on port {port} instead.")
    print(f"Open http://{host}:{port}/")
    app.run(host=host, port=port, debug=True, use_reloader=False)
