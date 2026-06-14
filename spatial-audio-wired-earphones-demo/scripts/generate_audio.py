#!/usr/bin/env python3
import math
import os
import wave
import struct

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'audio')
SAMPLE_RATE = 44100
DURATION_SECONDS = 0.7
AMPLITUDE = 0.4

TONE_CONFIG = {
    'beep': 880,
    'front': 440,
    'front_left': 466,
    'front_right': 494,
    'left': 523,
    'right': 587,
    'back': 659,
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

for name, freq in TONE_CONFIG.items():
    path = os.path.join(OUTPUT_DIR, f'{name}.wav')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        frames = []
        for i in range(int(SAMPLE_RATE * DURATION_SECONDS)):
            sample = AMPLITUDE * math.sin(2.0 * math.pi * freq * i / SAMPLE_RATE)
            int_sample = int(max(-1.0, min(1.0, sample)) * 32767)
            frames.append(struct.pack('<h', int_sample))
        w.writeframes(b''.join(frames))

print('Generated audio assets in', OUTPUT_DIR)
