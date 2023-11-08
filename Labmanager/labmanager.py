try: 
    from .src.Controller import Controller_unit, init_device_objs
except:
    from src.Controller import Controller_unit

import sys
from concurrent.futures import ThreadPoolExecutor , as_completed
      

def init_backend() -> Controller_unit:
    """returns ControllerUnit class and a dict of Device_instance classes"""

    session=Controller_unit()

    DeviceInstances = {}

    with ThreadPoolExecutor(max_workers=1024) as executor:
        task = {executor.submit(init_device_objs,device): device for device in session.db.data["devices"]}
        for future in as_completed(task):
            _ = task[future]
            DeviceInstances[_["DNS_name"]] = future.result()

    session.DeviceInstances=DeviceInstances
    _threadPool=ThreadPoolExecutor(max_workers=1)
    _pingthread=_threadPool.submit(session.Action_thread)
    _threadPool.shutdown(False)
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
    
    session.update_db(session.DeviceInstances)
            
    