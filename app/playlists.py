# This is the playlist microservice Python script.

import flask;
from flask import request, jsonify, g, Response;
import sqlite3;
import json, uuid
from itertools import chain

# Here we fire up an instance of our tracks app.
app = flask.Flask(__name__);
sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: buffer(u.bytes_le))
#app.config.from_envvar('APP_CONFIG');

# This is a helper function to convert the database rows returned into dictionaries.
def dict_factory(cursor, row):
    d = {};
    for (idx, col) in enumerate(cursor.description):
        d[col[0]] = row[idx];
    return d;
# End of dict_factory

# This is a helper function to modularize the database connection creation code.
def get_db():
    # First see if we have a current instance. If we do, just return it.
    # If not, then open a connection.
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("../var/microservices_db.db");
        db.row_factory = dict_factory;
    return db;
# End of get_db()

# This is a special helper function for clean-up detail. Currently, it is only
# used to tear down the database connection.
@app.teardown_appcontext
def close_connection(expection):
    # This close is similar to the code that sets up the database connection
    # but now in reverse!
    db = getattr(g, '_database', None);
    if db is not None:
        db.close();
# End of close_connection

# This is a helper function to check the uniqueness of an entry by checking if
# the (track,album,artist) tuple is already in the database.
def check_uniqueness(track, album, artist):
    cur = get_db().cursor();
    if cur.execute("SELECT * FROM tracks WHERE title=? AND album=? AND artist=?;",\
            (track, album, artist)).fetchone() is None:
        return True;
    return False;
# End of check_uniqueness

# This function runs when the user attempts to access the root of this microservice
# and all it does is spit out the REST API interface for the user to see the
# functionality
@app.route("/", methods=["GET"])
def tracks_home():
    return '''<h1>Welcome to the Playlist Microservice API!</h1>
    <p>This is a documentation page for the way to interface with
    the tracks microservice via Create, Retrieve, Delete, List All,
    and List All By User functions.</p>

    <h2>Create</h2>
    URL: <i>/api/v1/resources/playlists</i>, METHOD: POST <br/>
    <p>This function allows the user to add a new playlist to the table. The user
    will give it a title, the username of themselves, and an optional description.
    The List of URLs will be initalized to nothing to begin with.
    On success, it'll give the user back a 201 - Created.
    On failure, it'll return a 409 - Conflict. A failure is usually due to
    the playlist already existing in the database or lack of enough required
    data.</p>

    <p>Example Call: <br/>
        /api/v1/resource/tracks <br/>
        { <br/>
            "title":"Night City", <br/>
            "URLs_list":"", <br/>
            "user":"rkretschmar", <br/>
            "description":"A curated playlist of cyberpunk music for that
            high-tech, low-life mood.", <br/>
        }
    </p>

    <h2>Retrieve</h2>
    URL: <i>/api/v1/resources/tracks</i>, METHOD: GET <br/>
    <p>This function allows you to retrieve tracks from the tracks table. The user
    will perform a GET request on the tracks endpoint, and it will take the search
    parameters of track name, album name, and/or artist. It returns a 200 and the data
    if the data is in the table, and a 404 with an error message if not.

    <p>Example Call: <br/>
        /api/v1/resource/tracks?track_name=My+Slumbering+Heart&artist=Rilo+Kiley <br/>
    <b>Which returns:</b> <br/>
        { <br/>
            "track_name":"My Slumbering Heart", <br/>
            "album_name":"The Execution of All Things", <br/>
            "artist":"Rilo Kiley", <br/>
            "track_len":"5:36", <br/>
            "track_URL":"file://...", <br/>
            "art_URL":"file://..." <br/>
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
            "track_name":"", <br/>
            "album_name":"The Execution of All Things (Remastered)", <br/>
            "artist":"", <br/>
            "track_len":"4:30", <br/>
            "track_URL":"file://...", <br/>
            "art_URL":"" <br/>
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
# End of tracks_home()


#function to create a new playlist for a user from query parameter in the api endpoint
@app.route('/api/v1/resource/playlists/newplaylist',methods=['POST'])
def create_new_playlist():
    conn = get_db()
    cur = conn.cursor()
    query_parameters = request.args
    playlist_id_string= query_parameters.get("playlist_id")
    playlist_id = int(playlist_id_string)
    playlist_title = query_parameters.get("playlist_title")
    track_url = query_parameters.get("track_url")
    username = query_parameters.get("username")
    description = query_parameters.get("description")
    if playlist_id_string is not None and playlist_title is not None and track_url is not None and username is not None:
        try:
            playlist = (playlist_id, playlist_title,track_url,username,description)
            execute_string = "INSERT INTO playlists (playlist_id,playlist_title,track_url,username,description) VALUES (?,?,?,?,?);"
            result = cur.execute(execute_string, playlist)
            conn.commit()
            cur.close()
            #if items is None:
            return "<h1>Success!</h1><p>Congrat</p>", 201
            #else:
            #return Response(json.dumps(newuser_dict, sort_keys=False),headers={'Content-Type':'application/json'},status=201)
        except Exception as err:
            return ('Query Failed: %s\nError %s' % (''' INSERT INTO playlists''', str()))
    else:
        return ("input query parameters")


#retrieve all playlist from a user by playlist title and username
@app.route('/api/v1/resource/playlists/profile', methods = ['GET'])
def get_user_profile():
    conn = get_db()
    cur = conn.cursor()
    query_parameters = request.args
    playlist_title = query_parameters.get("playlist_title")
    username = query_parameters.get("username")
    query = "SELECT playlist_id, playlist_title, track_url, username, description FROM playlists WHERE playlist_title=? AND username=?"
    result = cur.execute(query, (playlist_title,username))
    items = cur.fetchall()

    # guid = [item.get("guid") for item in items]
    # print(type(guid))
    cur.close()
    if items is None:
        return page_not_found(404)
    else:
        return Response(json.dumps(items),mimetype="application/json",status=200)
        # return items
  

#delete a user's playlist
#query parameters: e.g. username=HLMN, playlist_title=Trending
@app.route('/api/v1/resource/playlists/removal', methods = ['DELETE'])
def delete_user():
    conn = get_db()
    cur = conn.cursor()
    username = request.args.get('username')
    playlist_title = request.args.get('playlist_title')
    if username is not None and playlist_title is not None:
        try:
            query = ''' DELETE FROM playlists WHERE playlist_title =? AND username = ?'''
            cur.execute(query,(playlist_title,username))
            conn.commit()
            cur.close()
            return Response( "200 OK,The user's playlist is deleted successfully", headers={'Content-Type':'application/json'},status=200)
        except Exception as err:
            return ('Query Failed: %s\nError: %s' % (''' DELETE FROM playlists''', str()))
    return ("input playlist_title and username as query parameters")


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
# app.run(debug=True, port=8080);
app.run()
