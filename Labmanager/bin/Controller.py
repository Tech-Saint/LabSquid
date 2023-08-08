import json, os, configparser
from concurrent.futures import ThreadPoolExecutor , as_completed
from .db.database_interface import  _Database
from .clients import *


output_list=[]
class Controller_unit():
    """Orchistrates and holds info to give back to each device instance."""
    def __init__(self):

        self.path_of_tool = path[0]
        self.file_setup()


    def file_setup(self):
        if platform=="win32":
            self.username =os.getenv("username")
            self.path_of_bin = os.path.dirname(os.path.realpath(__file__))
            self.path_of_db = self.path_of_bin +"\\db\\"
        else:
            self.username =os.getenv("USER")
            self.path_of_bin = os.path.dirname(os.path.realpath(__file__))
            self.path_of_db = self.path_of_bin + "/db/"
            
        config=configparser.ConfigParser()
        config.read(self.path_of_bin+'config.ini')
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
    
    
    ## testing 

    def mass_ssh_command(self,instruction:str, devices:list=None):
        """pass None to dev list to do all instances"""
        if devices == None: devices= list(self.DeviceInstances.keys())
        if type(devices) == str:
            devices=[devices]

        results = []
        jobs=[]
        with ThreadPoolExecutor(8) as executor:
            for i in devices:
                task = executor.submit(self.DeviceInstances[i].dynamic_method_call,instruction)
                jobs.append(task)
            for entry in jobs:  
                result = entry.result(timeout=60)
                results.append(result)

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
                print(f"The IP for {DNS_name} is invalid, \nPlease type a correct number below")
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
                    print(f"The IP for {'DNS_name'} is invalid, \nPlease type a correct number below")
                    updated_val=input()
                    Valid=bool(int(max(re.findall(ip_regex, data[db][i]["ip"])))> 254)
        except KeyError:pass
    data[db] = sorted(data[db], key=lambda d: d['ip']) # sorts for *hopefully* fast reading later. 
    """  