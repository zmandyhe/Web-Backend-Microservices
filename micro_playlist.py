# This is the main code that is going to run the Flask webserver and will interact
# with the user. It will pull functionality from the different microservices modules.

# Regular imports
import flask;
from flask import request, jsonify;
import sqlite3;
import sys;

# Add our custom /lib path at runtime to access our libraries
sys.path.append("./lib");

# Import our different microservices library
import tracks;

# Create our main app thread. TODO: Make debug dynamic based on config file.
app = flask.Flask(__name__);
app.config["DEBUG"] = True;

# The Main Page
@app.route('/', methods=["GET"])
def home():
    return '''<h1>Welcome to our Playlist Microservices API.</h1> \
            <img src="/usr/images/uc.jpg" alt="Under Construction"> \
            <p> This website is still being built! </p>''';
            # NOTE: Still trying to get images to be served by Flask
# End home()

# This is a custom HTTP 404 (File Not Found) error
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1> \
            <p>The resource could not be found.</p>", 404;
#End of page_not_found()

# This is the route to return all of the data from the tracks table.
@app.route('/api/v1/resources/tracks/all', methods=['GET'])
def route_tracks_all():
    resp = tracks.tracks_all();
    return resp;
# End route_tracks_all()

# And we're off!
app.run(port=8000);
