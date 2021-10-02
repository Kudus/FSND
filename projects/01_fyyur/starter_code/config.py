import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
# IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://dbuser:strpassword@192.168.1.10:5432/fyyurapp'

SQLALCHEMY_TRACK_MODIFICATIONS = False

os.environ["FLASK_ENV"] = "development"
