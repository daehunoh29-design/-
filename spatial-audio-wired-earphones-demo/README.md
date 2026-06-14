# spatial-audio-wired-earphones-demo

## Project Purpose

This repository provides a spatial audio test demo for wired earphones on Ubuntu/Linux. It uses OpenAL Soft HRTF binaural rendering with stereo output to simulate sounds coming from front, front-left, front-right, left, right, and back directions.

## Key Features

- Six direction test sounds: `front`, `front_left`, `front_right`, `left`, `right`, `back`
- Distance comparison: `1m` and `3m`
- OpenAL Soft HRTF binaural rendering for stereo headphone output
- Interactive keyboard mode and JSON demo playback mode

## Why Headphones/Earphones?

HRTF binaural rendering models the time and frequency differences between left and right ears to create directional audio cues. This technique works best with stereo headphone or earphone output, not speaker output.

## Requirements

```bash
sudo apt update
sudo apt install -y build-essential cmake libopenal-dev libsndfile1-dev python3
```

## Build and Run

```bash
git clone <repo-url>
cd spatial-audio-wired-earphones-demo
python3 ./scripts/generate_audio.py
./scripts/build.sh
./scripts/run_demo.sh
```

`./scripts/run_demo.sh` launches the demo in `--interactive` mode by default.

## System Setup

1. Connect wired earphones.
2. Set the Linux audio output device to `Analog Stereo Output` or a stereo headphone output.
3. Disable virtual surround, equalizer, and spatial audio enhancement features.
4. Ensure OpenAL Soft is configured to use HRTF if available.

## Run Modes

- Interactive mode

```bash
./build/spatial_audio_demo --interactive
```

- JSON demo mode

```bash
./build/spatial_audio_demo --demo assets/config/demo_positions.json
```

- Single position test

```bash
./build/spatial_audio_demo --azimuth 45 --distance 1.0 --wav assets/audio/beep.wav
```

## Demo Procedure

1. Plug in wired earphones.
2. Confirm the audio output is `Analog Stereo Output`.
3. Turn off virtual surround and equalizer effects.
4. Run the demo.
5. Repeat direction tests to verify spatial cues.
6. Press `d` during interactive mode to toggle between `1m` and `3m` distances.

## Future Extensions

This demo can be extended into a prototype for assistive navigation systems, such as obstacle direction guidance for visually impaired users. Future work may include actual distance sensing, obstacle position input, and voice instructions.
