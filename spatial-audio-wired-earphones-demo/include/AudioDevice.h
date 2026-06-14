#pragma once

#include <AL/al.h>
#include <AL/alc.h>
#include <string>

class AudioDevice {
public:
    AudioDevice();
    ~AudioDevice();

    bool initialize();
    bool isInitialized() const;
    ALCdevice* device() const;
    ALCcontext* context() const;
    std::string lastError() const;

private:
    ALCdevice* device_ = nullptr;
    ALCcontext* context_ = nullptr;
    std::string errorMessage_;
    bool initialized_ = false;
};
