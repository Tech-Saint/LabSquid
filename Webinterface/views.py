
from json import dumps as jsonstring


from flask import Flask,render_template,request,Blueprint

from flask_bootstrap import Bootstrap

views = Blueprint('views', __name__)

@views.route('/',methods=['GET', 'POST'])
def home():
    return render_template('index.html')

