"""Child process entry point. Readiness secrets travel only over inherited pipes."""

import argparse
import asyncio
import json
import os
import socket
import sys
from pathlib import Path

import uvicorn

from tabi.core.config import Settings

from .app import create_app
from .contracts import PROTOCOL, WorkerReady
from .runtime import Runtime
from .security import Sessions


async def run(payload, listener, ready_fd):
    settings = Settings(
        config_file=Path(payload["settings"]["config_file"]),
        config_loaded=payload["settings"]["config_loaded"],
        project_root=Path(payload["settings"]["project_root"]),
        cache_root=Path(payload["settings"]["cache_root"]),
        ffmpeg=payload["settings"]["ffmpeg"],
        ffprobe=payload["settings"]["ffprobe"],
    )
    address, port = listener.getsockname()
    if address != "127.0.0.1":
        raise ValueError("worker requires an inherited loopback socket")
    runtime = Runtime(
        settings,
        payload["roots"],
        sessions=Sessions(lifetime=payload.get("session_lifetime", 43200)),
    )
    app = create_app(runtime, f"http://127.0.0.1:{port}", payload["web_root"])
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            access_log=False,
            log_level="critical",
            server_header=False,
            proxy_headers=False,
            timeout_graceful_shutdown=35,
        )
    )
    loop = asyncio.get_running_loop()
    runtime.on_stopped = lambda: loop.call_soon_threadsafe(setattr, server, "should_exit", True)
    serving = asyncio.create_task(server.serve(sockets=[listener]))
    try:
        while not server.started:
            if serving.done():
                await serving
                raise RuntimeError("server stopped before readiness")
            await asyncio.sleep(0.01)
        ready = WorkerReady(
            protocol=PROTOCOL,
            pid=os.getpid(),
            port=port,
            session_id=runtime.sessions.id,
            nonce=payload["nonce"],
            bootstrap=runtime.sessions.ticket(),
            bearer=runtime.sessions.bearer,
        )
        with os.fdopen(ready_fd, "w") as channel:
            channel.write(ready.model_dump_json() + "\n")
            channel.flush()
        await serving
    finally:
        runtime.stop(cancel=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket-fd", type=int, required=True)
    parser.add_argument("--ready-fd", type=int, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(sys.stdin.buffer.readline(65537))
        if payload["protocol"] != PROTOCOL:
            raise ValueError("launcher protocol is incompatible")
        with socket.socket(fileno=args.socket_fd) as listener:
            asyncio.run(run(payload, listener, args.ready_fd))
        return 0
    except Exception:
        print(
            "Local worker failed; check registered folders, static build and configuration",
            file=sys.stderr,
        )
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
