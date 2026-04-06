cmake_minimum_required(VERSION 3.15)
project(ORION_SafetyCore VERSION 1.0.0 LANGUAGES CXX)

# =============================================================================
# ORION Safety Core - CMake Configuration
# Adapted from GENESIS DUAL-SYSTEM V3.0.1
# =============================================================================

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler warnings
if(MSVC)
    add_compile_options(/W4 /WX)
else()
    add_compile_options(-Wall -Wextra -Werror -pedantic)
endif()

# Build type default
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Options
option(BUILD_TESTS "Build unit tests" ON)
option(BUILD_PYTHON_BINDINGS "Build Python bindings with pybind11" ON)
option(ENABLE_OPENSSL "Use OpenSSL for cryptographic functions" ON)

# =============================================================================
# Dependencies
# =============================================================================

# OpenSSL (optional but recommended for production)
if(ENABLE_OPENSSL)
    find_package(OpenSSL)
    if(OPENSSL_FOUND)
        message(STATUS "OpenSSL found: ${OPENSSL_VERSION}")
        add_definitions(-DUSE_OPENSSL)
    else()
        message(WARNING "OpenSSL not found, using fallback SHA-256")
    endif()
endif()

# pybind11 for Python bindings
if(BUILD_PYTHON_BINDINGS)
    find_package(pybind11 CONFIG)
    if(pybind11_FOUND)
        message(STATUS "pybind11 found: ${pybind11_VERSION}")
    else()
        message(WARNING "pybind11 not found, skipping Python bindings")
        set(BUILD_PYTHON_BINDINGS OFF)
    endif()
endif()

# Google Test for unit tests
if(BUILD_TESTS)
    find_package(GTest)
    if(NOT GTest_FOUND)
        # Fetch GTest if not found
        include(FetchContent)
        FetchContent_Declare(
            googletest
            GIT_REPOSITORY https://github.com/google/googletest.git
            GIT_TAG release-1.12.1
        )
        FetchContent_MakeAvailable(googletest)
    endif()
    enable_testing()
endif()

# =============================================================================
# Include Directories
# =============================================================================

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# =============================================================================
# Library: ORION Safety Core (Header-Only for now)
# =============================================================================

add_library(orion_safety_core INTERFACE)
target_include_directories(orion_safety_core INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

if(OPENSSL_FOUND)
    target_link_libraries(orion_safety_core INTERFACE OpenSSL::Crypto)
endif()

# =============================================================================
# Python Bindings (pybind11)
# =============================================================================

if(BUILD_PYTHON_BINDINGS)
    pybind11_add_module(orion_safety_cpp
        src/python_bindings.cpp
    )

    target_link_libraries(orion_safety_cpp PRIVATE orion_safety_core)

    if(OPENSSL_FOUND)
        target_link_libraries(orion_safety_cpp PRIVATE OpenSSL::Crypto)
    endif()
endif()

# =============================================================================
# Tests
# =============================================================================

if(BUILD_TESTS)
    add_executable(test_dmacas_types
        tests/test_dmacas_types.cpp
    )

    target_link_libraries(test_dmacas_types
        orion_safety_core
        GTest::gtest_main
    )

    include(GoogleTest)
    gtest_discover_tests(test_dmacas_types)
endif()

# =============================================================================
# Installation
# =============================================================================

install(DIRECTORY include/ DESTINATION include)
install(TARGETS orion_safety_core EXPORT ORIONSafetyCoreTargets)

# =============================================================================
# Package Configuration
# =============================================================================

include(CMakePackageConfigHelper)
write_basic_package_version_file(
    "ORIONSafetyCoreConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(EXPORT ORIONSafetyCoreTargets
    FILE ORIONSafetyCoreTargets.cmake
    NAMESPACE ORION::
    DESTINATION lib/cmake/ORIONSafetyCore
)

# =============================================================================
# Summary
# =============================================================================

message(STATUS "")
message(STATUS "ORION Safety Core Configuration Summary")
message(STATUS "========================================")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "OpenSSL: ${ENABLE_OPENSSL}")
if(OPENSSL_FOUND)
    message(STATUS "  Version: ${OPENSSL_VERSION}")
endif()
message(STATUS "Python Bindings: ${BUILD_PYTHON_BINDINGS}")
message(STATUS "Unit Tests: ${BUILD_TESTS}")
message(STATUS "")
