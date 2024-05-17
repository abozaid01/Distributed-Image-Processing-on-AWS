#!/bin/bash

# Update and install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-opencv libopencv-dev mpich

# Install mpi4py
pip3 install mpi4py
