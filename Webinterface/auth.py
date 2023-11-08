from flask import Blueprint,render_template,request,session,redirect,flash

from Webinterface import lab

auth = Blueprint('auth', __name__)

@auth.route('/login',methods=['GET', 'POST'])
def login():
    if request.method=="POST":
        session["logged_in"] = False
        formInvalid=False
        for i in request.form:
            if request.form[i] == '':
                flash(f"Please fill out {i}")
                formInvalid=True
        if formInvalid == True:
            return redirect("/login")
        Return = lab.db.userDB.execute_query(f"""
            SELECT * FROM users
            WHERE Email = '{request.form['email']}'
        """)
        if Return == []:
            flash("Email is invalid")
            return redirect("/login")
        if Return[-1][-1] == request.form['password1']:
            session["logged_in"]=True
            session["name"] = Return[-1][1]
            session["email"] = Return[-1][2]
            return redirect("/")
        flash("Invalid Password")
    if lab.db.userDB.execute_query(f"""SELECT * FROM users""") == []:
        return redirect('/signup')
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
        formInvalid=False
        for i in request.form:
            if request.form[i] == '':
                flash(f"Please fill out {i}")
                formInvalid=True

        if request.form["password1"] != request.form["password2"]:
            flash(f"Passwords do not match!")
            formInvalid=True

        if formInvalid == True:
            return redirect("/signup")
        
        result = lab.db.userDB.execute_query(f"""
            INSERT INTO users (Username, Email, Password) VALUES (
                '{request.form["username"]}', '{request.form["email"]}', '{request.form["password1"]}'
            )""")
        
        if result!=[]:
            flash(result)
        else:
            lab.db.userDB.connection.commit()
        return redirect("/login")
    return render_template("signup.html")