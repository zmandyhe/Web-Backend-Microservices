# This is the tracks microservice Python script.

import flask;
from flask import request, jsonify, g;
import sqlite3;

# Here we fire up an instance of our tracks app.
app = flask.Flask(__name__);
app.config["DEBUG"] = True;

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
        db = g._database = sqlite3.connect("../var/micro_playlist.db");
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
    return '''<h1>Welcome to the tracks microservice API!</h1>
    <p>This is a documentation page for the way to interface with
    the tracks microservice via Create, Retrieve, Edit, and Delete functions.</p>

    <h2>Create</h2>
    URL: <i>/api/v1/resources/tracks</i>, METHOD: POST
    <p>This function allows you to add new tracks to the database through
    a POST request. On success, it'll give the user back a 201 - Created.
    On failure, it'll return a 409 - Conflict. A failure is usually due to
    the track already existing in the database or lack of enough required
    data.</p>

    <p>Example Call:
        /api/v1/resource/tracks
        {
            "track_name":"I Ain't Got Time",
            "album_name":"Flower Boy",
            "artist":"Tyler, The Creator",
            "track_len":"3:25",
            "track_URL":"file://...",
            "art_URL":"file://..."
        }
    </p>

    <h2>Retrieve</h2>
    URL: <i>/api/v1/resources/tracks</i>, METHOD: GET
    <p>This function allows you to retrieve tracks from the tracks table. The user
    will perform a GET request on the tracks endpoint, and it will take the search
    parameters of track name, album name, and/or artist. It returns a 200 and the data
    if the data is in the table, and a 404 with an error message if not.

    <p>Example Call:
        /api/v1/resource/tracks?track_name=My+Slumbering+Heart&artist=Rilo+Kiley
    Which returns:
        {
            "track_name":"My Slumbering Heart",
            "album_name":"The Execution of All Things",
            "artist":"Rilo Kiley",
            "track_len":"5:36",
            "track_URL":"file://...",
            "art_URL":"file://..."
        }
    </p>
    '''
# End of tracks_home()

# This function runs when the users attempts to add a track to the library.
#   On success, return a 201 - Created
#   On failure, return a 409 - Conflict
@app.route("/api/v1/resources/tracks", methods=["POST"])
def track_create():
    # First, we need to make sure that the required fields are populated. These
    # are the Title, Album Title, Artist, Length, and the URL for file. There is
    # one field that is optional which is the URL for the Album Art.
    error = None;
    if not request.form['track_name']:
        error = "Track Name Missing!";
    elif not request.form['album_name']:
        error = "Album Name Missing!";
    elif not request.form['artist']:
        error = "Artist Name Missing!"
    elif not request.form['track_len']:
        error = "Track Length Missing!"
    elif not request.form["track_URL"]:
        error = "Track's URL Missing!"

    # Next, we check that the this specific track doesn't already exist. However,
    # just the track name won't be unique enough since it could be a cover or on
    # two seperate albums. For this reason, we're going to check it see if the
    # combination of track, artist, and album should be unique enough.
    elif check_uniqueness(request.form['track_name'], request.form['album_name'],
            request.form['artist']) is False:
        error = "This track already exists in the database!";
    else:
        # Given that we haven't failed any of the above checks, we are ready to
        # open a connection and insert the new record.
        conn = get_db();
        cur = conn.cursor();
        cur.execute("INSERT INTO tracks(title, album, artist, len, track_url, art_url) \
                VALUES(?,?,?,?,?,?);", (request.form['track_name'], request.form['album_name'],\
                request.form['artist'], request.form['track_len'], request.form['track_URL'],\
                request.form['art_URL']));
        conn.commit();

    if error:
        ret_str = "<h1>Oops!</h1> <p>Looks like there was a problem inserting a new record \
                into the database: " + error + "</p>";
        return ret_str, 409;
    else:
        ret_str = "<h1>Success!</h1><p>This record was successfully added to the service!</p> \
                Track: " + request.form['track_name'] + \
                "Album: " +  request.form['album_name'] + \
                "Artist: " + request.form['artist'] + \
                "Length: " + request.form['track_len'] + \
                "Track URL: " +  request.form['track_URL'] + \
                "Art URL: " +  request.form['art_URL'];

        return ret_str, 201
# End of track_create()

# This function runs when the users attempts to retrieve a track from the
# database. The user can use any combination of the track name, album name,
# or artist as a search query.
#   On success, return a 200 - OK, with the data
#   On failure, return a 404 - Not Found, with an error
# NOTE: This code follows very closely to the code provided to us in the Science
# Fiction Book example.
@app.route("/api/v1/resources/tracks", methods=["GET"])
def track_retrieve():
    # Since we're going to be using the incoming variables a lot, let's get
    # them into more managable variables.
    query_params = request.args;
    track = query_params.get('track_name');
    album = query_params.get('album_name');
    artist = query_params.get('artist');

    # Now we can check to see which items the user submitted, and build our
    # query string.
    query = "SELECT * FROM tracks WHERE";
    to_filter = [];

    if track:
        query += ' title=? AND';
        to_filter.append(track);
    if album:
        query += ' album=? AND';
        to_filter.append(album);
    if artist:
        query += ' artist=? AND';
        to_filter.append(artist);
    if not (track or album or artist):
        return "<h1>You must fill in at least one search query term!</h1>", 404;

    # Do some final trimming and append a semicolon onto our query
    query = query[:-4] +';';

    # Finally, query the database and return the results!
    cur = get_db().execute(query, to_filter);
    results = cur.fetchall();
    cur.close();

    if results:
        return jsonify(results), 200;
    else:
        return "<h1>Failure</h1><p>It seems that there's nothing in the database \
                that matches those search parameters.</p><p>Please try again!</p>", 404;
# End of track_retrieve()

# This function runs when the users attempts to edit a track from the
# database. The user can search
#   On success, return a 200 - OK, with the data
#   On failure, return a 404 - Not Found, with an error
# NOTE: This code follows very closely to the code provided to us in the Science
# Fiction Book example.
#@app.route("/api/v1/resources/tracks", methods=["GET"])
#def track_retrieve():


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
app.run();
