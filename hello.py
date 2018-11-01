

from flask import Flask
# create a global Flask instance directly at the top of your code

app=Flask(__name__)
# A Flask application is an instance of the Flask class.
# Everything about the application, such as configuration and URLs, will be registered with this class.

@app.route('/')
def hello():
    return 'Hello,World!'