from flask import Blueprint, render_template



devices = Blueprint('devices', __name__)

@devices.route('/devices')
def showdevices():

    return render_template('Alldevices.html' )

@devices.route('/devices/<Device>')
def sh_single_dev(Device):

    return render_template('Device.html',device=Device)

@devices.route('/add/device')
def addDevice():

    return render_template('Adddevice.html',)

