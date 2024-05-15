import can

class can_msg_manager(can.Listener):
    
    def __init__(self, writer):
        self._writer = writer
        return


    def on_message_received(self, msg: can.Message) -> None:
        pass