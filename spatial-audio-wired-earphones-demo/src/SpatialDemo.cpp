#include "SpatialDemo.h"
#include <AL/al.h>
#include <AL/alc.h>
#include <sndfile.h>
#include <cstring>
#include <cmath>
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <fstream>

namespace {

constexpr float kDefaultGain = 1.0f;
constexpr float kMinDistance = 1.0f;
constexpr float kMaxDistance = 3.0f;

bool fileExists(const std::string& path) {
    std::ifstream f(path);
    return f.good();
}

void sleepMilliseconds(int ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

std::vector<float> polarToCartesian(float azimuthDeg, float distance) {
    float radians = azimuthDeg * static_cast<float>(M_PI) / 180.0f;
    float x = std::sin(radians) * distance;
    float y = 0.0f;
    float z = -std::cos(radians) * distance;
    return {x, y, z};
}

float computeGainForDistance(float distance) {
    float clamped = std::max(kMinDistance, std::min(distance, kMaxDistance));
    float attenuation = kMinDistance / clamped;
    return kDefaultGain * attenuation;
}

}

SpatialDemo::SpatialDemo() = default;

SpatialDemo::~SpatialDemo() {
    if (audioDevice_.isInitialized()) {
        alcMakeContextCurrent(nullptr);
    }
}

bool SpatialDemo::initialize() {
    if (!audioDevice_.initialize()) {
        std::cerr << "Audio device initialization failed: " << audioDevice_.lastError() << "\n";
        return false;
    }
    printStartupInfo();
    alListener3f(AL_POSITION, 0.0f, 0.0f, 0.0f);
    alListener3f(AL_VELOCITY, 0.0f, 0.0f, 0.0f);
    float orientation[] = {0.0f, 0.0f, -1.0f, 0.0f, 1.0f, 0.0f};
    alListenerfv(AL_ORIENTATION, orientation);
    initialized_ = true;
    return true;
}

void SpatialDemo::printStartupInfo() {
    std::cout << "==============================================\n";
    std::cout << "Spatial audio demo for wired earphones (stereo output)\n";
    std::cout << "Please connect wired earphones and select Analog Stereo Output.\n";
    std::cout << "Disable virtual surround, EQ, and sound enhancement effects.\n";
    std::cout << "This demo uses HRTF binaural rendering and stereo headphone output.\n";
    std::cout << "==============================================\n";
}

bool SpatialDemo::loadWav(const std::string& path, ALenum& format, ALvoid*& data, ALsizei& size, ALsizei& freq) {
    if (!fileExists(path)) {
        std::cerr << "WAV file not found: " << path << "\n";
        return false;
    }
    SF_INFO sfInfo;
    SNDFILE* sndFile = sf_open(path.c_str(), SFM_READ, &sfInfo);
    if (!sndFile) {
        std::cerr << "Failed to open WAV file: " << path << "\n";
        return false;
    }
    if (sfInfo.frames <= 0 || sfInfo.channels <= 0) {
        sf_close(sndFile);
        std::cerr << "Invalid WAV file format: " << path << "\n";
        return false;
    }
    std::vector<short> samples(sfInfo.frames * sfInfo.channels);
    sf_count_t framesRead = sf_readf_short(sndFile, samples.data(), sfInfo.frames);
    sf_close(sndFile);
    if (framesRead < 1) {
        std::cerr << "No audio data read from: " << path << "\n";
        return false;
    }
    size = static_cast<ALsizei>(framesRead * sfInfo.channels * sizeof(short));
    freq = sfInfo.samplerate;
    if (sfInfo.channels == 1) {
        format = AL_FORMAT_MONO16;
    } else if (sfInfo.channels == 2) {
        format = AL_FORMAT_STEREO16;
    } else {
        std::cerr << "Unsupported WAV channels: " << sfInfo.channels << "\n";
        return false;
    }
    data = static_cast<ALvoid*>(malloc(size));
    if (!data) {
        std::cerr << "Memory allocation failed for audio data." << "\n";
        return false;
    }
    std::memcpy(data, samples.data(), size);
    return true;
}

void SpatialDemo::unloadWav(ALvoid* data) {
    free(data);
}

void SpatialDemo::setSourcePosition(ALuint source, float azimuthDeg, float distanceMeters) {
    auto coord = polarToCartesian(azimuthDeg, distanceMeters);
    alSource3f(source, AL_POSITION, coord[0], coord[1], coord[2]);
    alSource3f(source, AL_VELOCITY, 0.0f, 0.0f, 0.0f);
    float gain = computeGainForDistance(distanceMeters);
    alSourcef(source, AL_GAIN, gain);
}

void SpatialDemo::playAt(float azimuthDeg, float distanceMeters, const std::string& wavPath) {
    if (!initialized_) {
        std::cerr << "SpatialDemo not initialized.\n";
        return;
    }
    ALenum format;
    ALvoid* data = nullptr;
    ALsizei size = 0;
    ALsizei freq = 0;
    if (!loadWav(wavPath, format, data, size, freq)) {
        return;
    }

    ALuint buffer = 0;
    ALuint source = 0;
    alGenBuffers(1, &buffer);
    alGenSources(1, &source);
    alBufferData(buffer, format, data, size, freq);
    alSourcei(source, AL_BUFFER, buffer);
    alSourcei(source, AL_LOOPING, AL_FALSE);
    alSourcef(source, AL_REFERENCE_DISTANCE, 1.0f);
    alSourcef(source, AL_ROLLOFF_FACTOR, 1.0f);
    alSourcef(source, AL_MAX_DISTANCE, 100.0f);
    setSourcePosition(source, azimuthDeg, distanceMeters);
    alSourcePlay(source);

    ALint state = AL_PLAYING;
    while (state == AL_PLAYING) {
        sleepMilliseconds(50);
        alGetSourcei(source, AL_SOURCE_STATE, &state);
    }

    alDeleteSources(1, &source);
    alDeleteBuffers(1, &buffer);
    unloadWav(data);
}

void SpatialDemo::runDemoList(const std::vector<DemoPosition>& positions) {
    for (const auto& item : positions) {
        std::cout << "Playing " << item.name << " at " << item.azimuth << " deg, " << item.distance << " m\n";
        playAt(item.azimuth, item.distance, item.wav);
        sleepMilliseconds(300);
    }
}

void SpatialDemo::runInteractiveDemo() {
    std::cout << "Interactive spatial audio demo:\n";
    std::cout << "1=front, 2=front_left, 3=front_right, 4=left, 5=right, 6=back\n";
    std::cout << "d=toggle distance, q=quit\n";

    struct Option { std::string name; float azimuth; };
    const std::vector<Option> options = {
        {"front", 0.0f},
        {"front_left", 45.0f},
        {"front_right", -45.0f},
        {"left", 90.0f},
        {"right", -90.0f},
        {"back", 180.0f}
    };

    float distance = 1.0f;
    while (true) {
        std::cout << "Current distance: " << distance << " m. Select direction: ";
        char c = 0;
        std::cin >> c;
        if (!std::cin) {
            break;
        }
        if (c == 'q' || c == 'Q') {
            break;
        }
        if (c == 'd' || c == 'D') {
            distance = (distance < 2.0f) ? 3.0f : 1.0f;
            std::cout << "Distance set to " << distance << " m.\n";
            continue;
        }
        int index = c - '1';
        if (index >= 0 && index < static_cast<int>(options.size())) {
            auto& option = options[index];
            std::cout << "Playing " << option.name << " at " << option.azimuth << " deg, " << distance << " m\n";
            std::string fileName = "assets/audio/" + option.name + ".wav";
            playAt(option.azimuth, distance, fileName);
        } else {
            std::cout << "Invalid selection. Use 1-6, d, q.\n";
        }
    }
}
