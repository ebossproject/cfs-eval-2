# Copyright (c) 2025 Cromulence
# Use Ubuntu 24.04 LTS as the base image
FROM ubuntu:24.04 AS build

# Disable interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    clang \
    lld \
    cmake \
    ninja-build \
    git \
    make \
    wget \
    curl \
    zip \
    unzip \
    time \
    ca-certificates \
    pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install vcpkg
ENV VCPKG_ROOT=/opt/vcpkg
ENV PATH="${VCPKG_ROOT}:${PATH}"

RUN git clone --depth 1 --branch 2025.03.19 https://github.com/microsoft/vcpkg.git ${VCPKG_ROOT} && \
    ${VCPKG_ROOT}/bootstrap-vcpkg.sh -disableMetrics

# Declare defaults for later stages (can be overridden)
ENV TOOLCHAIN_FILE=/opt/toolchain/toolchain.cmake
ENV TRIPLET=x64-linux
ENV VCPKG_OVERLAY_PORTS=/opt/vcpkg-overlays/ports
ENV VCPKG_OVERLAY_TRIPLETS=/opt/vcpkg-overlays/triplets

# Create expected directories
RUN mkdir -p /opt/toolchain /opt/vcpkg-overlays/ports /opt/vcpkg-overlays/triplets /opt/dependencies
COPY toolchains/toolchain.cmake /opt/toolchain/toolchain.cmake
COPY vcpkg-triplets/x64-linux.cmake /opt/vcpkg-overlays/triplets/x64-linux.cmake

COPY vcpkg-overlays/ports /opt/vcpkg-overlays/ports
COPY dependencies /opt/dependencies

RUN MISSIONCONFIG=sample vcpkg install cfs --triplet=${TRIPLET}

WORKDIR /
RUN cp -r /opt/vcpkg/packages/cfs_${TRIPLET}/cpu1 ./release

ARG RUN_BASE=ubuntu:24.04
FROM ubuntu:24.04 AS runtime

ENV CHALLENGE_BINARY="/cfs/core-cpu1"

RUN useradd -m user

WORKDIR /
COPY --from=build /release /cfs
COPY --from=build /opt/vcpkg/buildtrees /cfs/buildtrees
COPY --from=build /opt/vcpkg/packages /cfs/packages

ARG LOG_FILE=/var/tmp/cfs.log
ENV LOG_FILE=$LOG_FILE

# Update package list and install dependencies
RUN apt-get update -y && \
    apt-get install -y \
    --no-install-recommends \
    python3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN chmod -R o+w /cfs

USER user

COPY --chmod=755 utils/run_cfs.sh /cfs/run_cfs.sh

WORKDIR /cfs
CMD /cfs/run_cfs.sh "$LOG_FILE"
