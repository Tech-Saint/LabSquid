from os import popen
from sys import platform,path 
from socket import gethostbyname
from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException, SSHDetect

from .Localutils import *
from .client_base import __client ,win32 , linux
from .roles import *


def build_device_init_dict() -> dict:
    """Creates a dictionary of keys and their associated device classes made from the __client class."""
    
    deviceBuilderDict={
         "win32": win32,
         "linux": linux,
    }
    modlist = [module for module in globals() if not module.startswith("__")]
    for moduleName in modlist:
        module = globals()[moduleName]
        for objName in dir(module):
            try:
                if issubclass((getattr(module, objName)),__client) == True and objName != "__client":
                    moddedDevice = getattr(module, objName)
                    deviceBuilderDict[moddedDevice.deviceName] = moddedDevice
                    
            except: pass
    return deviceBuilderDict




