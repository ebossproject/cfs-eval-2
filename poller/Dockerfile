# Copyright (c) 2025 Cromulence
ARG BUILD_BASE=ubuntu:24.04
ARG RUN_BASE=ubuntu:24.04

# Use the official Ubuntu base image
FROM ${BUILD_BASE} AS build

# Set environment variables to non-interactive (avoid prompts during build)
ENV DEBIAN_FRONTEND=noninteractive

# Include an environmental variable to point to the necessary binary path
# Update package list and install dependencies
RUN apt-get update -y && \
    apt-get install -y \
    --no-install-recommends \
    python3 \
    python3-pip \
    python3-pyqt5 \
    python3-zmq \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /
ADD utils poller/utils
ADD poller/poller.py poller/poller.py

RUN python3 -m pip install spacepackets --break-system-packages

CMD python3 poller/poller.py
