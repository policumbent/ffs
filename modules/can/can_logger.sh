#!/bin/bash

stdbuf -i0 -o0 -e0 candump -tz can0 >> $(date +"%Y-%m-%dT%H:%M:%S%z")