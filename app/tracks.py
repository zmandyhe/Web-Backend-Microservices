# This is the tracks microservice Python script.

import flask;
from flask import request, jsonify, g;
import sqlite3;

# Here we fire up an instance of our tracks app.
app = flask.Flask(__name__);
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
            "track_name":"I Ain't Got Time", <br/>
            "album_name":"Flower Boy", <br/>
            "artist":"Tyler, The Creator", <br/>
            "track_len":"3:25", <br/>
            "track_URL":"file://...", <br/>
            "art_URL":"file://..." <br/>
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
# database. The user can search for a track and then edit it. This will use the
# PUT HTTP verb. Since we're essientally going to get two pieces of information
# from the user (i.e. a query to look up, and the data to replace it with) that
# we're going to use the GET "way" of argument passing in the URL for the search
# query, and the POST way of getting the body contents for the updated information.
#   On success, return a 200 - OK, with the updated data
#   On failure, return a 404 - Not Found, with an error
# NOTE: This will only deal with finding a single track -- unlike the retrieval
# function -- since editing multiple tracks is difficult without a solid front-end.
@app.route("/api/v1/resources/tracks", methods=["PUT"])
def track_edit():
    # This will repeat the search functionality of the retrieve method, but
    # slimmed down for editing.
    track = request.args.get('track_name');

    # Make sure the user typed in a track title to look up
    if not track:
        return "<h1>Failure</h1><p>You must specify a track name in the URL \
        to look up!</p>", 404;

    # And check to see if it's in the database
    query = "SELECT * FROM tracks WHERE title=?;";
    cur = get_db().execute(query, [track]);
    result = cur.fetchall();
    cur.close();

    if not result:
        return "<h1>Failure!</h1><p>The track that you've searched for is not \
        in the database. Either correct your spelling, or try adding it to \
        the database first!</p>", 404;

    # Next, we parse the update information by checking to see if the user suppied
    # the information. For each field they supplied information to, we'll collect
    # them and pass them as a parameter list to an execute function.
    query = "UPDATE tracks SET";
    update_info = [];

    # NOTE: Current issue with this method is finding out if a user populated any
    # of these fields with information meanwhile needing the ones that aren't changed
    # to still be there, just without information.
    if request.form['track_name']:
        query += ' title=?,';
        update_info.append(request.form['track_name']);
    if request.form['album_name']:
        query += ' album=?,';
        update_info.append(request.form['album_name']);
    if request.form['artist']:
        query += ' artist=?,';
        update_info.append(request.form['artist']);
    if request.form['track_len']:
        query += '  len=?,';
        update_info.append(request.form['track_len']);
    if request.form['track_URL']:
        query += ' track_url=?,';
        update_info.append(request.form['track_URL']);
    if request.form['art_URL']:
        query += ' art_url=?,';
        update_info.append(request.form['art_URL']);

    # Remove the trailing comma, and finish the rest of the query string.
    query = query[:-1] + " WHERE title=?;";
    update_info.append(track);
    # Execute the update
    conn = get_db()
    cur = conn.cursor();
    cur.execute(query, update_info);
    conn.commit();
    cur.close();

    return "<h1>Success!</h1><p>You have updated the information of record: " \
            + track + "!</p>", 200;
# End of track_edit()

# This function allows the user to delete tracks from the database. It's going
# to work along the same lines as the edit function, but just a bit simpler since
# it needs to only delete the record.
#   On success, return a 200 - OK, with a positive message
#   On failure, return a 404 - Not Found, with an error
@app.route("/api/v1/resources/tracks", methods=["DELETE"])
def track_delete():
    # This will repeat the search functionality of the retrieve method, but
    # slimmed down for deleting
    track = request.args.get('track_name');

    # Make sure the user typed in a track title to look up
    if not track:
        return "<h1>Failure</h1><p>You must specify a track name in the URL \
        to look up!</p>", 404;

    # And check to see if it's in the database
    query = "SELECT * FROM tracks WHERE title=?;";
    cur = get_db().execute(query, [track]);
    result = cur.fetchall();
    cur.close();

    if not result:
        return "<h1>Failure!</h1><p>The track that you've searched for is not \
        in the database. Either correct your spelling, or try adding it to \
        the database first!</p>", 404;

    # So, now we know the record exists, and we can safely delete it.
    query = "DELETE FROM tracks WHERE title=?;";
    conn = get_db()
    cur = conn.cursor();
    cur.execute(query, [track]);
    conn.commit();
    cur.close();

    return "<h1>Success!</h1><p>You have deleted the record of track: " \
            + track + "!</p>", 200;
# End of track_delete()

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
