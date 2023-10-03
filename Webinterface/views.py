from json import dumps as jsonstring


from flask import Flask,render_template,request,Blueprint,flash,redirect,session,send_file
import os


from Webinterface import lab

views = Blueprint('views', __name__)

@views.route('/',methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@views.route('Settings',methods=['GET', 'POST'])
def settings():
    if 'logged_in' not in session:
        return redirect("/login")

    if request.method=="POST":
        try:
            output=lab.UpdateSettings(request.form)
            if type(output)==str:
                flash(output,"success")
            else:
                for I in output:
                    flash(I,"danger")
        except Exception as e:
            flash(f"Failed to run due to error: \n{e}","danger")

    return render_template('settings.html')
@views.route('logs')
def return_logs():
   
    try:
        return send_file(os.path.join(lab.path_of_tool,"log.txt"))
    except Exception as e:
        return str(e)
