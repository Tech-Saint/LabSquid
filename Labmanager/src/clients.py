import re
from os import popen
from sys import platform,path 
from socket import gethostbyname
from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException, SSHDetect

from .Localutils import *
from .client_base import __client

from .roles import *


def init_device_objs(device:dict) -> object:
    """Determines correct class based on device type"""
    
    match device["device_type"]:
        case "win32":
            return win32(device)
        case "linux":
            return linux(device)
        case "cisco":
            return network(device)
        case "turing":
            return turing.turing_pi2(device)


class linux(__client):
    
    def __init__(self, device:str):
        super().__init__(device)

        self.commands= {
                "update_info":[
                    "sudo dmidecode --string='processor-version'",
                    "sudo dmidecode --string='system-manufacturer'",
                    'cat /etc/*-release | grep -i "PRETTY_NAME"',
                    "sudo dmidecode -s system-product-name"
                    ],
                "shutdown":["sudo shutdown"],
                "reboot":["sudo reboot"]
                }

    def update_info(self):
        """This updates the class instance's copy of the data base for its respective entry.
        TODO: covert the hard coded lines to regexes. 
        Note: this SHOULD not update the main session.db.data. 
        """

        output_list= self.execute_cmds(self.commands["update_info"])
        if f'{self.DNS_name}>' not in output_list and type(output_list) != list:
            raise Exception("failed to connect")
        self.device["cpu"]=output_list[0].replace((self.DNS_name+"> "),"")
        self.device["mfg"]=output_list[1].replace((self.DNS_name+"> "),"")
        self.device["os_ver"]=output_list[2].replace((self.DNS_name+'> PRETTY_NAME="'),"")
        self.device["Device"]=output_list[3].replace((self.DNS_name+'> '),"")
        return "updated"

class win32(__client):
    
    def __init__(self, device:str):
        super().__init__(device)

        self.commands= {
        "update_info":[
            "wmic cpu get name",
            "wmic baseboard get manufacturer",
            'systeminfo | findstr /B /C:"OS Name" /B /C:"OS Version"',
            ],
        "update":[
            "cmd.exe",
            "wuauclt /detectnow",
            "wuauclt /updatenow"
            ],
        "shutdown":["shutdown /s /t 00"],
        "reboot":["shutdown /r /t 00"]
        }


    def update_info(self):
        """This updates the class instance's copy of the data base for its respective entry.
        
        Note: this SHOULD not update the main session.db.data. 
        """

        log_event(f"Updating info for {self.DNS_name}")
        output_list= self.execute_cmds(self.commands["update_info"])

        self.device["cpu"]=output_list[0].replace((self.DNS_name+"> OS Name:"),"")
        self.device["mfg"]=output_list[1].replace((self.DNS_name+"> "),"")
        self.device["os_ver"]=output_list[3].replace((self.DNS_name+"> "),"")
        return "Updated"


class network(__client):
    # Not able to test as I do not have a cisco sw. 
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


