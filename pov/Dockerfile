# Copyright (c) 2025 Cromulence
ARG BUILD_BASE=ubuntu:24.04
ARG RUN_BASE=ubuntu:24.04
ARG LOG_FILE=/var/tmp/cfs.log

FROM ${BUILD_BASE} AS build
ARG LOG_FILE
ENV LOG_FILE=$LOG_FILE

# Set environment variables to non-interactive (avoid prompts during build)
ENV DEBIAN_FRONTEND=noninteractive

# Include an environmental variable to point to the necessary binary path
# Update package list and install dependencies
RUN apt-get update -y && \
    apt-get install -y \
    --no-install-recommends \
    python3 \
    python3-pip \
    pkg-config \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    ulimit -c unlimited

WORKDIR /
ADD pov pov
ADD utils pov/utils
RUN python3 -m pip install spacepackets --break-system-packages

CMD python3 pov/pov.py --log_file "$LOG_FILE"
