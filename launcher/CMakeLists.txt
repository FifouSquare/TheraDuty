cmake_minimum_required(VERSION 3.28)
project(TheraDuty)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_PREFIX_PATH "/opt/homebrew/opt/qt@5")


find_package(Qt5 COMPONENTS
        Core
        Gui
        Widgets
        REQUIRED)

add_executable(TheraDuty main.cpp
)
target_link_libraries(TheraDuty
        Qt5::Core
        Qt5::Gui
        Qt5::Widgets
)

