#pragma once

#include <string>
#include <vector>
#include "DemoConfig.h"
#include "AudioDevice.h"

class SpatialDemo {
public:
    SpatialDemo();
    ~SpatialDemo();

    bool initialize();
    void playAt(float azimuthDeg, float distanceMeters, const std::string& wavPath);
    void runInteractiveDemo();
    void runDemoList(const std::vector<DemoPosition>& positions);

private:
    bool initializeOpenAL();
    bool loadWav(const std::string& path, ALenum& format, ALvoid*& data, ALsizei& size, ALsizei& freq);
    void unloadWav(ALvoid* data);
    void setSourcePosition(ALuint source, float azimuthDeg, float distanceMeters);
    void printStartupInfo();

    AudioDevice audioDevice_;
    bool initialized_ = false;
};
