
from json import dumps as jsonstring


from flask import Flask,render_template,request,Blueprint

from Webinterface import session

views = Blueprint('views', __name__)

@views.route('/',methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@views.route('Settings',methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')

@views.get("/uptime")
def return_uptime():
    return session.uptime()