from flask import Flask
from Labmanager.labmanager import init_backend
import logging,os

lab=""

def Main_app():
    app = Flask(__name__)


    with app.app_context():
        global lab
        lab = init_backend()
    @app.context_processor
    def inject_global_vars():

        return {'lab': lab}  # Return the session object as a dictionary
        
    from .views import views
    from .devices import devices
    from .auth import auth

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='Debug.txt')
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(devices, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    
    return app