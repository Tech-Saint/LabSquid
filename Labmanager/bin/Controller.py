import json, os
from concurrent.futures import ThreadPoolExecutor , as_completed
from .db.database_interface import  _Database
from .clients import *
from datetime import datetime,timezone,timedelta

import math, cpuinfo, socket, uuid, platform,psutil,time

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

        self.path_of_tool = path[0]
        self.readappconfig()
        self.file_setup()

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
        path, filename = os.path.split(os.path.realpath(__file__))
        with open(os.path.join(path,"Config.cfg")) as app_config_file:
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
            elif "Logging" in _[0]:
                if "INFO" in _[1]:
                    logging.basicConfig(filename='log.txt', level=logging.INFO)
                    logging.info("Logging set to INFO")
                    self.logging = _[1]
                elif "DEBUG" in _[1]:
                    logging.basicConfig(filename='log.txt', level=logging.DEBUG)
                    logging.info("Logging set to DEBUG")
                    self.logging = _[1]
                else:
                    logging.basicConfig(filename='log.txt', level=logging.CRITICAL)
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
            
        self.refresh_db()
        self.db= _Database()
        self.Tempdb = self.db.__repr__()

    def refresh_db(self):
        # set aside as I plan to update and refresh db alot.
        with open(self.path_of_db+"device_db.json", "r" ) as db_temp:
            self.device_info = json.load(db_temp)
            db_temp.close()
    
    def update_db(self, DeviceInstances, dev_list:list=None):
        if dev_list == None: dev_list= list(DeviceInstances.keys())
        
        for i in dev_list:
            self.db.update_db(DeviceInstances[i].device)
        self.db.save_db()
        
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
            _thread.shutdown(False)
            time.sleep(int(self.Ping_Cooldown)*60)

    ## testing 

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
        return results
"""    
    def pingThread(self):

        try:
            for key in self.Cooldown_tag.keys():
                print(DeviceInstances.[key])
                if (datetime.now(timezone.utc).timestamp() >= ((self.Ping_Cooldown*60) + DeviceInstances.[key])):
                    self.Cooldown_tag.pop(key)
        except Exception as e:
            pass
            log_event(f"Expected Error: {e} Trying again later...", printout=True)

    
    def start_ping_thread(self):
        _threadPool=ThreadPoolExecutor(max_workers=1)
        ping_future=_threadPool.submit(self.pingThread)
        _threadPool.shutdown(False)
"""
"""  
def sort_device_db(data,db):
    ip_regex=r"(?:[\d]{1,3})"
    db_len=len(data[db])

    for i in range(db_len):
        # prep for RADIX sort
        ip_byte_List= re.findall(ip_regex, data[db][i]["ip"])
        # Check if the bytes are valid in the IP address. 
        highest_value=max([int(i) for i in ip_byte_List])
        if highest_value > 254:
            Valid=False
            DNS_name=data[db][i]['DNS_name']
            while Valid != True:
                "The IP for {DNS_name} is invalid, \nPlease type a correct number below")
                updated_val=input()
                Valid=bool(int(max(re.findall(ip_regex, data[db][i]["ip"])))> 254)
                data[db][i]["ip"]=updated_val
        data[db][i]["sort_temp"]=int(''.join([_.zfill(3) for _ in ip_byte_List])) #adds Zfills to buffer

    data[db] = sorted(data[db], key=lambda d: d['ip']) # sorts for *hopefully* fast reading later. 
    for i in range(len(data[db])):
        data[db][i]["id"]=i
        try:
            highest_value=max([int(i) for i in re.findall(ip_regex, data[db][i]["ip"])])
            if highest_value > 254:
                Valid=False
                while Valid != True:
                    "The IP for {'DNS_name'} is invalid, \nPlease type a correct number below")
                    updated_val=input()
                    Valid=bool(int(max(re.findall(ip_regex, data[db][i]["ip"])))> 254)
        except KeyError:pass
    data[db] = sorted(data[db], key=lambda d: d['ip']) # sorts for *hopefully* fast reading later. 
    """  