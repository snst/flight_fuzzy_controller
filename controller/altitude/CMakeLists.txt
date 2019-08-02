cmake_minimum_required(VERSION 2.8.9)
project(altitude_fuzzy_controller)
#set(CMAKE_BUILD_TYPE "Debug")

#add_executable(${PROJECT_NAME} main.cpp)

add_custom_target(${PROJECT_NAME}_gen
  COMMAND java -jar ${FCL_GENERATOR} -c ${CMAKE_CURRENT_SOURCE_DIR}/model/altitude.fcl > ./generated/altitude.h
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  COMMENT "run generated test2 in ${CMAKE_CURRENT_SOURCE_DIR}"
)

add_library(${PROJECT_NAME} SHARED main.cpp)
add_dependencies(${PROJECT_NAME} ${PROJECT_NAME}_gen)

