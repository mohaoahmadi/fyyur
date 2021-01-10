import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# DONE
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:2142@192.168.0.10:5433/fuyyr'
# Add your own db address here