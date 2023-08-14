from flask import Flask
from Labmanager.labmanager import init_backend

session=""

def Main_app():
    app = Flask(__name__)


    with app.app_context():
        global session
        session = init_backend()
    @app.context_processor
    def inject_global_vars():

        return {'lab': session}  # Return the session object as a dictionary
        
    from .views import views
    from .devices import devices
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(devices, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    
    return app