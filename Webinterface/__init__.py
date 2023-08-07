from flask import Flask

def Main_app():
    app = Flask(__name__)


    from .auth import auth

    app.register_blueprint(auth,url_prefix="/auth/")

    from .views import views

    app.register_blueprint(views,url_prefix="/")