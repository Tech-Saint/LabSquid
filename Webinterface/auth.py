from flask import Blueprint,render_template,request,session,redirect


auth = Blueprint('auth', __name__)

@auth.route('/login',methods=['GET', 'POST'])
def login():
    if request.method=="POST":
        session["logged_in"]=True
        return redirect("/")
    return render_template("login.html")

@auth.route('/logout',methods=['GET', 'POST'])
def logout():
    try:
        del session["logged_in"]
    except: pass
    return redirect("/login")

@auth.route('/signup',methods=['GET', 'POST'])
def signup():
    if request.method=="POST":
        session["logged_in"]=False
        return redirect("/login")
    return render_template("signup.html")