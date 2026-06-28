# spatial-audio-wired-earphones-demo

macOS에서 유선 이어폰으로 방향감과 거리감을 확인하는 `pyroomacoustics` 기반 공간 음향 데모입니다.
테스트음은 갑작스러운 고음 비프 대신 짧고 부드러운 차임 계열로 생성됩니다.

## 빠른 실행

```bash
cd spatial-audio-wired-earphones-demo
./scripts/setup_macos.sh
./scripts/run_macos.sh
```

`run_macos.sh`는 기본으로 대화형 모드를 실행합니다.

## macOS 준비

1. 유선 이어폰을 Mac에 연결합니다.
2. macOS `시스템 설정 > 사운드 > 출력`에서 해당 이어폰을 선택합니다.
3. 데모를 실행한 뒤 `1-6`으로 방향을 바꿔 들어봅니다.

## 조작

- `1`: 앞
- `2`: 왼쪽 앞
- `3`: 오른쪽 앞
- `4`: 왼쪽
- `5`: 오른쪽
- `6`: 뒤
- `d`: 거리 `1m` / `3m` 전환
- `q`: 종료

## 실행 모드

탑뷰 웹 실행:

```bash
./scripts/run_web_macos.sh
```

대화형 실행:

```bash
./scripts/run_macos.sh
```

JSON 설정 순서대로 재생:

```bash
./scripts/run_macos.sh --demo assets/config/demo_positions.json
```

특정 위치 하나만 재생하고 stereo WAV로 저장:

```bash
./scripts/run_macos.sh --azimuth 45 --distance 1.0 --wav assets/audio/beep.wav
```

기본 방향과 거리 조합을 모두 `output/`에 저장:

```bash
./scripts/run_macos.sh --render-all --no-play
```

오디오 장치 번호 확인:

```bash
./scripts/run_macos.sh --list-devices
```

특정 장치로 출력:

```bash
./scripts/run_macos.sh --device 2
```

## 구조

- `spatial_audio_demo.py`: pyroomacoustics 기반 메인 데모
- `web_server.py`: 탑뷰 웹 앱 서버
- `web/`: 클릭 기반 탑뷰 UI
- `scripts/setup_macos.sh`: macOS용 가상환경 생성 및 의존성 설치
- `scripts/run_macos.sh`: 데모 실행
- `scripts/run_web_macos.sh`: 웹 앱 실행
- `scripts/generate_audio.py`: 테스트용 mono WAV 생성
- `assets/config/demo_positions.json`: 순차 재생용 방향 설정
- `output/`: 렌더링된 stereo WAV 저장 위치
