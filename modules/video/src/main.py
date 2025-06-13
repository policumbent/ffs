import os, sys, stat
from signal import pause
from time import sleep, time
from threading import Thread

import libcamera
from picamera2 import Picamera2, Preview

from .overlay import OverlayElement, Overlay, colors

import numpy as np

import json

# append into path the libs folder, so that Python will find them
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs')))
from log import log


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
speed = OverlayElement("speed", unit=" kph", color=colors["white"])
distance = OverlayElement("distance", unit=" m", color=colors["white"])
power = OverlayElement("power", unit=" W", color=colors["white"])
heartrate = OverlayElement("heartrate", unit=" bpm", color=colors["white"])
cadence = OverlayElement("cadence", unit=" rpm", color=colors["white"])
gear = OverlayElement("gear", color=colors["white"])

test_overlay = OverlayElement("test", val="TEST", color=colors["white"])

time_elapsed = OverlayElement("time", color=colors["white"])


def generate_overlay_positioning(MODE):
    if MODE == "ENDURANCE_MODE":
        top_left_overlay = [time_elapsed, speed, distance]
        top_right_overlay = [heartrate, power, cadence]
        bottom_middle_overlay = [gear]
        bottom_right_overlay = []
        bottom_left_overlay = []
    else:
        top_left_overlay = [speed, distance]
        top_right_overlay = [heartrate, power, cadence]
        bottom_middle_overlay = [gear]
        bottom_right_overlay = []
        bottom_left_overlay = []

    if MODE == "TEST_MODE":
        top_middle_overlay = [test_overlay]
    else:
        top_middle_overlay = []

    return {
        "top_left_overlay": top_left_overlay,
        "top_middle_overlay": top_middle_overlay,
        "top_right_overlay": top_right_overlay,
        "bottom_left_overlay": bottom_left_overlay,
        "bottom_middle_overlay": bottom_middle_overlay,
        "bottom_right_overlay": bottom_right_overlay
    }


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

    elif type == "time":
        time_elapsed.set_time(val)


def run_mode(picam, overlay_obj):
    """
    takes FIFO_TO_VIDEO as asynchronous data source and updates the overlay
    :param picam: Picamera2 object
    :param overlay_obj: overlay object created in the main function
    """
    log.info(f"RUN MODE STARTED")

    while True:
        try:
            with open(FIFO, 'rb', 0) as fifo:
                log.info(f"RUN MODE - {FIFO} opened")

                for line in fifo:
                    log.info(f"RUN MODE, READING - {line.decode()}")
                    try:    
                        sensor, value = line.decode().rstrip().split(":")
                        log.info(f"{sensor}: {value}")
                        update_values(sensor, value)
                        overlay = overlay_obj.update_overlay()
                        picam.set_overlay(overlay)
                    except Exception as e:
                        log.err(f"RUN MODE: {e}")
        except Exception as e:
            log.err(f"RUN MODE: {e}")


def time_sending(picam, overlay_obj):
    start_time = time()

    while True:
        actual_time = time() - start_time
        update_values("time", actual_time)

        log.info(f"TIME SENDING: {actual_time}")

        overlay = overlay_obj.update_overlay()
        picam.set_overlay(overlay)
        sleep(0.5)


def endurance_mode(picam, overlay_obj):
    """
    takes FIFO_TO_VIDEO as asynchronous data source and updates the overlay,
    with time elapsed
    :param picam: Picamera2 object
    :param overlay_obj: overlay object created in the main function
    """
    log.info(f"ENDURANCE MODE STARTED")

    thread_time_sending = Thread(target=time_sending, args=(picam, overlay_obj,))
    thread_time_sending.start()

    while True:
        try:
            with open(FIFO, 'rb', 0) as fifo:
                log.info(f"ENDURANCE MODE - {FIFO} opened")

                for line in fifo:
                    log.info(f"ENDURANCE MODE, READING - {line.decode()}")
                    try:    
                        sensor, value = line.decode().rstrip().split(":")
                        log.info(f"{sensor}: {value}")
                        update_values(sensor, value)
                        overlay = overlay_obj.update_overlay()
                        picam.set_overlay(overlay)
                    except Exception as e:
                        log.err(f"ENDURANCE MODE: {e}")
        except Exception as e:
            log.err(f"ENDURANCE MODE: {e}")
            

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
    mode_conf = json_to_dict(f"{config_path}/mode.json")
    video_conf = json_to_dict(f"{config_path}/video.json")
    camera_conf = json_to_dict(f"{config_path}/camera.json")

    MODE = mode_conf["mode"]

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

    sleep(1)

    overlay_pos = generate_overlay_positioning(MODE)

    # overlay declaration
    overlay_obj = Overlay(
        video_conf["screen"]["width"],
        video_conf["screen"]["height"],
        thickness=video_conf["overlay"]["thickness"],
        rotation=video_conf["overlay"]["rotation"],
        top_left=overlay_pos["top_left_overlay"],
        top_middle=overlay_pos["top_middle_overlay"],
        top_right=overlay_pos["top_right_overlay"],
        bottom_left=overlay_pos["bottom_left_overlay"],
        bottom_middle=overlay_pos["bottom_middle_overlay"],
        bottom_right=overlay_pos["bottom_right_overlay"]
    )

    if MODE == "TEST_MODE":
        test_mode(picam, overlay_obj)
    elif MODE == "RUN_MODE":
        # hybrid solution with pipe still in bob
        run_mode(picam, overlay_obj)
    elif MODE == "ENDURANCE_MODE":
        endurance_mode(picam, overlay_obj)


if __name__ == '__main__':
    main()