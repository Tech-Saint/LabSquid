import json, cryptography, os,re
from sys import platform,path 
from copy import deepcopy
from .SQL_DB import SQL_DB

from Labmanager.src.Localutils import log_event

#TODO figure out password storage.

class _Database():
    """Creates and loads a DB object to change and update."""
    def __init__(self):
        self.dir_path = os.path.join(os.path.dirname(__file__))
        self.Refresh_image_list()
        self.userDB=SQL_DB()
        self.load_db()
        self.temp_data = deepcopy(self.data) # unlinks the dict.
        self.unsaved_changes = False
        log_event("Initalized DB Object")
    
    def __repr__(self):
        return self.data

    def Refresh_image_list(self):
        """Refreshes the image list."""
        return
        image_list = os.listdir(os.path.join(os.path.dirname(self.dir_path), "Images"))
        for _ in range(len(image_list)):
            image_list[_] = image_list[_][:-4] #strips the File ext.
        self.image_list = image_list

    def Verify_data(self, temp_data:dict = None,) ->( list ) :
        """Confirms a device dict is valid."""
        #TODO convert to pandas table. 
        result_list=[]

 
            # Check ip       
        if re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", temp_data["ip"]) == False:
            result_list.append(f"Please enter a valid IP.\n")

        return result_list

    def Verify_all_data(self,database=None) -> ( list ):
        """Verfies All of the database entries"""
        
        if database == None:
            database = self.temp_data
            using_database = True

        for i in list(database.keys()):

            if i == "Templates":
                continue
           
            for index,key in enumerate(database[i]):
                ok=False
                result = self.Verify_data(temp_data = key)
                if len(result) != 0:
                    return result # returns the error statement.
            
            if i == "devices":
                database[i] = sorted(database[i], key=lambda d: d['ip'])
            else:
                return (f"Error: {i} is not a valid database.")

            for index,key in enumerate(database[i]):
                database[i][index]["id"] = index

        try: 
            using_database
            self.temp_data=database
            return ["All data was verified successfully."]
        except:pass
        return ["All data was verified successfully."]
    
    def save_db(self):
        result_list=self.Verify_all_data()
        if result_list != ["All data was verified successfully."]:
            return result_list
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"device_db.json"), 'w', encoding = 'utf-8') as f:
            json.dump(self.temp_data, f, indent = 4)
        result_list.append("Saved Database")
        self.load_db()
        self.unsaved_changes = False
        log_event("saved db")
        return result_list
        

    def load_db(self):
        try:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"device_db.json"), 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"device_db.json"), 'w', encoding = 'utf-8') as f:
                self.data={
                            "Templates": {
                                "devices": [
                                    "DNS_name",
                                    "device_type",
                                    "netmiko_type",
                                    "ip",
                                    "username",
                                    "password"
                                ]
                            },
                            "devices": []
                            }
                json.dump(self.data, f, indent = 4)
                
    def update_db(self,entry:dict):
        """Give this a single database entry."""
        index=entry["id"]
        self.temp_data["devices"][index]=entry
        self.save_db()
        log_event(f"Updated entry:{entry['DNS_name']}")

    def add_device(self,entry:dict):
        entry["id"]=len(self.data["devices"])
        self.temp_data["devices"].append(entry)
        self.save_db()
        log_event(f"Added entry:{entry['DNS_name']}")
    
    def remove_device(self,entry:dict):
        
        index=entry["id"]
        del self.temp_data["devices"][index]
        self.save_db()
        log_event(f"Removed entry:{entry['DNS_name']}")


if __name__ == "__main__":

    def add_entry_cli(data,loc):
        stop=False
        temp_data = data.copy()
        while stop != True:
            data[loc].append({})
            for x in data["Templates"][loc]:
                temp=input(f"{x}:")
                temp_data[loc][-1].update({x:str(temp)})
            temp_data[loc][-1]['id']=len(temp_data[loc])-1
            stop = bool(input("Hit enter to continue or type exit to stop and commit changes.\n"))
        data[loc]=temp_data[loc]
        return data

    def remove_entry_cli(data,loc):
            stop=False
            temp_data = data.copy()
            while stop != True:
                Local_keys=[]
                for index,value in enumerate(temp_data[loc]):
                    print(f"{index} : {value}")
                    Local_keys.append(index)
                    
                del_selection = int(input("type the number attached to the entry to delete it."))
                temp_data[loc].pop(del_selection)
                print("Removed entry")
                stop = bool(input("Hit enter to continue or type exit to stop and commit changes.\n")) 
            return data

    def update_entry_cli(data,loc):
            stop=False
            temp_data = data.copy()
            while stop != True:
                Local_keys=[]
                for index,value in enumerate(temp_data[loc]):
                    print(f"{index} : {value}")
                    Local_keys.append(index)
                    
                main_selection = int(input("type the number attached to the entry to modify it."))
                Local_keys.clear()

                for i in temp_data[loc][main_selection].keys():
                    print(f"{n} : {i}")
                    Local_keys.append(i)
                    n+=1
                i=int(input("Type the number next to the entry to modify it."))
                temp=(input("What is the new updated value"))
                temp_data[loc][main_selection].update({Local_keys[i]:str(temp)})
                print("Updated entry")
                stop = bool(input("Hit enter to continue or type exit to stop and commit changes.\n")) 
            return data
    
    Database = _Database()
    valid,done=False,False
    data=Database.data

    while valid == False:
        print("Would you like to change?")
        n=0
        top_keys=[]
        for n,i in enumerate(Database.data.keys()):
            print(f"{n} : {i}")
            top_keys.append(i)
            
        Whattodo=str(input("or type E to exit.\n")).lower()
        if Whattodo == "e":
            exit()
        try:
            Whattodo=int(Whattodo)
            sel_key=top_keys[Whattodo]
            valid=True
        except IndexError:
            print("Please type a valid number in the list!")
        except ValueError: 
            print("Please type a number!")
        
    try: 
        while done == False:
            selection=input(f"Selected to modify the {sel_key} db\nwould you like to remove, add, or update entries?")
            match selection:
                case "remove"|"r":
                    data=remove_entry_cli(data,sel_key)
                case "add"|"a":
                    data=add_entry_cli(data,sel_key)
                case "update"|"u":
                    data=update_entry_cli(data,sel_key)
                case other:
                    print("Please Type add, remove, or update")
                    continue
            for i in data["devices"]:
                Database.update_db(i)
            Database.save_db()
            print("Saved db")
            done = bool(input("Hit enter to continue or type exit to stop.\n"))

    except KeyboardInterrupt:
            exit()




    
    
    def del_entries(self,selected:list, dictkey) -> str:
        """
        This function will delete the selected entries from the database.
        selected is a list of IDs to remove. 
        Returns a result string. 
        """
        
        list_of_IDs = []
        for i in selected:
            list_of_IDs.append(int(i[-1])) # this should always be the ID. Makes sure that the list of indexes are interpreted as an int.
        
        Local_temp = self.temp_data[dictkey].deepcopy()
        for index,i in reversed(list(enumerate(self.temp_data[dictkey]))):
            try:
                if i["id"] in list_of_IDs:
                    Local_temp.remove(i)

            except KeyError:
                return("There was an error deleting entries. Aborted database changes.")
            
        self.temp_data[dictkey] = Local_temp
        self.unsaved_changes = True

        return ("Successfully deleted entries.")
    
    def Update_db_entry(self,entry:dict, dictkey) -> str:
        """
        Give this a single database entry.
        The database entry will require the 
        """
        
        try:
            index=entry["id"]

            Local_temp = self.temp_data[dictkey].deepcopy()

            Local_temp[index]=entry

        except Exception as e:

            return (f"failed to update entry. Error:\n{e} \nAborted database changes.")
        
        self.temp_data[dictkey] = Local_temp

        self.unsaved_changes = True
        return ("Successfully updated entry.")
