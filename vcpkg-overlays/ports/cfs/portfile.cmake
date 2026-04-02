# Copyright (c) 2025 Cromulence
execute_process(
    COMMAND git clone --recursive https://github.com/nasa/cFS /cfs
    RESULT_VARIABLE GIT_CLONE_RESULT
)
if(NOT GIT_CLONE_RESULT EQUAL 0)
    message(FATAL_ERROR "Git clone failed")
endif()

# Checkout a specific commit
execute_process(
    COMMAND git checkout 9c786d2536821aae608560e0d75835e3637b499d
    WORKING_DIRECTORY /cfs
    RESULT_VARIABLE GIT_CHECKOUT_RESULT
)
if(NOT GIT_CHECKOUT_RESULT EQUAL 0)
    message(FATAL_ERROR "Git checkout failed")
endif()

set(CMAKE_C_COMPILER clang)
set(CMAKE_CXX_COMPILER clang++)
set(DEPS_SOURCE_PATH /deps)
set(SOURCE_PATH /cfs)
set(MM_SOURCE_PATH /opt/dependencies/mm)

message(STATUS "Setup build environment")
vcpkg_execute_required_process(
  COMMAND ${CMAKE_COMMAND} -E copy_directory ${SOURCE_PATH}/cfe/cmake/sample_defs ./sample_defs
  WORKING_DIRECTORY ${SOURCE_PATH}
  LOGNAME setup
)

vcpkg_execute_required_process(
  COMMAND ${CMAKE_COMMAND} -E copy_directory ${MM_SOURCE_PATH} ./cfe/modules/mm
  WORKING_DIRECTORY ${SOURCE_PATH}
  LOGNAME setup
)

vcpkg_execute_required_process(
  COMMAND ${CMAKE_COMMAND} -E copy $ENV{TOOLCHAIN_FILE} ./sample_defs/toolchain-custom.cmake
  WORKING_DIRECTORY ${SOURCE_PATH}
  LOGNAME setup
)

vcpkg_execute_required_process(
  COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_LIST_DIR}/custom_osconfig.cmake ./sample_defs
  WORKING_DIRECTORY ${SOURCE_PATH}
  LOGNAME setup
)

vcpkg_execute_required_process(
    COMMAND "${CMAKE_COMMAND}" -E make_directory ./cfe/build
    WORKING_DIRECTORY "${SOURCE_PATH}"
    LOGNAME setup
)

vcpkg_apply_patches(SOURCE_PATH ${SOURCE_PATH} PATCHES "build_custom.patch")
vcpkg_apply_patches(SOURCE_PATH ${SOURCE_PATH}/cfe PATCHES "mm_static_link.patch")
# These files are not automatically generated due to the syntax within the
# elf2cfetbl CMakeFiles so we must make them for the build to succeed
file(MAKE_DIRECTORY ${CURRENT_BUILDTREES_DIR}/$ENV{TRIPLET}-rel/tables/staging)
file(MAKE_DIRECTORY ${CURRENT_BUILDTREES_DIR}/$ENV{TRIPLET}-dbg/tables/staging)


set(SOURCE_PATH /cfs/cfe/build)
# --- Configure build ---
execute_process(
    COMMAND cmake ..
        -DMISSIONCONFIG=sample
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DSIMULATION=custom
        -DCMAKE_INSTALL_PREFIX=${CURRENT_PACKAGES_DIR}
    WORKING_DIRECTORY ${SOURCE_PATH}
    RESULT_VARIABLE _cmake_configure_result
)
if(NOT _cmake_configure_result EQUAL 0)
    message(FATAL_ERROR "cFS configure step failed")
endif()

# --- Patch platformdata_tool invocation ---
execute_process(
    COMMAND sed -i -E
        "s|cd /opt/vcpkg/buildtrees/cfs/${VCPKG_TARGET_TRIPLET}-rel/cfeconfig_platformdata_tool && cfeconfig_platformdata_tool|cd /opt/vcpkg/buildtrees/cfs/${VCPKG_TARGET_TRIPLET}-rel/cfeconfig_platformdata_tool && ./cfeconfig_platformdata_tool|g"
        cfeconfig_platformdata_tool/CMakeFiles/cfgtool-execute-custom_default_cpu1.dir/build.make
    WORKING_DIRECTORY ${SOURCE_PATH}
    RESULT_VARIABLE _sed_patch_result
)
if(NOT _sed_patch_result EQUAL 0)
    message(FATAL_ERROR "Failed to patch cfeconfig_platformdata_tool command")
endif()

# --- Build mission-prebuild ---
execute_process(
    COMMAND cmake --build . --config Release --target mission-prebuild
    WORKING_DIRECTORY ${SOURCE_PATH}
    RESULT_VARIABLE _mission_prebuild_result
)
if(NOT _mission_prebuild_result EQUAL 0)
    message(FATAL_ERROR "mission-prebuild target failed")
endif()

# --- Build mission-all ---
execute_process(
    COMMAND cmake --build . --config Release --target mission-all
    WORKING_DIRECTORY ${SOURCE_PATH}
    RESULT_VARIABLE _mission_all_result
)
if(NOT _mission_all_result EQUAL 0)
    message(FATAL_ERROR "mission-all target failed")
endif()

# --- Build mission-install ---
execute_process(
    COMMAND cmake --build . --config Release --target mission-install
    WORKING_DIRECTORY ${SOURCE_PATH}
    RESULT_VARIABLE _mission_install_result
)
if(NOT _mission_install_result EQUAL 0)
    message(FATAL_ERROR "mission-install target failed")
endif()

# --- Package results ---
file(INSTALL
    DESTINATION ${CURRENT_PACKAGES_DIR}/tools/cfs
    TYPE DIRECTORY
    FILES "${SOURCE_PATH}"
)

vcpkg_copy_pdbs()

vcpkg_fixup_pkgconfig()
