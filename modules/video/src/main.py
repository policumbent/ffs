import os, sys, stat
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


TEST_MODE = 0


# useful paths as strings
home_path = os.getenv("HOME")
ffs_path = f"{home_path}/ffs"
config_path = f"{ffs_path}/config"


FIFO_TO_VIDEO = "fifo_to_video"
FIFO = f"{home_path}/bob/{FIFO_TO_VIDEO}"

if os.path.exists(FIFO):
    if not stat.S_ISFIFO(os.stat(FIFO).st_mode):
        os.remove(FIFO)
        os.mkfifo(FIFO)
else:
    os.mkfifo(FIFO)


# overlay elements declaration
speed = OverlayElement("speed", unit=" kph", color=colors["blue"])
distance = OverlayElement("distance", unit=" m", color=colors["white"])
power = OverlayElement("power", unit=" W", color=colors["blue"])
heartrate = OverlayElement("heartrate", unit=" bpm", color=colors["red"])
cadence = OverlayElement("cadence", unit=" rpm", color=colors["green"])
gear = OverlayElement("gear", color=colors["white"])

test_mode = OverlayElement("test", val="TEST")

# overlay element positioning
top_left_overlay = [speed, heartrate]
top_right_overlay = [power, cadence]
bottom_middle_overlay = [gear]
bottom_right_overlay = [distance]

if TEST_MODE:
    top_middle_overlay = [test_mode]
else:
    top_middle_overlay = []


def test_mode(picam, overlay_obj):
    """
    changes every data in the overlay from 0 to 10
    :param picam: Picamera2 object
    :param overlay_obj: overlay object created in the main function
    """

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
    if type == "speed":
        speed.set_value(val)

    elif type == "distance":
        distance.set_value(val)

    elif type == "power":
        power.set_value(val)

    elif type == "heartrate":
        heartrate.set_value(val)

    elif type == "cadence":
        cadence.set_value(val)

    elif type == "gear":
        gear.set_value(val)


def fifo_mode(picam, overlay_obj):
    """
    takes FIFO_TO_VIDEO as asynchronous data source and updates the overlay
    :param picam: Picamera2 object
    :param overlay_obj: overlay object created in the main function
    """
    log.info(f"FIFO MODE STARTED")

    while True:
        try:
            with open(FIFO, 'rb', 0) as fifo:
                log.info(f"FIFO MODE - {FIFO} opened")

                for line in fifo:
                    log.info(f"FIFO MODE, READING - {line.decode()}")
                    try:    
                        sensor, value = line.decode().rstrip().split(":")
                        log.info(f"{sensor}: {value}")
                        update_values(sensor, value)
                        overlay = overlay_obj.update_overlay()
                        picam.set_overlay(overlay)
                    except Exception as e:
                        log.err(f"FIFO MODE: {e}")
        except Exception as e:
            log.err(f"FIFO MODE: {e}")


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
        fifo_mode(picam, overlay_obj)


if __name__ == '__main__':
    main()