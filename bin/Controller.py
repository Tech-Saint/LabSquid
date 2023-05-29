import json, os, configparser
from .db.database_interface import  _Database
from .clients import *


output_list=[]
class Controller_init():
    def __init__(self):

        self.path_of_tool = path[0]
        self.file_setup()
        try:
            with open('splashtext.txt', encoding="utf-8") as f:
                splashText = f.read()
        except:
            splashText="Error in reading from splash text."                
        print(splashText+"\n")
        print("\nHello {}, Thank you for using this script!\n".format(self.username))

    def file_setup(self):
        if platform=="win32":
            self.username =os.getenv("username")
            self.path_of_bin = path[0]+"\\bin\\"
            self.path_of_db = self.path_of_bin +"\\db\\"
        else:
            self.username =os.getenv("USER")
            self.path_of_bin = path[0] + "/bin/"
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
    
    def update_db(self, Device_instances, dev_list:list=None):
        if dev_list == None: dev_list= list(Device_instances.keys())
        
        for i in dev_list:
            self.db.update_db(Device_instances[i].device)
        self.db.save_db()

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