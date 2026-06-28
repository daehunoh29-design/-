#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import math
import sys
import wave
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "assets" / "audio"
CONFIG_PATH = ROOT / "assets" / "config" / "demo_positions.json"
OUTPUT_DIR = ROOT / "output"

SAMPLE_RATE = 44_100
EAR_DISTANCE_M = 0.18
ROOM_DIMENSIONS_M = (7.0, 7.0, 2.8)
LISTENER_POSITION_M = (3.5, 3.5, 1.55)
OUTPUT_PEAK_LEVEL = 0.56
OUTPUT_LIMIT_LEVEL = 0.62

DIRECTIONS = {
    "front": (0.0, "assets/audio/front.wav"),
    "front_left": (45.0, "assets/audio/front_left.wav"),
    "front_right": (-45.0, "assets/audio/front_right.wav"),
    "left": (90.0, "assets/audio/left.wav"),
    "right": (-90.0, "assets/audio/right.wav"),
    "back": (180.0, "assets/audio/back.wav"),
}


@dataclass(frozen=True)
class DemoPosition:
    name: str
    azimuth: float
    distance: float
    wav: Path


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def require_numpy():
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("numpy가 없습니다. ./scripts/setup_macos.sh 를 먼저 실행하세요.") from exc
    return np


def read_mono_wav(path: Path) -> np.ndarray:
    np = require_numpy()

    if not path.exists():
        raise FileNotFoundError(f"WAV 파일을 찾을 수 없습니다: {path}")

    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        sample_rate = handle.getframerate()
        frames = handle.readframes(handle.getnframes())

    if sample_rate != SAMPLE_RATE:
        raise ValueError(f"{path} 의 sample rate가 {SAMPLE_RATE} Hz가 아닙니다: {sample_rate} Hz")
    if sample_width != 2:
        raise ValueError(f"{path} 는 16-bit PCM WAV여야 합니다.")

    samples = np.frombuffer(frames, dtype="<i2").astype(np.float32)
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)

    samples = samples / 32767.0

    return np.clip(samples, -1.0, 1.0)


def write_stereo_wav(path: Path, samples: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(stereo_wav_bytes(samples))


def stereo_wav_bytes(samples: np.ndarray) -> bytes:
    np = require_numpy()

    int_samples = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(int_samples.tobytes())
    return buffer.getvalue()


def source_position_from_azimuth(azimuth_deg: float, distance_m: float) -> np.ndarray:
    np = require_numpy()

    radians = math.radians(azimuth_deg)
    x = LISTENER_POSITION_M[0] - math.sin(radians) * distance_m
    y = LISTENER_POSITION_M[1] + math.cos(radians) * distance_m
    z = LISTENER_POSITION_M[2]
    return np.array([x, y, z])


def ear_microphone_positions() -> np.ndarray:
    np = require_numpy()

    listener = np.array(LISTENER_POSITION_M)
    left_ear = listener + np.array([-EAR_DISTANCE_M / 2.0, 0.0, 0.0])
    right_ear = listener + np.array([EAR_DISTANCE_M / 2.0, 0.0, 0.0])
    return np.column_stack([left_ear, right_ear])


def normalize_audio(samples: np.ndarray, peak: float = OUTPUT_PEAK_LEVEL) -> np.ndarray:
    np = require_numpy()

    max_abs = float(np.max(np.abs(samples))) if samples.size else 0.0
    if max_abs < 1e-9:
        return samples
    return samples / max_abs * peak


def render_spatial_audio(wav_path: Path, azimuth: float, distance: float) -> np.ndarray:
    np = require_numpy()

    try:
        import pyroomacoustics as pra
    except ImportError as exc:
        raise RuntimeError("pyroomacoustics가 없습니다. ./scripts/setup_macos.sh 를 먼저 실행하세요.") from exc

    mono = read_mono_wav(wav_path)
    distance = max(0.35, float(distance))

    room = pra.ShoeBox(
        np.array(ROOM_DIMENSIONS_M),
        fs=SAMPLE_RATE,
        materials=pra.Material(energy_absorption=0.35),
        max_order=8,
    )
    room.add_source(source_position_from_azimuth(azimuth, distance), signal=mono)
    room.add_microphone_array(pra.MicrophoneArray(ear_microphone_positions(), SAMPLE_RATE))
    room.simulate()

    stereo = normalize_audio(room.mic_array.signals.T)
    distance_gain = min(1.0, 1.0 / distance)
    return np.clip(stereo * distance_gain, -OUTPUT_LIMIT_LEVEL, OUTPUT_LIMIT_LEVEL)


def play_stereo(samples: np.ndarray, device: int | None = None) -> None:
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise RuntimeError("sounddevice가 없습니다. ./scripts/setup_macos.sh 를 먼저 실행하세요.") from exc

    sd.play(samples, SAMPLE_RATE, device=device)
    sd.wait()


def load_demo_config(path: Path) -> list[DemoPosition]:
    with path.open("r", encoding="utf-8") as handle:
        raw_items = json.load(handle)

    return [
        DemoPosition(
            name=str(item["name"]),
            azimuth=float(item["azimuth"]),
            distance=float(item["distance"]),
            wav=resolve_path(item["wav"]),
        )
        for item in raw_items
    ]


def play_position(
    item: DemoPosition,
    *,
    output: Path | None,
    play: bool,
    device: int | None,
) -> None:
    stereo = render_spatial_audio(item.wav, item.azimuth, item.distance)

    if output is not None:
        write_stereo_wav(output, stereo)
        print(f"저장됨: {output.relative_to(ROOT) if output.is_relative_to(ROOT) else output}")

    print(f"재생: {item.name} / {item.azimuth:g}도 / {item.distance:g}m")
    if play:
        play_stereo(stereo, device=device)


def run_interactive(device: int | None) -> None:
    print("Mac용 pyroomacoustics 공간 음향 데모")
    print("이어폰을 연결하고 macOS 사운드 출력을 해당 이어폰으로 선택하세요.")
    print("1=앞, 2=왼쪽 앞, 3=오른쪽 앞, 4=왼쪽, 5=오른쪽, 6=뒤, d=거리 변경, q=종료")

    keys = list(DIRECTIONS.items())
    distance = 1.0
    while True:
        key = input(f"\n현재 거리 {distance:g}m > ").strip().lower()
        if key == "q":
            return
        if key == "d":
            distance = 3.0 if distance < 2.0 else 1.0
            continue
        if key not in {"1", "2", "3", "4", "5", "6"}:
            print("1-6, d, q 중 하나를 입력하세요.")
            continue

        name, (azimuth, wav_path) = keys[int(key) - 1]
        play_position(
            DemoPosition(name, azimuth, distance, resolve_path(wav_path)),
            output=None,
            play=True,
            device=device,
        )


def render_all(device: int | None, play: bool) -> None:
    for name, (azimuth, wav_path) in DIRECTIONS.items():
        for distance in (1.0, 3.0):
            item = DemoPosition(name, azimuth, distance, resolve_path(wav_path))
            output = OUTPUT_DIR / f"{name}_{distance:g}m_stereo.wav"
            play_position(item, output=output, play=play, device=device)


def list_devices() -> None:
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise RuntimeError("sounddevice가 없습니다. ./scripts/setup_macos.sh 를 먼저 실행하세요.") from exc

    print(sd.query_devices())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="macOS pyroomacoustics 공간 음향 데모")
    parser.add_argument("--interactive", action="store_true", help="키보드로 방향을 선택하며 재생합니다.")
    parser.add_argument("--demo", type=Path, help="JSON 데모 설정을 순서대로 재생합니다.")
    parser.add_argument("--azimuth", type=float, help="단일 소스의 방위각입니다. 앞=0, 왼쪽=90, 오른쪽=-90, 뒤=180")
    parser.add_argument("--distance", type=float, default=1.0, help="소스 거리(m)입니다.")
    parser.add_argument("--wav", type=Path, help="단일 소스로 사용할 mono WAV 파일입니다.")
    parser.add_argument("--output", type=Path, help="렌더링한 stereo WAV 저장 위치입니다.")
    parser.add_argument("--render-all", action="store_true", help="기본 방향/거리 조합을 output 폴더에 모두 저장합니다.")
    parser.add_argument("--no-play", action="store_true", help="WAV만 저장하고 재생하지 않습니다.")
    parser.add_argument("--device", type=int, help="sounddevice 출력 장치 번호입니다.")
    parser.add_argument("--list-devices", action="store_true", help="macOS에서 보이는 오디오 장치 목록을 출력합니다.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        if args.list_devices:
            list_devices()
            return 0

        play = not args.no_play

        if args.render_all:
            render_all(device=args.device, play=play)
            return 0

        if args.demo:
            for item in load_demo_config(resolve_path(args.demo)):
                play_position(item, output=None, play=play, device=args.device)
            return 0

        if args.azimuth is not None:
            if args.wav is None:
                raise ValueError("--azimuth 모드에서는 --wav 가 필요합니다.")
            output = resolve_path(args.output) if args.output else OUTPUT_DIR / "single_position_stereo.wav"
            item = DemoPosition("single", args.azimuth, args.distance, resolve_path(args.wav))
            play_position(item, output=output, play=play, device=args.device)
            return 0

        run_interactive(device=args.device)
        return 0

    except KeyboardInterrupt:
        print("\n종료합니다.")
        return 130
    except Exception as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
