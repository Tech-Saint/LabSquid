

def init_Roles(Device):
    """Takes in device and modifies the SSH CMDs to fit"""
    for role in Device.roles:
        match role:
            case "dns":
                Device.update_DNS = update_DNS() 
            case _:
                pass
            
        

def update_DNS():
    pass