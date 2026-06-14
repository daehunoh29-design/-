#include "AudioDevice.h"
#include <cstring>

#ifndef ALC_HRTF_SOFT
#define ALC_HRTF_SOFT 0x1992
#endif

AudioDevice::AudioDevice() = default;

AudioDevice::~AudioDevice() {
    if (context_) {
        alcMakeContextCurrent(nullptr);
        alcDestroyContext(context_);
    }
    if (device_) {
        alcCloseDevice(device_);
    }
}

bool AudioDevice::initialize() {
    device_ = alcOpenDevice(nullptr);
    if (!device_) {
        errorMessage_ = "Failed to open default OpenAL device.";
        return false;
    }

    const ALCchar* extensions = alcGetString(device_, ALC_EXTENSIONS);
    bool hrtfSupported = extensions && std::strstr(reinterpret_cast<const char*>(extensions), "ALC_SOFT_HRTF");

    if (hrtfSupported) {
        using PFNALCRESETDEVICESOFT = ALCboolean (*)(ALCdevice*, const ALCint*);
        PFNALCRESETDEVICESOFT resetFunc = reinterpret_cast<PFNALCRESETDEVICESOFT>(alcGetProcAddress(device_, "alcResetDeviceSOFT"));
        if (resetFunc) {
            const ALCint attrs[] = { ALC_HRTF_SOFT, ALC_TRUE, 0 };
            resetFunc(device_, attrs);
        }
    }

    context_ = alcCreateContext(device_, nullptr);
    if (!context_) {
        errorMessage_ = "Failed to create OpenAL context.";
        alcCloseDevice(device_);
        device_ = nullptr;
        return false;
    }

    if (!alcMakeContextCurrent(context_)) {
        errorMessage_ = "Failed to make OpenAL context current.";
        alcDestroyContext(context_);
        alcCloseDevice(device_);
        context_ = nullptr;
        device_ = nullptr;
        return false;
    }

    initialized_ = true;
    return true;
}

bool AudioDevice::isInitialized() const {
    return initialized_;
}

ALCdevice* AudioDevice::device() const {
    return device_;
}

ALCcontext* AudioDevice::context() const {
    return context_;
}

std::string AudioDevice::lastError() const {
    return errorMessage_;
}
