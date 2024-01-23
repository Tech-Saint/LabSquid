from ..client_base import __client
import re 

class network(__client):
    # Not able to test as I do not have a cisco sw.
    deviceName="cisco"
    def __init__(self, device:str):
        super().__init__(device)
        
        self.commands= {
        "update_info":["sh mac address-table | include Gi([1-9])/0/([1-9])",
                       "show int desc | in ([1-9])/0/([1-9])",
                       "sh ver"],
        "shutdown":["sudo shutdown","exit"],
        "reboot":["reload","Y"]
        }

    def update_info(self):
        """This should be called like this: session.db.update_db(Device_instances[device['DNS_name']].update_info())"""
        ## WIP for inerface gathering. 
        output_list=self.execute_cmds(self.commands["update_info"])
        sw_model_regex =r"Model Number *: (.*)"
        sw_SN_regex = r"System Serial Number *: (.*)"
        for line in output_list:
            line=line.replace((self.DNS_name+"> "),"")

            sw_model = re.findall(sw_model_regex, line)
            sw_serial = re.findall(sw_SN_regex, line)

            if len(sw_model) == 0 and len(sw_serial) == 0:
                # fall back for older switches
                sw_model_regex = r"Machine Type\.+(.*)"
                sw_SN_regex = r"Serial Number\.+(.*)"
                sw_model = re.findall(sw_model_regex, line)
                sw_serial = re.findall(sw_SN_regex, line)
            
            if len(sw_model) != 0: self.device["Model Number"] = sw_model
            if len(sw_serial) != 0: self.device["Serial Number"] = sw_model
        return "Updated"


