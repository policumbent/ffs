import os, sys
from signal import pause
from time import sleep

from picamera2 import Picamera2, Preview

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs')))
from log import log


def main():
    picam = Picamera2()

    config = picam.create_preview_configuration(
        main = {'size': (1920, 1125)},
        raw = {
            'format': 'SRGGB10_CSI2P',
            'size': (1640, 1232)
        }
    )
    picam.configure(config)

    picam.start_preview(Preview.DRM, x=0, y=0, width=1024, height=600)
    picam.start()

    pause()


if __name__ == '__main__':
    main()