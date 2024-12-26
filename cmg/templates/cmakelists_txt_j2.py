TEMPLATE = """
cmake_minimum_required(VERSION 3.10)

# Set the project name
project({{schema.namespace}})

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fprofile-instr-generate -fcoverage-mapping")
cmake_policy(SET CMP0135 NEW)

add_library({{schema.namespace}} {{schema.get_cmakelists_src()}})

# Testing
include(FetchContent)

FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/03597a01ee50ed33e9dfd640b249b4be3799d395.zip
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

add_executable(
  test_{{schema.namespace}}
  test_{{schema.namespace}}.cpp
)
target_link_libraries(
  test_{{schema.namespace}}
  GTest::gtest_main
  {{schema.namespace}}
)


include(GoogleTest)
gtest_discover_tests(test_{{schema.namespace}})

"""
