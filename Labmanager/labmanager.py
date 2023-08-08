try:
    from .bin.Controller import *
except:
    from bin.Controller import *

import sys
      

def init_backend() -> Controller_unit:
    """returns ControllerUnit class and a dict of Device_instance classes"""

    session=Controller_unit()

    DeviceInstances = {}

    with ThreadPoolExecutor(max_workers=8) as executor:
        task = {executor.submit(init_device_objs,device): device for device in session.device_info["devices"]}
        for future in as_completed(task):
            _ = task[future]
            DeviceInstances[_["DNS_name"]] = future.result()

    session.DeviceInstances=DeviceInstances
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

    session=init_backend()
    session.command(devices=["Pastasauce"],instruction="ping_device")

    session.command(devices=session.DeviceInstances,instruction="update_info")
    session.update_db(session.DeviceInstances)
            
    