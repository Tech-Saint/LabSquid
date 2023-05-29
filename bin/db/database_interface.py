import json, cryptography, os,re
from sys import platform,path 

#TODO figure out password storage.

class _Database():
    """Creates and loads a DB object to change and update."""
    def __init__(self):
        self.load_db()

    def __repr__(self):
        return self.data

    def prep_db(self):
        ip_regex=r"(?:[\d]{1,3})"
        for i in range(len(self.data["devices"])):
            self.data["devices"][i]["id"]=i
            highest_value=257
            while highest_value > 254:
                try:
                    highest_value=max([int(i) for i in re.findall(ip_regex, self.data["devices"][i]["ip"])])
                    if highest_value > 254:
                        self.fix_entry("ip",i)
                    
                except KeyError:pass

        # self.data["devices"] = sorted(self.data["devices"], key=lambda d: d['ip'])
        # Commented out as the device sort may cause issues later when db has not been passed to each thread. 
        # Fast enough for now. Uses Timsort to sort thr DB.
        # I'd like to open this up to have less loops...
             
    def fix_entry(self,loc:str,i):
        """
        Wrap this in a while not equal to the correct value loop. 
        """
        data=self.data["devices"][i]
        print(f"Invalid {loc} for \n{loc}")
        data[loc]=input(f"Please type the updated value for {loc}.\n")
        

    def save_db(self):
        self.prep_db()        
        try:
            with open(os.path.join(os.getcwd(),"bin","db","device_db.json"), 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=3)
        except:
            with open(os.path.join(os.getcwd(),"device_db.json"), 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=3)
        return 

    def load_db(self):
        try:
            with open(os.path.join(os.getcwd(),"bin","db","device_db.json"), 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            with open(os.path.join(os.getcwd(),"device_db.json"), 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def update_db(self,entry:dict):
        """"""
        index=entry["id"]
        self.data["devices"][index]=entry
        self.prep_db()
        


if __name__ == "__main__":

    def add_entry_cli(data,loc):
        stop=False
        temp_data = data.copy()
        while stop != True:
            data[loc].append({})
            for x in data["Templates"][loc]:
                temp=input(f"{x : }")
                temp_data[loc][-1].update({x:str(temp)})
            stop = bool(input("Hit enter to continue or type exit to stop and commit changes.\n"))
        data[loc]=temp_data[loc]
        return data

    def remove_entry_cli(data,loc):
            stop=False
            temp_data = data.copy()
            while stop != True:
                n=0
                Local_keys=[]
                for i in temp_data[loc]:
                    print(f"{n} : {i}")
                    Local_keys.append(i)
                    n+=1
                del_selection = int(input("type the number attached to the entry to delete it."))
                temp_data[loc].pop(del_selection)
                print("Removed entry")
                stop = bool(input("Hit enter to continue or type exit to stop and commit changes.\n")) 
            return data

    def update_entry_cli(data,loc):
            stop=False
            temp_data = data.copy()
            n=0
            while stop != True:
                for i in temp_data[loc]:
                    print(f"{n} : {i}")
                    n+=1
                main_selection = int(input("type the number attached to the entry to modify it."))
                n=0
                Local_keys=[]
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
        for i in Database.data.keys():
            print(f"{n} : {i}")
            top_keys.append(i)
            n+=1
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
            Database.prep_db(data,sel_key)
            Database.save_db(data,sel_key)
            print("Saved db")
            done = bool(input("Hit enter to continue or type exit to stop.\n"))

    except KeyboardInterrupt:
            exit()