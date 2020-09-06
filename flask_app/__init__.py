from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

"""init app"""
app = Flask(__name__)

"""set configurations for Jinja"""
app.jinja_env.filters['zip'] = zip

"""set configurations for DB"""
app.config.from_object(Config)
db = SQLAlchemy(app)

"""set configurations for login manager"""
login = LoginManager(app)
login.login_view = 'login'

from flask_app import routes, models

if __name__ == '__main__':
    app.run()
