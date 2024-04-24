import os, sys
from time import sleep

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs')))
from log import log

def main():
    while True:
        log.err("Error")
        log.warn("Warn")
        log.info("Info")
        sleep(1)

if __name__ == '__main__':
    main()