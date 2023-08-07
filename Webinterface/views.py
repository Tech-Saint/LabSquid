from Labmanager.labmanager import *
from json import dumps as jsonstring


from flask import Flask,render_template,request,Blueprint

from flask_bootstrap import Bootstrap

views = Blueprint('views', __name__)

@views.route('/')
def index():
    if request.method == 'POST':
        if request.form.get('action1') == 'VALUE1':
            DeviceInstances,session=init_backend()
            return render_template('devices.html', devices=DeviceInstances)
        else:
            pass # unknown
    elif request.method == 'GET':
        return render_template('index.html')
    
    return render_template("index.html")