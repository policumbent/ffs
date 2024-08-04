import sys, os
import can, cantools

# append into path the libs folder, so that Python will find them
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs')))
from log import log

class can_msg_manager(can.Listener):
    
    def __init__(self, writer, dbc_to_sensors, dbc):
        self.writer = writer
        self.dbc_to_sensors = dbc_to_sensors
        self.dbc = dbc
        return


    def on_message_received(self, msg: can.Message) -> None:
        decoded_msg = self.dbc.decode_message(msg.arbitration_id, msg.data)
        msg_name = self.dbc.get_message_by_frame_id(msg.arbitration_id).name

        for signal in decoded_msg:
            try:
                if self.dbc_to_sensors[msg_name][signal]["sensor"] != None:
                    self.writer.send((self.dbc_to_sensors[msg_name][signal]["sensor"], decoded_msg[signal]))

                    log.info(f"CAN RX: {msg_name}, {signal}: {decoded_msg[signal]}")
            except Exception as can_dbc_err:
                log.err(f"CAN RX - DBC CONV ERROR: {can_dbc_err}")

        return