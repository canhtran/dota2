from flask import Flask, render_template
# from flask.ext.sqlalchemy import SQLAlchemy
import pymongo

# Define the WSGI application object
app = Flask(__name__)
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
# db = SQLAlchemy(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

# Import a module / component using its blueprint handler variable (mod_auth)
from app.homepage.controllers import main as main
from app.player.controllers import player as player

# Register blueprint(s)
app.register_blueprint(main)
app.register_blueprint(player)

# Build the database:
# This will create the database file using SQLAlchemy
# db.create_all()