import os, sys
from signal import pause
from time import sleep

from picamera2 import Picamera2, Preview

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs')))
from log import log


# the following values are not the exact dimension of the screen, but,
# empirically, they are the best values we've found (up to now, at least)
MAIN_STREAM_WIDTH  = 1920
MAIN_STREAM_HEIGHT = 1125

SCREEN_WIDTH  = 1024
SCREEN_HEIGHT = 600


def main():
    picam = Picamera2()

    config = picam.create_preview_configuration(
        # main video stream parameters
        main = {'size': (MAIN_STREAM_WIDTH, MAIN_STREAM_HEIGHT)},
        # raw video stream from camera sensor (chosen with rpicam-hello)
        raw = {
            'format': 'SRGGB10_CSI2P',
            'size': (1640, 1232)
        }
    )
    picam.configure(config)

    picam.start_preview(Preview.DRM, x=0, y=0, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    picam.start()

    pause()


if __name__ == '__main__':
    main()