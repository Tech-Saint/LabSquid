
from json import dumps as jsonstring


from flask import Flask,render_template,request,Blueprint,flash

from Webinterface import session

views = Blueprint('views', __name__)

@views.route('/',methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@views.route('Settings',methods=['GET', 'POST'])
def settings():
    if request.method=="POST":
        try:
            output=session.UpdateSettings(request.form)
            if type(output)==str:
                flash(output,"success")
            else:
                for I in output:
                    flash(I,"danger")
        except Exception as e:
            flash(f"Failed to run due to error: \n{e}","danger")

    return render_template('settings.html')


@views.get("/uptime")
def return_uptime():
    return session.uptime()