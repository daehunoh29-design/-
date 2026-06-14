cmake_minimum_required(VERSION 3.10)
project(spatial_audio_wired_earphones_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(OpenAL REQUIRED)
find_library(SNDFILE_LIBRARY sndfile)
find_path(SNDFILE_INCLUDE_DIR sndfile.h)

if(NOT SNDFILE_LIBRARY OR NOT SNDFILE_INCLUDE_DIR)
    message(FATAL_ERROR "Could not find libsndfile. Install libsndfile1-dev and try again.")
endif()

include_directories(${PROJECT_SOURCE_DIR}/include ${SNDFILE_INCLUDE_DIR})

add_executable(spatial_audio_demo
    src/main.cpp
    src/SpatialDemo.cpp
    src/AudioDevice.cpp
    src/DemoConfig.cpp
)

target_link_libraries(spatial_audio_demo PRIVATE OpenAL::OpenAL ${SNDFILE_LIBRARY})

target_compile_definitions(spatial_audio_demo PRIVATE $<$<NOT:$<CONFIG:Debug>>:NDEBUG>)
