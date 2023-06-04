from os import popen
from sys import platform,path 
from socket import gethostbyname
from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException, SSHDetect
import re

class _client(object):

    """
    This is the common class with that all devices share.
    Put common methods and functions in here. 
    """

    def __init__(self, device):
        self.device = device
        self.DNS_name = device ["DNS_name"]
        self.os_type= device ["device_type"]
        try: device ['netmiko_type']
        except KeyError:
            try:

                guesser = SSHDetect(
                    host=device ['ip'],
                    username = device ['username'],
                    password = device ['password'],
                    secret =  device ['password'],
                    )
                
                best_match = guesser.autodetect()
                print(best_match) # Name of the best device_type to use further
                print(guesser.potential_matches)
                device ['netmiko_type'] = best_match
            except:raise NotImplementedError
        
        self.Netmiko_settings = {
            "device_type": device ['netmiko_type'],
            "host": device ['ip'],
            "username": device ['username'],
            "password": device ['password'],
            "secret": device ['password'],
            "global_delay_factor": 3,
        }
        self.dns_query()
        self.ping_device()

    def __str__(self):
        return self.DNS_name
    
    def init_ssh(self):
        try:
            net_connect = ConnectHandler(
                **self.Netmiko_settings, timeout=20
            ) 
            net_connect.find_prompt()
            return net_connect

        except (NetMikoAuthenticationException, NetMikoTimeoutException):
            print("Could not authenticate in time to {}\nExiting...".format(self.Netmiko_settings["host"]))
        except (ValueError):
            print("""Could not enter enable mode on {}""".format(self.Netmiko_settings["host"]))
            print("Continuing...\n")

    def dynamic_method_call(self, func: str, *args, **kwargs):
        """This is kinda buggy..."""
        do = f"{func}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            output=func(*args, **kwargs)
            self.lastOutput=output

        
    
    
    def dns_query(self):
        """
        Performs an NSLOOKUP of the hostname and if it exists puts the name to final switch list.
        """
        self.DNS_exist=False
        try:
            self.DNS_exist=bool(gethostbyname(self.DNS_name))
        except:
            pass

    def ping_device(self):
        """Returns None if successful. On fail will return 1."""
        if platform == "win32": 
            ping = popen("ping -n 1 "+self.Netmiko_settings["host"])
        else: 
            ping=popen("ping -c 1 "+self.Netmiko_settings["host"])
        return_code = ping.close()
        if return_code==None: self.pingable=True
        else: self.pingable=False
        return self.pingable

    def execute_cmds(self,command_lst:list):
        """
        Submit commands to this method as a list.
        Returns a list of outputs that starts with "DNS name > "
        """
        self.net_connect=self.init_ssh()
        output_list=[]
        self.net_connect.find_prompt()
        self.net_connect.enable(pattern="password")
        for command in command_lst:
            output = self.net_connect.send_command(command).strip()
            print(self.DNS_name + "> " + output)
            output_list.append(self.DNS_name + "> " + output)
        return output_list
    
    def shutdown(self):
        ## TODO add thread to check on status of ip. 
        output_list= self.execute_cmds(self.commands["shutdown"])
        
    def reboot(self):
        ## TODO add thread to check on status of ip. 
        output_list= self.execute_cmds(self.commands["reboot"])

class linux(_client):
    
    def __init__(self, device:str):
        self.commands= {
                "update_info":[
                    "sudo dmidecode --string='processor-version'",
                    "sudo dmidecode --string='system-manufacturer'",
                    'cat /etc/*-release | grep -i "PRETTY_NAME"',
                    ],
                "shutdown":["sudo shutdown"],
                "reboot":["sudo reboot"]
                }
        _client.__init__(self,device)

    def update_info(self):
        """This updates the class instance's copy of the data base for its respective entry.
        TODO: covert the hard coded lines to regexes. 
        Note: this SHOULD not update the main session.db.data. 
        """

        output_list= self.execute_cmds(self.commands["update_info"])

        self.device["cpu"]=output_list[0].replace((self.DNS_name+"> "),"")
        self.device["mfg"]=output_list[1].replace((self.DNS_name+"> "),"")
        self.device["os_ver"]=output_list[2].replace((self.DNS_name+'> PRETTY_NAME="'),"")
        return "updated"

class win32(_client):
    
    def __init__(self, device:str):
        _client.__init__(self,device)

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

        print(f"Updating info for {self.DNS_name}")
        output_list= self.execute_cmds(self.commands["update_info"])

        self.device["cpu"]=output_list[0].replace((self.DNS_name+"> OS Name:"),"")
        self.device["mfg"]=output_list[1].replace((self.DNS_name+"> "),"")
        self.device["os_ver"]=output_list[3].replace((self.DNS_name+"> "),"")
        return "Updated"


class network(_client):
    # Not able to test as I do not have a cisco sw. 
    def __init__(self, device:str):
        _client.__init__(self,device)
        
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
        output_list= self.execute_cmds(self.commands["update_info"])
        sw_model_rgx = r"Model Number *: (.*)"
        sw_serial_rgx = r"System Serial Number *: (.*)"
        for line in output_list:
            line=line.replace((self.DNS_name+"> "),"")

            sw_model = re.findall(sw_model_rgx, line)
            sw_serial = re.findall(sw_serial_rgx, line)

            if len(sw_model) == 0 and len(sw_serial) == 0:
                # fall back for older switches
                sw_model_rgx = r"Machine Type\.+(.*)"
                sw_serial_rgx = r"Serial Number\.+(.*)"
                sw_model = re.findall(sw_model_rgx, line)
                sw_serial = re.findall(sw_serial_rgx, line)
            
            if len(sw_model) != 0: self.device["Model Number"] = sw_model
            if len(sw_serial) != 0: self.device["Serial Number"] = sw_model
        return "Updated"
