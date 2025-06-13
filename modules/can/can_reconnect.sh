#!/bin/bash

sudo ip link set can0 type can bitrate 500000 restart-ms 100
sudo ip link set up can0