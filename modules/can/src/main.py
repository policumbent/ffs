import os, sys
import can, cantools

from threading import Thread
from multiprocessing import Process, Pipe 
import subprocess as sp

from .can_msg_manager import can_msg_manager

# append into path the libs folder, so that Python will find them
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs')))
from log import log


# useful paths as strings
home_path = os.getenv("HOME")
ffs_path = f"{home_path}/ffs"
config_path = f"{ffs_path}/config"


# fifo to can creation
FIFO_TO_CAN = "fifo_to_can"
FIFO_CAN = f"{home_path}/bob/{FIFO_TO_CAN}"

if os.path.exists(FIFO_CAN):
    if not stat.S_ISFIFO(os.stat(FIFO_CAN).st_mode):
        os.remove(FIFO_CAN)
        os.mkfifo(FIFO_CAN)
else:
    os.mkfifo(FIFO_CAN)

# fifo to video creation
FIFO_TO_VIDEO = "fifo_to_video"
FIFO_VID = f"{home_path}/bob/{FIFO_TO_VIDEO}"

if os.path.exists(FIFO_VID):
    if not stat.S_ISFIFO(os.stat(FIFO_VID).st_mode):
        os.remove(FIFO_VID)
        os.mkfifo(FIFO_VID)
else:
    os.mkfifo(FIFO_VID)


def can_logger():
    sp.call("./can_logger.sh")


def ant_reader(writer):
    while True:
        try:
            with open(FIFO_CAN, 'rb', 0) as fifo_can:
                for line in fifo_can:
                    try:    
                        sensor, value = line.decode().rstrip().split(":")
                        log.info(f"{sensor}: {value}")
                        if sensor in can_writers:
                            writer.send()
                    except Exception as e:
                        log.err(f"FIFO MODE (decode): {e}")
        except Exception as e:
            log.err(f"FIFO MODE: {e}")


def vid_sender(reader):
    fifo_vid = open(FIFO_VID, 'wb', 0)
    while True:
        if reader.poll():
            pass


def can_manager(reader_ant, writer_vid):
    dbc = cantools.database.load_file('./policanbent.dbc')
    bus = can.Bus(
            interface='socketcan',
            channel='can0',
            bitrate=500000,
            receive_own_messages=False
    )

    msg_handler = can_msg_manager(writer_vid)
    notifier = can.Notifier(bus, [msg_handler])

    while True:
        if reader.poll():
            pass


def main():
    thread_can_logger = Thread(target=can_logger)
    thread_can_logger.start()

    reader_ant, writer_ant = Pipe(duplex=False)
    reader_vid, writer_vid = Pipe(duplex=True)


if __name__ == '__main__':
    main()