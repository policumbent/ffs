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
from pipe import Pipe


TEST_MODE = 0


# useful paths as strings
home_path = os.getenv("HOME")
ffs_path = f"{home_path}/ffs"
config_path = f"{ffs_path}/config"

FIFO_TO_VIDEO = "fifo_to_video"


# overlay elements declaration
speed = OverlayElement("ant/speed", unit=" kph", color=colors["blue"])
distance = OverlayElement("ant/distance", unit=" m", color=colors["white"])
power = OverlayElement("ant/power", unit=" W", color=colors["blue"])
heartrate = OverlayElement("ant/heartrate", unit=" bpm", color=colors["red"])
cadence = OverlayElement("ant/cadence", unit=" rpm", color=colors["green"])
gear = OverlayElement("gb/gear", color=colors["white"])

test_mode = OverlayElement("test", val="TEST")

# overlay element positioning
top_left_overlay = [speed, heartrate]
top_right_overlay = [power, cadence]
bottom_middle_overlay = [gear]
bottom_right_overlay = [distance]

if TEST_MODE:
    top_middle_overlay = [test_mode]


def test_mode(picam, overlay_obj):
    while True:
        for i in range(11):
            speed.set_value(i)
            distance.set_value(i)
            power.set_value(i)
            heartrate.set_value(i)
            cadence.set_value(i)
            gear.set_value(i)
            overlay = overlay_obj.update_overlay()
            picam.set_overlay(overlay)
            #log.info("VIDEO - Overlay in progress")
            sleep(1)


def update_values(type, val):
    if type == "ant/speed":
        speed.set_value(val)

    elif type == "ant/distance":
        distance.set_value(val)

    elif type == "ant/power":
        power.set_value(val)

    elif type == "ant/heartrate":
        heartrate.set_value(val)

    elif type == "ant/cadence":
        cadence.set_value(val)

    elif type == "gb/gear":
        gear.set_value(val)


def fifo_mode(pipe, picam, overlay_obj):
    while True:
        try:
            if pipe.read():
                for rd in pipe.get_data().rstrip().split("-"):
                    if rd != "":
                        sensor, value = rd.split(":")
                        update_values(sensor, value)
                        overlay_obj.update_overlay()
        except Exception as e:
            log.err(f"FIFO: {e}")


def json_to_dict(path: str):
    res = dict()
    try: 
        with open(path) as file:
            try:
                res = json.load(file)
            except Exception as json_err:
                log.err(f"VIDEO - JSON: {json_err}")

    except Exception as file_err:
        log.err(f"VIDEO - FILE: {file_err}")

    return res


def main():
    video_conf = json_to_dict(f"{config_path}/video.json")
    camera_conf = json_to_dict(f"{config_path}/camera.json")

    cam_name = video_conf["camera_name"]

    picam = Picamera2()

    preview_config = picam.create_preview_configuration(
        # main video stream parameters
        main = {'size': (
            camera_conf[cam_name]["main_stream"]["width"],
            camera_conf[cam_name]["main_stream"]["height"]
        )},

        # raw video stream from camera sensor (chosen with rpicam-hello)
        raw = {
            'format': camera_conf[cam_name]["raw_stream"]["format"],
            'size': (
                camera_conf[cam_name]["raw_stream"]["size"]["width"],
                camera_conf[cam_name]["raw_stream"]["size"]["height"]
            )
        },

        # transform parameters
        transform = libcamera.Transform(
            hflip=video_conf["hflip"],
            vflip=video_conf["vflip"]
        )
    )
    picam.configure(preview_config)

    picam.start_preview(
        Preview.DRM,
        x=0, y=0,
        width=video_conf["screen"]["width"],
        height=video_conf["screen"]["height"]
    )
    picam.start()

    # overlay declaration
    overlay_obj = Overlay(
        video_conf["screen"]["width"],
        video_conf["screen"]["height"],
        thickness=video_conf["overlay"]["thickness"],
        rotation=video_conf["overlay"]["rotation"],
        top_left=top_left_overlay,
        top_middle=top_middle_overlay,
        top_right=top_right_overlay,
        bottom_middle=bottom_middle_overlay,
        bottom_right=bottom_right_overlay
    )

    if TEST_MODE:
        test_mode(picam, overlay_obj)
    else:
        # hybrid solution with pipe still in bob
        pipe = Pipe(f"{home_path}/bob/{FIFO_TO_VIDEO}", "r")
        fifo_mode(pipe, picam, overlay_obj)


if __name__ == '__main__':
    main()