import os, sys
from signal import pause
from time import sleep

import libcamera
from picamera2 import Picamera2, Preview

from .overlay import OverlayElement, Overlay, colors

import numpy as np

import json

# append into path the libs folder, so that Python will find them
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs')))
from log import log


home_path = os.getenv("HOME")
ffs_path = f"{home_path}/ffs"
config_path = f"{ffs_path}/config"


def main():
    config = None
    try: 
        with open(f"{config_path}/video.json") as video_config_file:
            try:
                config = json.load(video_config_file)

            except Exception as json_err:
                log.err(f"VIDEO - JSON: {json_err}")

    except Exception as file_err:
        log.err(f"VIDEO - FILE: {file_err}")

    picam = Picamera2()

    preview_config = picam.create_preview_configuration(
        # main video stream parameters
        main = {'size': (
            config["main_stream"]["width"],
            config["main_stream"]["height"]
        )},

        # raw video stream from camera sensor (chosen with rpicam-hello)
        raw = {
            'format': config["raw_stream"]["format"],
            'size': (
                config["raw_stream"]["size"]["width"],
                config["raw_stream"]["size"]["height"]
            )
        },

        # transform parameters
        transform = libcamera.Transform(
            hflip=config["hflip"],
            vflip=config["vflip"]
        )
    )
    picam.configure(preview_config)

    picam.start_preview(
        Preview.DRM,
        x=0, y=0,
        width=config["screen"]["width"],
        height=config["screen"]["height"]
    )
    picam.start()

    speed = OverlayElement("ant/speed", unit="kph", color=colors["blue"])
    distance = OverlayElement("ant/distance", unit="m", color=colors["white"])
    power = OverlayElement("ant/power", unit="W", color=colors["blue"])
    heartrate = OverlayElement("ant/heartrate", unit="bpm", color=colors["red"])
    cadence = OverlayElement("ant/cadence", unit="rpm", color=colors["green"])
    gear = OverlayElement("gb/gear", color=colors["white"])

    top_left_overlay = [speed, heartrate]
    top_right_overlay = [power, cadence]
    bottom_middle_overlay = [gear]
    bottom_right_overlay = [distance]

    overlay_obj = Overlay(
        config["screen"]["width"],
        config["screen"]["height"],
        top_left=top_left_overlay,
        top_right=top_right_overlay,
        bottom_middle=bottom_middle_overlay,
        bottom_right=bottom_right_overlay
    )

    pause()


if __name__ == '__main__':
    main()