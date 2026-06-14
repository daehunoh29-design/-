#include "DemoConfig.h"
#include <fstream>
#include <cctype>
#include <iterator>

namespace {

void skipWhitespace(const std::string& text, size_t& pos) {
    while (pos < text.size() && std::isspace(static_cast<unsigned char>(text[pos]))) {
        ++pos;
    }
}

bool parseString(const std::string& text, size_t& pos, std::string& out) {
    out.clear();
    skipWhitespace(text, pos);
    if (pos >= text.size() || text[pos] != '"') {
        return false;
    }
    ++pos;
    while (pos < text.size() && text[pos] != '"') {
        if (text[pos] == '\\' && pos + 1 < text.size()) {
            ++pos;
            out.push_back(text[pos]);
        } else {
            out.push_back(text[pos]);
        }
        ++pos;
    }
    if (pos >= text.size() || text[pos] != '"') {
        return false;
    }
    ++pos;
    return true;
}

bool parseNumber(const std::string& text, size_t& pos, float& out) {
    skipWhitespace(text, pos);
    size_t start = pos;
    if (pos < text.size() && (text[pos] == '-' || text[pos] == '+')) {
        ++pos;
    }
    while (pos < text.size() && (std::isdigit(static_cast<unsigned char>(text[pos])) || text[pos] == '.')) {
        ++pos;
    }
    if (start == pos) {
        return false;
    }
    try {
        out = std::stof(text.substr(start, pos - start));
        return true;
    } catch (...) {
        return false;
    }
}

}

bool DemoConfig::loadFromJson(const std::string& path) {
    positions_.clear();
    std::ifstream file(path);
    if (!file.is_open()) {
        return false;
    }

    std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    size_t pos = 0;
    skipWhitespace(content, pos);
    if (pos >= content.size() || content[pos] != '[') {
        return false;
    }
    ++pos;

    while (true) {
        skipWhitespace(content, pos);
        if (pos >= content.size()) {
            return false;
        }
        if (content[pos] == ']') {
            break;
        }
        if (content[pos] != '{') {
            return false;
        }
        ++pos;

        DemoPosition item;
        while (true) {
            skipWhitespace(content, pos);
            if (pos >= content.size()) {
                return false;
            }
            if (content[pos] == '}') {
                ++pos;
                break;
            }
            std::string key;
            if (!parseString(content, pos, key)) {
                return false;
            }
            skipWhitespace(content, pos);
            if (pos >= content.size() || content[pos] != ':') {
                return false;
            }
            ++pos;
            skipWhitespace(content, pos);
            if (key == "name") {
                if (!parseString(content, pos, item.name)) {
                    return false;
                }
            } else if (key == "wav") {
                if (!parseString(content, pos, item.wav)) {
                    return false;
                }
            } else if (key == "azimuth") {
                if (!parseNumber(content, pos, item.azimuth)) {
                    return false;
                }
            } else if (key == "distance") {
                if (!parseNumber(content, pos, item.distance)) {
                    return false;
                }
            } else {
                return false;
            }
            skipWhitespace(content, pos);
            if (pos < content.size() && content[pos] == ',') {
                ++pos;
                continue;
            }
        }

        positions_.push_back(item);
        skipWhitespace(content, pos);
        if (pos < content.size() && content[pos] == ',') {
            ++pos;
            continue;
        }
    }

    return true;
}

const std::vector<DemoPosition>& DemoConfig::getPositions() const {
    return positions_;
}
