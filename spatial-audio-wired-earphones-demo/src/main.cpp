#include "SpatialDemo.h"
#include "DemoConfig.h"
#include <iostream>
#include <string>
#include <vector>

int main(int argc, char* argv[]) {
    SpatialDemo demo;
    if (!demo.initialize()) {
        return 1;
    }

    if (argc < 2) {
        std::cout << "Usage:\n"
                  << "  " << argv[0] << " --interactive\n"
                  << "  " << argv[0] << " --demo assets/config/demo_positions.json\n"
                  << "  " << argv[0] << " --azimuth 45 --distance 1.0 --wav assets/audio/beep.wav\n";
        return 0;
    }

    std::string mode = argv[1];
    if (mode == "--interactive") {
        demo.runInteractiveDemo();
        return 0;
    }

    if (mode == "--demo" && argc >= 3) {
        DemoConfig config;
        if (!config.loadFromJson(argv[2])) {
            std::cerr << "Failed to load demo configuration: " << argv[2] << "\n";
            return 1;
        }
        demo.runDemoList(config.getPositions());
        return 0;
    }

    if (mode == "--azimuth") {
        if (argc < 7) {
            std::cerr << "Missing arguments for --azimuth mode.\n";
            return 1;
        }
        float azimuth = std::stof(argv[2]);
        float distance = 1.0f;
        std::string wavPath;
        for (int i = 3; i + 1 < argc; i += 2) {
            std::string key = argv[i];
            if (key == "--distance") {
                distance = std::stof(argv[i + 1]);
            } else if (key == "--wav") {
                wavPath = argv[i + 1];
            }
        }
        if (wavPath.empty()) {
            std::cerr << "A WAV file is required for --azimuth mode.\n";
            return 1;
        }
        demo.playAt(azimuth, distance, wavPath);
        return 0;
    }

    std::cerr << "Unknown mode: " << mode << "\n";
    return 1;
}
