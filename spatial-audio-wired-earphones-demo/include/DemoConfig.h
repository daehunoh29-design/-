#pragma once

#include <string>
#include <vector>

struct DemoPosition {
    std::string name;
    float azimuth;
    float distance;
    std::string wav;
};

class DemoConfig {
public:
    bool loadFromJson(const std::string& path);
    const std::vector<DemoPosition>& getPositions() const;

private:
    std::vector<DemoPosition> positions_;
};
