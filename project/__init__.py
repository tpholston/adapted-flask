from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from project.connect_unix import get_connect_url


application=Flask(__name__)
CORS(application)
# Talisman(app, content_security_policy=None)

application.config["SQLALCHEMY_DATABASE_URI"] = get_connect_url()
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(application)

from project.init_db import init_db
init_db(db, application)

from project.adapted.views import index_blueprint
application.register_blueprint(index_blueprint,url_prefix='/')

