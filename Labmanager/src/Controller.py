import json, os
from concurrent.futures import ThreadPoolExecutor , as_completed
from .db.database_interface import  _Database
from .clients import logging, log_event, build_device_init_dict

from datetime import datetime,timezone,timedelta

import math, cpuinfo, socket, uuid, platform,time, re


output_list=[]

class Controller_unit():
    """Orchestrates and holds info to give back to each device instance."""
    def __init__(self):
        self.last_run_command={}
        self.__init_time=datetime.now(timezone.utc).timestamp()
        #improves speed of going back to the home page significantly 
        with ThreadPoolExecutor() as e:
            self.cpuinfo = e.submit(cpuinfo.get_cpu_info)
            self.IpAddress = e.submit(socket.gethostbyname,socket.gethostname())
            e.shutdown(False)

        self.path_of_tool = os.path.join(os.path.dirname(__file__))
        self.readappconfig()
        self.file_setup()
        self.deviceInitDict = build_device_init_dict()
        

    def settings(self)->dict:
        settings={}
        settings["Logging Level"] = self.logging
        settings["Ping devices every N mins"] = f"{self.Ping_Cooldown}"

        return settings
    
    def __info__(self) -> dict:

        ATRLIST = [attr for attr in vars(self) if not callable(getattr(self, attr)) and not attr.startswith("__") and attr not in ["settings", "last_run_command", "DeviceInstances", "db", "Itemdb"] ]
        _={}
        for key in ATRLIST:
            _[key]=(getattr(self,key))
        _["Number of Devices"]=len(self.DeviceInstances)
        return _
    
    def uptime(self) -> str:
        """Returns the run time of the app"""
        return str(timedelta(seconds=math.ceil((datetime.now(timezone.utc).timestamp()-self.__init_time))))
    
    def setLogging(self, level:str):

        logging.getLogger().setLevel(level)        
        self.logging=level

    def readappconfig(self):
        self.path_of_tool, filename = os.path.split(os.path.realpath(__file__))
        with open(os.path.join(self.path_of_tool,"Config.cfg")) as app_config_file:
            app_config=app_config_file.readlines()
        regex = re.compile(r'(.*)=(.*)')
        for i in app_config:
            # This is a really dumb way of skipping over comments in a cfg file.
            # Uses a regex to find matching configs. 
            try: _=re.findall(regex,i)[0]
            except IndexError: continue
            if len(_) != 2: continue
            if "Ping Every N Mins" in _[0] :
                self.Ping_Cooldown = int(_[1])
            elif "HostBatt" in _[0]:
                if "True" in _[1]:
                    self.Host_Batt_check=True
                    #self.Batt_check = Batt_check
                    #self.Batt_check(self)
                else: 
                    self.Host_Batt_check=False
            elif "Logging" in _[0]:
                if "INFO" in _[1]:
                    logging.basicConfig(filename=os.path.join(self.path_of_tool,'log.txt'), level=logging.INFO)
                    logging.info("Logging set to INFO")
                    self.logging = _[1]
                elif "DEBUG" in _[1]:
                    logging.basicConfig(filename=os.path.join(self.path_of_tool,'log.txt'), level=logging.DEBUG)
                    logging.info("Logging set to DEBUG")
                    self.logging = _[1]
                else:
                    logging.basicConfig(filename=os.path.join(self.path_of_tool,'log.txt'), level=logging.CRITICAL)
                    logging.info("Logging set to CRITICAL")
                    self.logging = "CRITICAL" 
            else:
                pass
        self.app_config=app_config

    def host_info(self) -> dict:
        uname = platform.uname()
        host= {
            "System" : uname.system,
            "Node Name" : uname.node,
            "Release" : uname.release,
            "Processor" : self.cpuinfo.result()['brand_raw'],
            "Ip-address" : self.IpAddress.result(),
            "Mac_Address" : ':'.join(re.findall('..', '%012x' % uuid.getnode()))

        }
        return host

    def file_setup(self):
        if platform=="win32":
            self.username =os.getenv("username")
            self.path_of_bin = os.path.dirname(os.path.realpath(__file__))
            self.path_of_db = self.path_of_bin +"\\db\\"
        else:
            self.username =os.getenv("USER")
            self.path_of_bin = os.path.dirname(os.path.realpath(__file__))
            self.path_of_db = self.path_of_bin + "/db/"
            
        self.db = _Database()
        self.Tempdb = self.db.__repr__()

    
    def update_db(self, DeviceInstances, dev_list:list=None):
        if dev_list == None: dev_list= list(DeviceInstances.keys())
        
        for i in dev_list:
            self.db.update_db(DeviceInstances[i].device)

        
    def UpdateSettings(self, RequestDict:dict):
        result=[]
        for I in RequestDict.keys():
            if I == "Logging":
                try:
                    self.setLogging(RequestDict[I])
                except Exception as e:
                        log_event(f"Failed to write {RequestDict[I]} to {I} due to {e}")
                        result.append(f"Failed to set {RequestDict[I]} to {I} due to {e}")
            elif I == "Ping devices every N mins":
                if RequestDict[I] == '':
                    continue
                try:
                    temp_val=float(RequestDict[I])
                    
                    self.Ping_Cooldown=temp_val
                except Exception as e:
                    log_event(f"Failed to write {RequestDict[I]} to CooldownTimer due to {e}")
                    result.append(f"Failed to set {RequestDict[I]} to CooldownTimer due to {e}") 
            else:
                pass
        if result==[]:
            return "Updated settings"
        return result
    
    def Action_thread(self):
        while True==True:
            _thread=ThreadPoolExecutor()
            _thread.submit(self.command('ping'))
            _thread.submit(self.command('dns_query'))
            if self.Host_Batt_check == True:
                _thread.submit(self.Batt_check(self))
            _thread.shutdown(False)
            time.sleep(int(self.Ping_Cooldown)*60)

    def command(self,instruction:str, devices:list=None) ->str:
        """pass None to dev list to do all instances"""
        if devices == None: devices= list(self.DeviceInstances.keys())
        elif type(devices) != list:
            devices=[devices]
        for index,value in enumerate(devices):
            if type(value) == str:
                devices[index]=self.DeviceInstances[value]
        
        results = []
        jobs=[]
        with ThreadPoolExecutor(8) as executor:
            for i in devices:
                self.last_run_command[i]=[instruction,datetime.now(timezone.utc)]
                task = executor.submit(i._client__dynamic_method_call,instruction)
                jobs.append(task)
            for entry in jobs:  
                result = entry.result(timeout=60)
                results.append(result)

        if instruction == 'update_info':
            self.update_db(self.DeviceInstances)
        return results
    
    def init_device_objs(self,device:dict) -> object:
        """Determines correct class based on device type"""
        try: 
            deviceClass = self.deviceInitDict[device["device_type"]]
            return deviceClass(device)
        except KeyError:
            log_event(f"Failed to match a device class to the recorded device {device}")
