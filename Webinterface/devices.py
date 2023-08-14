from flask import Blueprint, render_template , request, flash

import re
from Labmanager.bin.clients import init_device_objs

from Webinterface import session


devices = Blueprint('devices', __name__)

@devices.route('/devices')
def showdevices():

    return render_template('Alldevices.html' )

@devices.route('/devices/<Device>')
def sh_single_dev(Device):

    return render_template('Device.html',device=Device)

@devices.route('/add/device',methods=('GET', 'POST'))
def addDevice():
    try:
        if request.method == "POST":
            formInvalid=False
            for i in request.form:
                if request.form[i] == '':
                    flash(f"Please fill out {i}")
                    formInvalid=True
            if request.form["password1"] != request.form["password2"]:
                flash(f"Passwords do not match!")
                formInvalid=True
            if request.form["device_type"]=="Device Type":
                flash("Please select a device type")
                formInvalid=True
            ip_octet_regex=r"(?:[\d]{1,3})"
            ip_format_regex=r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
            highest_value=257

            if formInvalid==True:return render_template('Adddevice.html',)

            if re.match(ip_format_regex,request.form["ip"]) != None:  
                try:
                    highest_value=max([int(i) for i in re.findall(ip_octet_regex, request.form["ip"])])
                    if highest_value > 254:
                            raise Exception
                    
                    else:
                        try: 
                            session.DeviceInstances[request.form["DNS_name"]]
                            flash(f"The DNS name: '{request.form['DNS_name']}' already exists!")
                            return render_template('Adddevice.html')

                        except KeyError: pass
                        new_device=dict(request.form)
                        new_device["password"]=new_device["password1"]
                        del new_device["password2"]
                        del new_device["password1"]
                        session.db.add_device(new_device)
                        session.db.load_db()
                        
                        session.DeviceInstances[new_device["DNS_name"]]=init_device_objs(new_device)
                        return sh_single_dev(new_device["DNS_name"])


                except Exception as e: 
                    flash("IP address is invalid!")

            else: 
                flash("IP address is invalid!")
    except Exception as e:
        print(e)
    return render_template('Adddevice.html',)

