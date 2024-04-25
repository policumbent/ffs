import os, sys

from picamera2 import Picamera2, Preview

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs')))
from log import log


def main():
    picam = Picamera2()
    picam.start_preview()


if __name__ == '__main__':
    main()