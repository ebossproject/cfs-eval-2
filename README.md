> ⚠️ **SECURITY & USE NOTICE**
> 
> Unless specified otherwise, the contents of this repository are distributed according to the following terms.
> 
> Copyright (c) 2024-2026 Cromulence LLC. All rights reserved.
> 
> This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Contract No. HR001124C0487. Any opinions, finding and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of DARPA.
> 
> The U.S. Government has unlimited rights to this software under contract HR001124C0487.
>
> DISTRIBUTION STATEMENT A. Unlimited Distribution
>
> Original work Licensed under MIT License (See `LICENSE`). Derived from open source libraries under respective licenses - see (`THIRD_PARTY_LICENSES.md`)
>
> This repository is provided **solely for research, educational, and defensive security analysis purposes**.
>
> The software contained herein **intentionally includes known vulnerabilities** in third-party libraries and application logic. These vulnerabilities are included **for the purpose of studying reachability analysis, exploitability, and remediation techniques**.
>
> **DO NOT deploy this software in production environments**, on internet-accessible systems, or on systems containing sensitive data.
>
> By downloading, building, or running this software, you acknowledge that you **understand its intended purpose and potential security impact**, and that you assume all responsibility for its use.

# cFS

## Objective: Reachability with Input Synthesis and Remediation (Timed Release)

In this challenge, cFS, a free, open-source software suite designed to run on satellites for communication contains code flaws.

## Overview
This challenge is configured to be built and run using Docker, checked with a poller, and to determine reachability of the present vulnerabilities.

## Usage
This challenge is set up to be built and run locally, pulled from the container registry, or tested with the included docker compose. The simplest way to examine the challenge is with the compose files:

**PLEASE NOTE**: To run poller or pov images alongside cFS, the environment makes use of shared volumes to log the cFS output for investigation. The default location for the shared volume is `/var/tmp`. If this location is not valid on your system you may get errors when trying to run the containers. You may adjust these locations accordingly to get them working in your environment. For more information on shared volumes in docker compose, visit [this link](https://docs.docker.com/reference/compose-file/volumes/)

To build the dockerfiles, run the following command `docker compose build`.

To begin running cFS run the following command `docker compose up -d cfs`

To test cFS with the poller tool, run `docker compose run --rm poller`

To test cFS with pov1, run `docker compose run --rm pov1`

To test cFS with pov2, run `docker compose run --rm pov2`

To test cFS with the pov template, run `docker compose run --rm pov`

To stop any currently running containers, run `docker compose down -v`

## Build Tools
This updated challenge structure relies on vcpkg package manager and cmake working coopreratively to build cFS. This challenge is developed primarily to be built using the Dockerfile locally with Compose. It is viable to build this locally outside the Dockerfile process, however you must have a foundational understanding of vcpkg and cmake, supply your own toolchains and triplets, and make note of the  environmental variables here. Becaues of the additional configuration requirements, we will not be able to help debug builds outside of the Docker Compose.

In this form, cmake will create the build directory, chainload the custom toolchain file to install the dependencies, and build for Release according to the target triplet.

The build leverages the following environmental variables inherited from the base image:

- `VCPKG_OVERLAY_TRIPLETS` - specifies directory to look for target triplets
- `VCPKG_OVERLAY_PORTS` - specifies location to search ports (takes precedence over vcpkg repo)
- `TOOLCHAIN_FILE` - specifies toolchain path and file
- `TRIPLET` - specifies the triplet to use for the cmake configuration
- `VCPKG_ROOT` - specifies the root of the vcpkg install location and other contents

## Poller
The poller runs extensive tests of the cFS software to ensure basic functionality. All tests are expected to pass. This can be used to determine if build modifications have affected the behavior of the system or not.

The poller can be run in a docker container as described above or locally by running the shell script provided in the poller directory.

## POV
Two premade povs are provided for the reachable vulnerabilities. A separate PoV template is provided to test custom triggers.

## Reachability
A JSON file is provided for this challenge to classify reachability for each of the CVE records. Reachability classifications should be determined based on the information provided in the vulnerabilities.json file.

## Remediation
A suitable remediation should prevent malicious commands while preserving the ability to process legitimate commands. Implementations should validate inputs prior to use and ensure that malformed requests are safely rejected. When an invalid call is detected, execution should either abort the operation in a controlled manner or return an appropriate error without affecting normal execution flow.

## Attack Surface
The cFS challenge relies on a network to send commands to the flight system. This network barrier would be RF in nature if this device was on a satellite. These commands are considered valid entrypoints for vulnerabilities.

---
## CVEs

See [vulnerablities.json](vulnerabilities.json)