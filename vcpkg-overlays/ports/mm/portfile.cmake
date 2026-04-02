# Copyright (c) 2025 Cromulence
set(SOURCE_PATH "/opt/dependencies/mm")
message(STATUS "Using local mm dependency at: ${SOURCE_PATH}")
if(NOT EXISTS "${SOURCE_PATH}")
    message(FATAL_ERROR "Local mm dependency not found at ${SOURCE_PATH}. Expected your local repository to be at ${SOURCE_PATH}.")
endif()

set(CMAKE_C_COMPILER clang)
set(CMAKE_CXX_COMPILER clang++)

if(CMAKE_HOST_WIN32)
    string(COMPARE EQUAL "${VCPKG_LIBRARY_LINKAGE}" "dynamic" ENABLE_PUBLIC_SYMBOLS)
    string(COMPARE NOTEQUAL "${VCPKG_LIBRARY_LINKAGE}" "dynamic" DENABLE_HIDDEN_SYMBOLS)
else()
    set(ENABLE_PUBLIC_SYMBOLS OFF)
    set(DENABLE_HIDDEN_SYMBOLS OFF)
endif()

vcpkg_copy_pdbs()

vcpkg_fixup_pkgconfig()
