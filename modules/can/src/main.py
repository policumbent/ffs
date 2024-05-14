import os, sys
import can, cantools

import multiprocessing as mp
import subprocess as sp

from threading import Thread


def can_logger():
    sp.call("./can_logger.sh")


def main():
    thread_can_logger = Thread(target=can_logger)
    thread_can_logger.start()


if __name__ == '__main__':
    main()