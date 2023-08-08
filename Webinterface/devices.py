from flask import Blueprint, render_template



devices = Blueprint('devices', __name__)

@devices.route('/devices')
def showdevices():

    return render_template('devices.html' )
