import can, cantools

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
            if self.dbc_to_sensors[msg_name][signal]["sensor"] != None:
                writer.send((self.dbc_to_sensors[msg_name][signal]["sensor"], decoded_msg[signal]))

        return