try:
    from .bin.Controller import *
except:
    from bin.Controller import *

import sys
      

def init_backend() -> Controller_unit:
    """returns ControllerUnit class and a dict of Device_instance classes"""

    session=Controller_unit()

    Device_instances = {}

    with ThreadPoolExecutor(max_workers=8) as executor:
        task = {executor.submit(init_device_objs,device): device for device in session.device_info["devices"]}
        for future in as_completed(task):
            _ = task[future]
            Device_instances[_["DNS_name"]] = future.result()

    session.Device_instances=Device_instances
    return session


if __name__ == "__main__":
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

    session=Controller_unit()

    Device_instances = {}

    with ThreadPoolExecutor(max_workers=8) as executor:
        task = {executor.submit(init_device_objs,device): device for device in session.device_info["devices"]}
        for future in as_completed(task):
            _ = task[future]
            Device_instances[_["DNS_name"]] = future.result()

    # test cases:
    # Replace "ctlbox" to test your own devices. Use the 
    #print("avail ssh cmds" + list(Device_instances["ctlbox"].commands.keys()))
    #output = Device_instances["ctlbox"].dynamic_method_call("update_info")
    
    mass_ssh_command(Device_instances,"update_info")
    session.update_db(Device_instances)
    mass_ssh_command(Device_instances,"ping_device")
            
    