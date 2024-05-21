import os, sys, stat
import can, cantools

import json

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

can_writers = ["power", "cadence", "ant_speed", "ant_distance", "heartrate"]

if os.path.exists(FIFO_VID):
    if not stat.S_ISFIFO(os.stat(FIFO_VID).st_mode):
        os.remove(FIFO_VID)
        os.mkfifo(FIFO_VID)
else:
    os.mkfifo(FIFO_VID)


def can_logger():
    sp.call("./can_logger.sh")


def json_to_dict(path: str):
    res = dict()
    try: 
        with open(path) as file:
            try:
                res = json.load(file)
            except Exception as json_err:
                log.err(f"CAN (json_to_dict) - JSON: {json_err}")

    except Exception as file_err:
        log.err(f"CAN (json_to_dict) - FILE: {file_err}")

    return res


def ant_reader(writer):
    while True:
        try:
            with open(FIFO_CAN, 'rb', 0) as fifo_can:
                for line in fifo_can:
                    try:    
                        sensor, value = line.decode().rstrip().split(":")
                        log.info(f"{sensor}: {value}")

                        if sensor in can_writers:
                            writer.send((sensor, value))

                    except Exception as e:
                        log.err(f"ANT READER (decode): {e}")

        except Exception as e:
            log.err(f"ANT READER: {e}")

    return


def vid_writer(reader):
    fifo_vid = open(FIFO_VID, 'wb', 0)
    while True:
        if reader.poll():
            data = reader.recv()

            fifo_vid.write(f"{data[0]}:{data[1]}")


def can_manager(reader_ant, writer_vid):
    dbc = cantools.database.load_file('./policanbent.dbc')
    bus = can.Bus(
            interface='socketcan',
            channel='can0',
            bitrate=500000,
            receive_own_messages=False
    )

    sensors_to_dbc = json_to_dict(f"{config_path}/sensors_to_dbc.json")
    dbc_to_sensors = json_to_dict(f"{config_path}/dbc_to_sensors.json")
    
    msg_handler = can_msg_manager(writer_vid, dbc_to_sensors, dbc)
    notifier = can.Notifier(bus, [msg_handler])

    while True:
        if reader_ant.poll():
            data = reader.recv()    # data encoded as a two elements tuple in
                                    # ant_reader:
                                    #  - data[0] -> sensor
                                    #  - data[1] -> value

            id_name = sensors_to_dbc[data[0]][0]
            sig_name = sensors_to_dbc[data[0]][1]
            pl = dbc.encode_message(id_name, {sig_name: data[1]})
            id_frame = dbc.get_message_by_name[id_name].frame_id
            can_frame = can.Message(arbitration_id=id_frame, data=pl)

    return


def main():
    thread_can_logger = Thread(target=can_logger)
    thread_can_logger.start()

    reader_ant, writer_ant = Pipe(duplex=False)
    reader_vid, writer_vid = Pipe(duplex=False)

    can_manager_proc = Process(target=can_manager, args=(reader_ant, writer_vid))
    vid_writer_proc  = Process(target=vid_writer, args=(reader_vid))
    ant_reader_proc  = Process(target=ant_reader, args=(writer_ant))

    can_manager_proc.start()
    vid_writer_proc.start()
    ant_reader_proc.start()

    can_manager_proc.join()
    vid_writer_proc.join()
    ant_reader_proc.join()


if __name__ == '__main__':
    main()