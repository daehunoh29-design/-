#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from spatial_audio_demo import (
    ASSET_DIR,
    DIRECTIONS,
    EAR_DISTANCE_M,
    LISTENER_POSITION_M,
    ROOM_DIMENSIONS_M,
    SAMPLE_RATE,
    render_spatial_audio,
    resolve_path,
    stereo_wav_bytes,
)


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"


def json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


class SpatialAudioHandler(SimpleHTTPRequestHandler):
    server_version = "SpatialAudioWeb/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, status: int, payload: dict) -> None:
        body = json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status: int, message: str) -> None:
        self.send_json(status, {"error": message})

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/api/config":
            self.send_json(
                200,
                {
                    "sampleRate": SAMPLE_RATE,
                    "room": {
                        "width": ROOM_DIMENSIONS_M[0],
                        "depth": ROOM_DIMENSIONS_M[1],
                    },
                    "listener": {
                        "x": LISTENER_POSITION_M[0],
                        "y": LISTENER_POSITION_M[1],
                        "earDistance": EAR_DISTANCE_M,
                    },
                    "sounds": list(DIRECTIONS.keys()) + ["beep"],
                },
            )
            return

        if route == "/":
            self.path = "/index.html"

        super().do_GET()

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        if route != "/api/render":
            self.send_error_json(404, "알 수 없는 API입니다.")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            azimuth = float(payload["azimuth"])
            distance = float(payload["distance"])
            sound = str(payload.get("sound", "beep"))
        except Exception:
            self.send_error_json(400, "요청 데이터가 올바르지 않습니다.")
            return

        if sound not in set(DIRECTIONS.keys()) | {"beep"}:
            self.send_error_json(400, "지원하지 않는 사운드입니다.")
            return

        distance = max(0.35, min(distance, 3.25))
        wav_path = resolve_path(ASSET_DIR / f"{sound}.wav")

        try:
            stereo = render_spatial_audio(wav_path, azimuth, distance)
            body = stereo_wav_bytes(stereo)
        except Exception as exc:
            self.send_error_json(500, str(exc))
            return

        self.send_response(200)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Spatial-Azimuth", f"{azimuth:.2f}")
        self.send_header("X-Spatial-Distance", f"{distance:.2f}")
        self.end_headers()
        self.wfile.write(body)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="macOS top-view spatial audio web app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), SpatialAudioHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"Spatial audio web app: {url}")
    print("종료: Ctrl+C")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n종료합니다.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
