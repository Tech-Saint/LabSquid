from os import popen
from sys import platform,path 
from socket import gethostbyname
from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException, SSHDetect

from .Localutils import *

class __client:

    """
    This is the common class with that all devices share.\n
    Put common methods and functions in here.\n
    """

    def __init__(self, device:dict):
        
        self.device = device
        self.DNS_name = device ["DNS_name"]
        self.os_type = device ["device_type"]
        log_event(f"initialized {self.DNS_name}")
        self.busy = False #spin lock for app
        try: device ['netmiko_type']

        except KeyError:
            log_event(f"{self.DNS_name}> Netmiko Type does not exist, trying to guess it now...")
            try:

                guesser = SSHDetect(
                    device_type='autodetect',
                    host=device ['ip'],
                    username = device ['username'],
                    password = device ['password'],
                    secret =  device ['password'],
                    )
                
                best_match = guesser.autodetect()
                log_event(best_match) # Name of the best device_type to use further
                device ['netmiko_type'] = best_match
                log_event(f"{self.DNS_name}> Successfully guessed the SSH format.")

            except Exception as e:
                log_event(f"{self.DNS_name}> Failed to guess the SSH format due to error:{e}")
        try:
            self.Netmiko_settings = {
                "device_type": device ['netmiko_type'],
                "host": device ['ip'],
                "username": device ['username'],
                "password": device ['password'],
                "secret": device ['password'],
                "global_delay_factor": 3,
            }
        except Exception as e:
            log_event(f"{self.DNS_name}> {e}")
        self.dns_query()
        self.ping()

    def __status__(self) -> dict:
        """Returns base status"""
        status_dict={}
        status_dict["ip"]=self.device["ip"]
        status_dict["id"]=self.device["_id"]
        status_dict["Os_type"]=self.os_type
        status_dict["pingable"]=self.pingable
        status_dict["Roles"]="Not implemented"

        return status_dict
    
    def __str__(self):
        return self.DNS_name
    
    def __info__(self) -> dict:

        ATRLIST = [attr for attr in vars(self) if not callable(getattr(self, attr)) and not attr.startswith("__") and attr not in ["device","Netmiko_settings",'net_connect'] ]
        _={}
        for key in ATRLIST:
            _[key]=(getattr(self,key))
        return _
    
    def __methods__(self):
        """returns a list of methods"""
        ATRLIST = [attr for attr in dir(self) if callable(getattr(self, attr)) and not attr.startswith("_") and attr not in ["device","execute_cmds","Netmiko_settings"] ]
        _={}
        for key in ATRLIST:
            _[key]=(getattr(self,key))
        return _
    
    def __init_ssh(self):
        self.busy = True
        try:
            net_connect = ConnectHandler(
                **self.Netmiko_settings, timeout=20
            ) 
            net_connect.find_prompt()
            return net_connect
        
        except AttributeError:
            log_event(f"{self.DNS_name}> Netmiko Type does not exist, trying to guess it now...")
            try:

                guesser = SSHDetect(
                    device_type='autodetect',
                    host= self.device ['ip'],
                    username = self.device ['username'],
                    password = self.device ['password'],
                    secret =  self.device ['password'],
                    )
                
                best_match = guesser.autodetect()
                log_event(best_match) # Name of the best device_type to use further
                self.device ['netmiko_type'] = best_match
                log_event(f"{self.DNS_name}> Successfully guessed the SSH format.")
                net_connect = ConnectHandler(
                    **self.Netmiko_settings, timeout=20
                ) 
                net_connect.find_prompt()
                
                return net_connect

            except Exception as e:
                log_event(f"{self.DNS_name}> Failed to guess the SSH format due to error:{e}")
                return e.args

        except (NetMikoAuthenticationException, NetMikoTimeoutException):
            log_event("Could not authenticate in time to {}\nExiting...".format(self.Netmiko_settings["host"]))
            self.busy=False
        except (ValueError):
            log_event("""Could not enter enable mode on {}""".format(self.Netmiko_settings["host"]))
            self.busy=False


    def __dynamic_method_call(self, func: str, *args, **kwargs):
        """Prob really insecure. Should look into turning this into a secure method call.\n
        Added so I can just list out strings of available methods for each class and \n
        then from the front end select them to call the function.\n

        :params *args - args for the method being called
        :params **kwargs - more args to pass through the function call. 
        """

        do = f"{func}"
        log_event(f"Trying to call {func} on {self.DNS_name}")
        if hasattr(self, do) and callable(func := getattr(self, do)):
            output=func(*args, **kwargs)
            self.lastOutput=output
            return output
        
    
    def dns_query(self):
        """
        Performs an NSLOOKUP of the hostname and if it exists puts the name to final switch list.
        """
        self.DNS_exist=False
        try:
            ip=gethostbyname(self.DNS_name)
            
            if ip!=self.device ['ip'] and ip != "":
                self.device['ip']=ip
            self.DNS_exist=bool(ip)
        except:
            log_event(f"failed to get DNS name{self.DNS_name}")

    def ping(self):
        """Returns None if successful. On fail will return 1."""
        if platform == "win32": 
            ping = popen("ping -n 1 "+self.device["ip"])
            output = ping.read()
            ping.close()
            if "Received = 1" in output:
                self.pingable=True
            else: self.pingable=False
            return self.pingable
        else: 
            ping = popen("ping -c 1 "+self.device["ip"])
            output = ping.read()
            ping.close()
            if "1 received" in output:
                self.pingable=True
            else: self.pingable=False
            return self.pingable

    def execute_cmds(self,command_lst:list) -> list:
        """
        Submit commands to this method as a list.
        Returns a list of outputs that starts with "DNS name > "
        """
        self.busy=True
        self.net_connect=self.__init_ssh()
        output_list=[]
        if type(self.net_connect) == tuple: return self.net_connect[0]
        self.net_connect.find_prompt()
        self.net_connect.enable(pattern="password")
        for command in command_lst:
            output = self.net_connect.send_command(command).strip()
            log_event(f"{self.DNS_name} > {output}")
            output_list.append(self.DNS_name + "> " + output)
        self.busy=False
        self.net_connect.disconnect()
        return output_list
    
    def shutdown(self):
        ## TODO add thread to check on status of ip. 
        output_list= self.execute_cmds(self.commands["shutdown"])
        
    def reboot(self):
        ## TODO add thread to check on status of ip. 
        output_list= self.execute_cmds(self.commands["reboot"])
        
        
        
        

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
