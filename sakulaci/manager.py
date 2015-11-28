from flask import current_app
from flask.ext.script import Manager
from .application import create_app

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)
