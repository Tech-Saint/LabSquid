from labmanager import init_backend
import tkinter as tk
from tkinter import ttk

class gui(tk.Tk):
    def __init__(self,appcontrol):
        self.AppControl = appcontrol

        super().__init__()

        self.title("Debug_interface")
        self.configure(background='#1A1A24')

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.window_height= self.winfo_height()

        style = ttk.Style()
        style.configure('Horizontal.TSeparator', background='#2F2F3F')

        self.option_var = tk.StringVar(self)


        self.creator = tk.Label(bg="#1A1A24",fg="skyblue", borderwidth=0,font=("Helvetica",11), text= "Built by Linkeyth\nV0.9 - 6/29/23" , justify=tk.RIGHT, anchor="w")

        self.instruction = tk.Label(
            text="For issues, Please reach out to Linkeyth on slack or via email." 
                ,font=("Helvetica", 12 , "italic"), padx=70, height=5, bg="#282836",fg="#E4E4F7")

        self.scrollbar = tk.Scrollbar(self)


            ## button setup
        style.theme_use("clam")
        style.map('head.TButton',
                relief='flat',
                height="17",
                        foreground=[('!active', 'skyblue'),('pressed', 'yellow'), ('active', 'White')],
                        background=[ ('!active','#282840'),('pressed', '#1A1A24'), ('active', '#2F2F3F')])

        self.status= tk.Label(bg="#1A1A24",fg="yellow", borderwidth=0,font=("Helvetica",11), text= "Initializing" , justify=tk.RIGHT, anchor="w")
        self.status.grid(column=4,row=0)


        self.listbox = tk.Listbox(self,
                        borderwidth=0,
                        highlightthickness=0,
                        bg = "#282836",
                        activestyle = 'dotbox',
                        font = "Arial, 20", 
                        yscrollcommand = self.scrollbar.set,
                        highlightbackground="skyblue",
                        fg = "yellow")
        
        self.listbox.insert(0,"Select a Device")

        self.listbox.grid(row=3, column=0,columnspan=5,pady=10,padx=20,sticky="news")
        self.scrollbar.config(command = self.listbox.yview)

        self.scrollbar.grid(row=3, column=1,columnspan=5, sticky="nes")

        self.Devicenames=list(self.AppControl.Device_instances.keys())

        option_menu = ttk.OptionMenu(
            self,
            self.option_var,
            "Select Device",
            *self.Devicenames,
            command=self.selectDevice)
        
        option_menu.grid(row=0, column=0,ipadx=4, sticky="w")
        self.setupbuttons()

    def setupbuttons(self):
        head = ttk.Button(self, text="ping",style="head.TButton",command =lambda: self.runCommand("ping")).grid(row=1, column=0,ipadx=4, sticky="w")
        head = ttk.Button(self, text="ping",style="head.TButton",command =lambda: self.runCommand("ping")).grid(row=1, column=1,ipadx=4, sticky="w")
        head = ttk.Button(self, text="ping",style="head.TButton",command =lambda: self.runCommand("ping")).grid(row=1, column=2,ipadx=4, sticky="w")

        
    def runCommand(self,command:str):
        try:
            self.AppControl.mass_ssh_command(command,self.selcteddevice)
        except AttributeError:
            self.status.configure(text="no device selected!")

    def selectDevice(self, *args):

        self.selcteddevice = args[0]
        
        self.listbox.delete(0,self.listbox.size())
        Disallowlist = ("sudo","password","secret")

        for i,k in enumerate(self.AppControl.Device_instances[self.selcteddevice].device): 
            if k in Disallowlist:
                continue
            self.listbox.insert(i,f" {k}: {self.AppControl.Device_instances[self.selcteddevice].device[k]}")
        pass





if __name__ == "__main__":
    AppControl=init_backend()
    app = gui(AppControl)
    app.mainloop()

