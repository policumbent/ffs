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
    """
    reads the ant-can FIFO and writes the given messages on the internal ant Pipe that sends the messages that have to
    be sent on the CAN Bus
    :param writer: writer of Pipe that sends FIFO-read messages to the can_msg_manager function to send them on the CAN
                   Bus
    """
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
    """
    reads the internal video Pipe and then send the read messages on the FIFO directed to the video module
    :param reader: reader of the video Pipe, read data are then sent to the video FIFO
    """
    fifo_vid = open(FIFO_VID, 'wb', 0)
    log.info(f"VID WRITER - {FIFO_VID} opened")

    while True:
        if reader.poll():
            data = reader.recv()

            payload = f"{data[0]}:{data[1]}\n"
            log.info(f"VID WRITER: sending data - {data[0]}: {data[1]}")

            try:
                fifo_vid.write(payload.encode())
            except Exception as e:
                log.err(f"VID WRITER: {e}")


def can_manager(bus, reader_ant, writer_vid):
    """
    manages CAN Bus communication with other boards, both reading and writing on the bus
    :param reader_ant: reader of the ant Pipe, read data are then sent to can_msg_manager to send them on the CAN Bus
    :param writer_vid: writer of the video Pipe, used to send the CAN-received data to the process managing the video
                       FIFO
    """
    dbc = cantools.database.load_file('./policanbent.dbc')
    

    sensors_to_dbc = json_to_dict(f"{config_path}/sensors_to_dbc.json")
    dbc_to_sensors = json_to_dict(f"{config_path}/dbc_to_sensors.json")
    
    msg_handler = can_msg_manager(writer_vid, dbc_to_sensors, dbc)
    notifier = can.Notifier(bus, [msg_handler])

    while True:
        if reader_ant.poll():
            data = reader_ant.recv()    # data encoded as a two elements tuple in
                                        # ant_reader:
                                        #  - data[0] -> sensor
                                        #  - data[1] -> value

            log.info(f"ANT READ: {data[0]}:{data[1]}\n")

            id_name = sensors_to_dbc[data[0]][0]
            sig_name = sensors_to_dbc[data[0]][1]
            pl = dbc.encode_message(id_name, {sig_name: float(data[1])})
            id_frame = dbc.get_message_by_name(id_name).frame_id
            can_frame = can.Message(arbitration_id=id_frame, is_extended_id=False, data=pl)

            bus.send(can_frame, timeout=0.2)

    return


def main():
    sp.call("./can_reconnect.sh")

    flg = 0
    while flg == 0:
        try:
            bus = can.Bus(
                    interface='socketcan',
                    channel='can0',
                    bitrate=500000,
                    receive_own_messages=False
            )

            flg = 1
        except:
            log.err(f"CAN MANAGER: no CAN connection, retrying...")
            sp.call("./can_reconnect.sh")
        

    thread_can_logger = Thread(target=can_logger)
    thread_can_logger.start()

    reader_ant, writer_ant = Pipe(duplex=False)
    reader_vid, writer_vid = Pipe(duplex=False)

    can_manager_proc = Process(target=can_manager, args=(bus, reader_ant, writer_vid,))
    vid_writer_proc  = Process(target=vid_writer, args=(reader_vid,))
    ant_reader_proc  = Process(target=ant_reader, args=(writer_ant,))

    can_manager_proc.start()
    vid_writer_proc.start()
    ant_reader_proc.start()

    can_manager_proc.join()
    vid_writer_proc.join()
    ant_reader_proc.join()


if __name__ == '__main__':
    main()
