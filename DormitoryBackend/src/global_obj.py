from flask import Flask
from flask_peewee.db import Database


def create_app():
    app = Flask(__name__)

    env = app.config['ENV']
    app.config.from_pyfile("../config/common.py", silent=False)
    if env.lower() == 'production':
        app.config.from_pyfile("../config/production.py", silent=False)
    else:
        app.config.from_pyfile("../config/development.py", silent=False)

    return app


app = create_app()
database = Database(app)
