from labmanager import init_backend
import tkinter as tk
from tkinter import ttk

class gui:
    def __init__(self,appcontrol,window:tk):
        self.AppControl = appcontrol

        style = ttk.Style()
        style.configure('Horizontal.TSeparator', background='#2F2F3F')
        self.textcolor = "grey87"
        self.bgcolor = "#090C21"
        self.btncolor = "#282840"
        self.accenttext = "#41FAD4"
        self.accentbg = "#173057"
        self.accent = "#3A7CDE"
        self.accent2 = "#4DBCF5"

        style = ttk.Style()
        style.theme_use("alt")
        
        style.configure('.',
            font = "Arial, 15",             
            borderwidth = 0, )
        
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        style.configure('TLabel', background = self.bgcolor, foreground = self.textcolor)
        style.configure('TFrame', background = self.btncolor)
        style.configure('TButton', background = self.btncolor, foreground = self.accenttext)
        
        style.configure("bar.Horizontal.TProgressbar",
                        troughcolor = self.btncolor, 
                        bordercolor = self.btncolor,
                        background = self.accent2,
                        lightcolor = self.accent2, 
                        darkcolor = self.accent2)
        
        style.map('main.TButton',
        relief = 'flat',
        height = "17",
        foreground = [('!active', self.textcolor), ('pressed', self.accent2), ('active', self.accenttext)],
        background = [('!active', self.btncolor), ('pressed', self.bgcolor), ('active', self.accent)])
        
        style.map('Action.TButton',
        relief = 'flat',
        height = "17",
        foreground = [('!active', "#F7F4E4"), ('pressed', self.textcolor), ('active', self.accent2)],
        background = [('!active', self.accent), ('pressed', self.btncolor), ('active', self.accent)])
        
        style.map('main.TMenubutton',
        relief = 'flat',
        height = "17",
        foreground = [('!active', self.textcolor), ('pressed', self.accent2), ('active', self.accenttext)],
        background = [('!active', self.btncolor), ('pressed', self.bgcolor), ('active', self.accent)])


        style.configure("TScrollbar",
                background = self.btncolor,
                gripcount = 0,
                reilef = "flat",
                troughcolor = self.accent,
                bordercolor = self.bgcolor,
                lightcolor = self.accent2, 
                darkcolor = self.accent2,
                arrowcolor = self.btncolor)
        
        style.configure("Treeview",
                background = self.btncolor,
                foreground = self.accent2,
                lightcolor = self.accent2, 
                darkcolor = self.accent2,
                borderwidth = 5,
                bordercolor = self.bgcolor,
                rowheight = 35,
                fieldbackground = self.btncolor,
                troughcolor = self.btncolor, )
        
        style.configure('Treeview.Heading',
                background = self.accenttext,
                foreground = self.btncolor,
                font = "Arial, 15",
                relief = tk.RIDGE,
                fieldbackground = self.accent)
        
        
        style.configure('TCheckbutton',
                focuscolor = '',
                font = ['arial', '15', 'italic'])

        style.map('TCheckbutton',
          foreground = [('disabled', "white"),
                      ('pressed', "white"),
                      ('active', self.textcolor),
                      ('!active', self.accenttext)],
          background = [('disabled', self.accent),
                      ('pressed', '!focus', self.accent),
                      ('active', self.bgcolor),
                      ('!active', self.bgcolor)],
          indicatorcolor = [('selected', self.accent),
                          ('pressed', self.bgcolor)])

        style.map("Treeview",
                    background = [('selected', self.accent2)],
                    foreground = [('selected', self.accent)])
        
        
        self.window = window
        self.window.configure(background = self.bgcolor)


        self.window.title("Debug_interface")

        self.window.grid_columnconfigure(2, weight = 1)
        self.window.grid_rowconfigure(3, weight = 1)

        
        self.scrollbar = tk.Scrollbar(self.window)


        self.status= tk.Label(bg=self.bgcolor,fg="yellow", borderwidth=0,font=("Helvetica",11), text= "Initializing" , justify=tk.RIGHT, anchor="w")
        self.status.grid(column=4,row=0)


        self.listbox = tk.Listbox(self.window,
                        borderwidth=0,
                        highlightthickness=0,
                        bg = self.accentbg,
                        activestyle = 'dotbox',
                        font = "Arial, 20", 
                        yscrollcommand = self.scrollbar.set,
                        fg = self.accent)
        
        self.listbox.insert(0,"Select a Device")

        self.listbox.grid(row=3, column=0,columnspan=5,pady=10,padx=20,sticky="news")
        self.scrollbar.config(command = self.listbox.yview)

        self.scrollbar.grid(row=3, column=1,columnspan=5, sticky="nes")

        self.Devicenames=list(self.AppControl.DeviceInstances.keys())

        self.option_var = tk.StringVar(self.window)


        self.table_config = ttk.OptionMenu(self.window, self.option_var, "select device", *self.Devicenames, style = "main.TMenubutton", command=self.selectDevice)
        self.table_config['menu'].config(bg = self.btncolor, fg = self.textcolor, activebackground =  self.accent, activeforeground =  self.accenttext, relief = 'flat')
        self.table_config.grid(column = 0, padx = (40, 0), row = 0, pady = 20, sticky = "w")
        
      
        self.setupbuttons()

    def setupbuttons(self):
        head = ttk.Button(self.window, text="ping",style="head.TButton",command =lambda: self.runCommand("ping")).grid(row=1, column=0,ipadx=4, sticky="w")

        
    def runCommand(self,command:str):
        device=self.option_var.get()
        try:
            output=self.AppControl.command(command,device)
            print(output)
            self.status.configure(text=output)
        except Exception as e:
            self.status.configure(text=e)

    def selectDevice(self, *args):

        self.selcteddevice = args[0]
        
        self.listbox.delete(0,self.listbox.size())
        Disallowlist = ("sudo","password","secret")

        for i,k in enumerate(self.AppControl.DeviceInstances[self.selcteddevice].device): 
            if k in Disallowlist:
                continue
            self.listbox.insert(i,f" {k}: {self.AppControl.DeviceInstances[self.selcteddevice].device[k]}")
        pass

    def loop(self):
        self.window.after(10,self.loop)

if __name__ == "__main__":
    root = tk.Tk()
    AppControl=init_backend()
    app = gui(AppControl,root)
    root.after(10,app.loop)
    root.mainloop()

