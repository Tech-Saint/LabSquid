
from ..client_base import linux

class ubuntu(linux):
    deviceName = "ubuntu"
    def __init__(self, device:str):
        super().__init__(device)

        self.commands = {
            "shutdown":["sudo shutdown"],
                "reboot":["sudo reboot"]
        }


    def update_info(self):
        """This updates the class instance's copy of the data base for its respective entry.
        
        Note: this SHOULD not update the main session.db.data. 
        """

        self.ip
        return "Updated"
