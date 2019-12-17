# This is the tracks microservice Python script.

import flask;
from flask import request, jsonify, g, Response;
from itertools import chain
import json
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

# Here we fire up an instance of our tracks app.
app = flask.Flask(__name__);
#app.config.from_envvar('APP_CONFIG');

# This is a helper function to modularize the database connection
def get_db_session():
    cluster = Cluster(['172.17.0.2'], port=9042)
    session = cluster.connect('xspf')
    return session

# This function runs when the user attempts to access the root of this microservice
# and all it does is spit out the REST API interface for the user to see the
# functionality
@app.route("/", methods=["GET"])
def tracks_home():
    return '''<h1>Welcome to the Tracks Microservice API!</h1>
    <p>This is a documentation page for the way to interface with
    the tracks microservice via Create, Retrieve, Edit, and Delete functions.</p>

    <h2>Create</h2>
    URL: <i>/api/v1/resources/tracks</i>, METHOD: POST <br/>
    <p>This function allows you to add new tracks to the database through
    a POST request. On success, it'll give the user back a 201 - Created.
    On failure, it'll return a 409 - Conflict. A failure is usually due to
    the track already existing in the database or lack of enough required
    data.</p>

    <p>Example Call: <br/>
        /api/v1/resource/tracks <br/>
        { <br/>
            "track_id": 001,<br/>
            "track_title":"I Ain't Got Time", <br/>
            "track_album":"Flower Boy", <br/>
            "track_artist":"Tyler, The Creator", <br/>
            "track_len":"3:25", <br/>
            "track_media_urlURL":"http://127.0.0.1:9000/minio/tracks/WhenYouSayYouLoveMe.mp3", <br/>
            "art_URL": NULL,<br/>
            "track_desc": "This is a wonderful song" <br/>
        }
    </p>

    <h2>Retrieve</h2>
    URL: <i>/api/v1/resources/tracks</i>, METHOD: GET <br/>
    <p>This function allows you to retrieve tracks from the tracks table. The user
    will perform a GET request on the tracks endpoint, and it will take the search
    parameters of track_id. It returns a 200 and the data
    if the data is in the table, and a 404 with an error message if not.

    <p>Example Call: <br/>
        /api/v1/resource/tracks?track_id = 001 <br/>
    <b>Which returns:</b> <br/>
        { <br/>
            "track_id": 001,<br/>
            "track_title":"I Ain't Got Time", <br/>
            "track_album":"Flower Boy", <br/>
            "track_artist":"Tyler, The Creator", <br/>
            "track_len":"3:25", <br/>
            "track_media_urlURL":"http://127.0.0.1:9000/minio/tracks/WhenYouSayYouLoveMe.mp3", <br/>
            "art_URL": NULL,<br/>
            "track_desc": "This is a wonderful song" <br/>
        }
    </p>

    <h2>Edit</h2>
    URL: <i>/api/v1/resources/tracks</i>, METHOD: PUT <br/>
    <p> This function allows the user to edit tracks that already exist in the database. It
    has a unique way of deliving the information to the function. Half of it is in the URL
    in a GET request type way, and the other half sits in the body like a POST request. The
    URL parameter is the name of the track you want to change, and the body data contains the
    new information. Because of a fluke in the way sqlite statements are handled in Python,
    if the user wants something to remain UNCHANGED, then they will still have to have that
    body variable present, just empty.
    This function returns a 200 OK on success, and a 404 Not Found if the record didn't
    exist in the table to begin with.
    </p>

    <p>Example Call: <br/>
        /api/v1/resource/tracks?track_name=Runner <br/>
    <br/>
        { <br/>
            "track_id": 001,<br/>
            "track_title":"Runner", <br/>
            "track_album":"Flower Boy", <br/>
            "track_artist":"Tyler, The Creator", <br/>
            "track_len":"3:25", <br/>
            "track_media_urlURL":"http://127.0.0.1:9000/minio/tracks/WhenYouSayYouLoveMe.mp3", <br/>
            "art_URL": NULL,<br/>
            "track_desc": "This is a wonderful song" <br/>
        } <br/>
    <i>NOTE: This reads: the track whose data we want to change is "Runner" (URL), and
    the data that we WANT changed are the album_name, track_len, and the track_URL. The
    rest remains unchanged (blank).</i>
    </p>

    <h2>Delete</h2>
    URL: <i>/api/v1/resources/tracks</i>, METHOD: DELETE <br/>
    <p>This function allows a user to delete a record out of the tracks table. This will
    use a straight-forward GET (URL) style parameter passing. It takes one parameter which
    is the track to remove.
    This function returns a 200 OK on success, and a 404 Not Found if the record didn't
    exist in the table to begin with.</p>

    <p>Example Call: <br/>
        /api/v1/resource/tracks?track_name=My+Slumbering+Heart<br/>
    </p>
    '''

# This function runs when the users attempts to add a track to the library.
#   On success, return a 201 - Created
#   On failure, return a 409 - Conflict
# share the table of playlists_by_playlist_id_and_username, but set
# playlist_id = 0, and username = "system"
@app.route("/api/v1/resources/tracks", methods=["POST"])
def track_create():
    session = get_db_session()
    error = None;
    playlist_id = 0
    username = "system"
    if not request.form.get("track_id", type=int):
        error = "Track's id Missing!"
    elif not request.form['track_name']:
        error = "Track Name Missing!";
    elif not request.form['album_name']:
        error = "Album Name Missing!";
    elif not request.form['artist']:
        error = "Artist Name Missing!"
    elif not request.form['track_len']:
        error = "Track Length Missing!"
    elif not request.form["media_URL"]:
        error = "art's URL Missing!"
    elif not request.form["art_URL"]:
        error = "art's URL Missing!"
    elif not request.form["track_desc"]:
        error= "track description missing!"
    track_id = request.form.get('track_id', type=int)
    track = (playlist_id, username, track_id, request.form['track_name'], request.form['album_name'],\
    request.form['artist'], request.form['track_len'],request.form['media_URL'],\
    request.form['art_URL'], request.form['track_desc'])
    session.execute(
        """
        INSERT INTO playlists_by_playlist_id_and_username (playlist_id, username, track_id, track_title, track_album, track_artist, track_len, track_media_url, track_art_url, track_desc)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        track
    )
    if error:
        ret_str = "<h1>Oops!</h1> <p>Looks like there was a problem inserting a new record \
                into the database: " + error + "</p>";
        return ret_str, 409;
    else:
        ret_str = "<h1>Success!</h1><p>This record was successfully added to the service!</p> "
        return ret_str, 201


# Retrieve track(s) by track_id(s)
# tracks share the same table with playlists_by_playlist_id_and_username
# but with playlist_id = 0 and username ="system"
#   On success, return a 200 - OK, with the data
#   On failure, return a 404 - Not Found, with an error
@app.route("/api/v1/resources/tracks", methods=["GET"])
def track_retrieve():
    playlist_id = 0
    username = "system"
    session = get_db_session()
    session.row_factory = dict_factory
    query_params = request.args;
    track_id_s = query_params.get('track_id_string')
    track_id = int(track_id_s)
    query = "SELECT * FROM playlists_by_playlist_id_and_username WHERE playlist_id= %s AND username =%s AND track_id= %s"
    rows = session.execute(query,(playlist_id, username, track_id))
    if rows is None:
        return page_not_found(404)
    else:
        data = []
        for row in rows:
            data.append(row)
        return Response(json.dumps(data, indent=4, sort_keys=False), 200, {'Content-Type': 'application/json'})


# This function attempts to edit a track'S media URL
@app.route("/api/v1/resources/tracks", methods=["PUT"])
def track_edit():
    session = get_db_session()
    session.row_factory = dict_factory
    playlist_id = 0
    username = "system"
    query_params = request.args;
    track_id_s = query_params.get("track_id_string")
    track_id = int(track_id_s)
    new_media_url = query_params.get("new_track_media_url")
    if track_id_s is not None and new_media_url is not None:
        query1 = "SELECT * FROM playlists_by_playlist_id_and_username WHERE playlist_id=%s AND username=%s AND track_id=%s"
        result1= session.execute(query1,(playlist_id, username, track_id))
        if result1 is None:
            return "track is not in the database"
        else:
            try:
                session.execute("UPDATE playlists_by_playlist_id_and_username SET track_media_url=%s WHERE playlist_id=%s AND username=%s \
                    AND track_id=%s", (new_media_url,playlist_id, username, track_id))
                return Response("200 OK,The track information is changed successfully", headers={'Content-Type':'application/json'},status=200)
            except Exception as err:
                return ('Query Failed: %s\nError: %s' % (''' UPDATE''', str()))
    else:
        return "input correct parameters"


# Detele a track by track_id
#   On success, return a 200 - OK, with a positive message
#   On failure, return a 404 - Not Found, with an error
@app.route("/api/v1/resources/tracks", methods=["DELETE"])
def track_delete():
    playlist_id = 0
    username = "system"    
    session = get_db_session()
    track_id_s = request.args.get('track_id_string')
    track_id = int(track_id_s)
    if track_id_s is None:
        return ("input track_id as a query parameter")
    else:
        try:
            query = "DELETE FROM playlists_by_playlist_id_and_username WHERE playlist_id=%s AND username=%s AND track_id=%s"
            session.execute(query,(playlist_id, username, track_id))
            return Response( "200 OK,The track is deleted successfully", headers={'Content-Type':'application/json'},status=200)
        except Exception as err:
            return ('Query Failed: %s\nError: %s' % (''' DELETE FROM users''', str()))


# This will be a special function that is a generic File Not Found error
# handler that will just spit out a message that let's the user know they've
# traveled down the wrong path.
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404 - File Not Found</h1> \
    <p>You have turned the wrong way. There is nothing down this path. Please go \
    back to the root page, and use one of the functions of the interface.</p>", 404
# End of page_not_found


# Finally, spin up our little app!
# if __name__ == "__main__":
#     app.run(debug=True, port=5000);
app.run
