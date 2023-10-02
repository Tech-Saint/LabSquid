from Webinterface import Main_app
from uuid import uuid4

app = Main_app()

if __name__ == "__main__":

    app.config["SECRET_KEY"]=uuid4().hex

    app.run(debug=True,host="0.0.0.0")