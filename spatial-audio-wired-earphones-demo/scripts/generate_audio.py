#!/usr/bin/env python3
import math
import struct
import wave
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'assets' / 'audio'
SAMPLE_RATE = 44100
DURATION_SECONDS = 0.85
PEAK_LEVEL = 0.28

TONE_CONFIG = {
    'beep': 523.25,
    'front': 392.00,
    'front_left': 415.30,
    'front_right': 440.00,
    'left': 466.16,
    'right': 493.88,
    'back': 349.23,
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def raised_cosine_fade(position, duration):
    if duration <= 0.0:
        return 1.0
    phase = max(0.0, min(1.0, position / duration))
    return 0.5 - 0.5 * math.cos(math.pi * phase)


def envelope(t):
    attack = 0.045
    release = 0.22
    if t < attack:
        return raised_cosine_fade(t, attack)
    if t > DURATION_SECONDS - release:
        return raised_cosine_fade(DURATION_SECONDS - t, release)
    return math.exp(-1.75 * (t - attack))


def soft_chime_sample(freq, t):
    vibrato = 1.0 + 0.0025 * math.sin(2.0 * math.pi * 4.8 * t)
    fundamental = math.sin(2.0 * math.pi * freq * vibrato * t)
    octave = 0.32 * math.sin(2.0 * math.pi * freq * 2.0 * t + 0.15)
    fifth = 0.18 * math.sin(2.0 * math.pi * freq * 1.5 * t + 0.35)
    warm_low = 0.13 * math.sin(2.0 * math.pi * freq * 0.5 * t)
    cue = (fundamental + octave + fifth + warm_low) / 1.63

    if 0.18 <= t <= 0.42:
        echo_t = t - 0.18
        echo_env = math.exp(-8.0 * echo_t) * raised_cosine_fade(echo_t, 0.025)
        cue += 0.18 * echo_env * math.sin(2.0 * math.pi * freq * 1.25 * echo_t)

    return math.tanh(cue * 1.1) * envelope(t) * PEAK_LEVEL


for name, freq in TONE_CONFIG.items():
    path = OUTPUT_DIR / f'{name}.wav'
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        frames = []
        for i in range(int(SAMPLE_RATE * DURATION_SECONDS)):
            sample = soft_chime_sample(freq, i / SAMPLE_RATE)
            int_sample = int(max(-1.0, min(1.0, sample)) * 32767)
            frames.append(struct.pack('<h', int_sample))
        w.writeframes(b''.join(frames))

print('Generated audio assets in', OUTPUT_DIR)
