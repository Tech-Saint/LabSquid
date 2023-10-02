from flask import Blueprint, render_template , request, flash, redirect, url_for, session
from concurrent.futures import as_completed,ThreadPoolExecutor
import re, copy
from Labmanager.src.clients import init_device_objs


from Webinterface import lab


devices = Blueprint('devices', __name__)

@devices.route('/devices')
def showdevices():
    if 'logged_in' not in session:
        return redirect("/login")
    return render_template('Alldevices.html' )

@devices.route('/device/<device>/edit',methods=('GET', 'POST'))
def edit_single_dev(device):
    try:
        if request.method == "POST":
            if lab.db.unsaved_changes != True:
                #append data 
                temp_device = copy.deepcopy(lab.db.data['devices'][lab.DeviceInstances[device].device["id"]])
                for i in request.form:
                    if request.form[i] == '':
                        continue
                    else:
                        temp_device[i]=request.form[i]
                #check data 
                result = lab.db.Verify_data(temp_data=temp_device)
                if len(result) != 0:
                    for i in result:
                        flash(f"{i.capitalize()}","danger")
                    return render_template('EditDevice.html',device=device)
                
                else:
                    #apply changes 
                    lab.db.temp_data['devices'][lab.DeviceInstances[device].device["id"]]=temp_device
                    result=lab.db.save_db()
                    lab.db.load_db()
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        init_device = executor.submit(init_device_objs,temp_device)

                        try:
                            lab.DeviceInstances[device] = init_device.result()
                            print("re-initialized: "+ device)
                        except Exception as e:
                            print(f"Error: {e}")

                    # Update device IDs
                    for _ in lab.DeviceInstances:
                        a=next(( item for item in lab.db.data['devices'] if item["DNS_name"] == _),None)
                        lab.DeviceInstances[_].device['id']= int(a["id"])
                        

                    return redirect(f'/device/{device}')
    
    except Exception as e:
        print(e)

    return render_template('EditDevice.html',device=device)



@devices.route('/device/<Device>',methods=('GET', 'POST'))
def sh_single_dev(Device):
    if 'logged_in' not in session:
        return redirect("/login")

    if request.method=="POST":
        try:
            if request.form["action"]=='DELETE':
                lab.db.remove_device(lab.DeviceInstances[Device].device)
                lab.db.load_db()
                                
                del lab.DeviceInstances[Device]
                return showdevices()
            else:
                try:
                    result=lab.command(devices=Device ,instruction=request.form["action"])
                    flash(f"Success fully ran with result:{result}","success")
                except Exception as e:
                    flash(f"Failed to run due to error: \n{e}","danger")
        except:
            pass

    return render_template('Device.html',device=Device)

@devices.route('/add/device',methods=('GET', 'POST'))
def addDevice():
    if 'logged_in' not in session:
        return redirect("/login")
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
            if request.form["device_type"]=="Select":
                flash("Please select a device type")
                formInvalid=True
            
            if formInvalid==True:return render_template('Adddevice.html',)
            try: 
                lab.DeviceInstances[request.form["DNS_name"]]
                flash(f"The DNS name: '{request.form['DNS_name']}' already exists!")
                return render_template('Adddevice.html')      
            except KeyError: pass
            new_device=dict(request.form)
            new_device["password"]=new_device["password1"]
            try:
                id = max([id['id'] for id in lab.db.temp_data['devices']])
                id+=1
            except ValueError:
                id=0
            new_device["id"]=id
            del new_device["password2"]
            del new_device["password1"]
            lab.db.add_device(new_device)
            lab.db.save_db()
            lab.db.load_db()       
 

            lab.DeviceInstances[new_device["DNS_name"]]=init_device_objs(new_device)
            return redirect(f"/device/{new_device['DNS_name']}")

    except Exception as e:
        flash(e)
    return render_template('Adddevice.html')

