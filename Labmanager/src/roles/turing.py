from ..client_base import __client


class turing_pi2(__client):
    deviceName = "turing"
    def __init__(self, device:str):
        super().__init__(device)

        self.commands= {
            
            "shutdown":["sudo shutdown"],
                "reboot":["sudo reboot"]
        }


    def update_info(self):
        """This updates the class instance's copy of the data base for its respective entry.
        
        Note: this SHOULD not update the main session.db.data. 
        """

        self.ip
        return "Updated"
