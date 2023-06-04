from bin.Controller import *
import sys , concurrent.futures 

def init_device_objs(device):
    match device["device_type"]:
        case "win32":
            return win32(device)
        case "linux":
            return linux(device)
        case "cisco":
            return network(device)
        

def mass_ssh_command(Device_instances,instruction:str, dev_list:list=None):
    """pass None to dev list to do all instances"""
    if dev_list == None: dev_list= list(Device_instances.keys())
    
    results = []
    jobs=[]
    with concurrent.futures.ThreadPoolExecutor(8) as executor:
        for i in dev_list:
            task = executor.submit(Device_instances[i].dynamic_method_call,instruction)
            jobs.append(task)
        for entry in jobs:  
            result = entry.result(timeout=60)
            results.append(result)

if __name__ == "__main__":
    #parse CLI 
    arg = ""
    try:
        arg = sys.argv[1].lower()
    except IndexError:
        #print("args empty")
        pass
    if arg == ("-v" or "--version"):
        print("placeholder")
        sys.exit()
    if arg == ("-h" or "--help"):
        print("placeholder")
        sys.exit()
    else:
        pass

    session=Controller_init()


    Device_instances = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        task = {executor.submit(init_device_objs,device): device for device in session.device_info["devices"]}
        for future in concurrent.futures.as_completed(task):
            _ = task[future]
            Device_instances[_["DNS_name"]] = future.result()
            print("Initialized: "+ _["DNS_name"])

    # test cases:
    # Replace "ctlbox" to test your own devices. Use the 
    print("avail ssh cmds" + list(Device_instances["ctlbox"].commands.keys()))
    #output = Device_instances["ctlbox"].dynamic_method_call("update_info")
    mass_ssh_command(Device_instances,"update_info")
    session.update_db(Device_instances)
    mass_ssh_command(Device_instances,"ping_device")
            
    