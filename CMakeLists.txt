cmake_minimum_required(VERSION 3.4.3)

project(flight_fuzzy_controller
  LANGUAGES CXX C
  VERSION 1.8.0
)

set(FCL_GENERATOR
    ${CMAKE_CURRENT_SOURCE_DIR}/tools/jFuzzyLogic.jar)

add_subdirectory(controller/altitude)
