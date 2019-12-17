#!/usr/bin/env python3

import flask;
from flask import request, jsonify, g, Response;
import json
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

# Here we fire up an instance of our tracks app.
app = flask.Flask(__name__);
#app.config.from_envvar('APP_CONFIG');

def get_db_session():
    cluster = Cluster(['172.17.0.2'], port=9042)
    session = cluster.connect('xspf')
    return session


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


    <h2>Retrieve</h2>
    URL: <i>/api/v1/resource/playlists/profile</i>, METHOD: GET <br/>
    <p>This function allows you to retrieve a user's playlists. The user
    will perform a GET request on the playlists endpoint, and it will take the search
    parameters of playlist_title, username. It returns a 200 and the data
    if the data is in the table, and a 404 with an error message if not.

    <p>Example Call: <br/>
        /api/v1/resource/playlists/profile?playlist_title=Inspiring Songs&username=mandy <br/>
    <b>Which returns:</b> <br/>
    </p>


    <h2>Delete</h2>
    URL: <i>/api/v1/resource/playlists/removal</i>, METHOD: DELETE <br/>
    <p>This function allows a user to delete a playlist by playlist_title and username parameters.
    This function returns a 200 OK on success, and a 404 Not Found if the record didn't
    exist in the table to begin with.</p>

    <p>Example Call: <br/>
        /api/v1/resource/playlists/removal?playlist_title=Inspiring Songs&username=mandy<br/>
    </p>
    '''
# End of tracks_home()


#function to create a new playlist
@app.route('/api/v1/resource/playlists/newplaylist',methods=['POST'])
def create_new_playlist():
    session = get_db_session()
    query_parameters = request.args
    playlist_id_string= query_parameters.get("playlist_id")
    playlist_id = int(playlist_id_string)
    playlist_title = query_parameters.get("playlist_title")
    playlist_description = query_parameters.get("playlist_description")
    username = query_parameters.get("username")
    track_id_string = query_parameters.get("track_id")
    track_id = int(track_id_string)
    track_title = query_parameters.get("track_title")
    track_album = query_parameters.get("track_album")
    track_artist = query_parameters.get("track_artist")
    track_len = query_parameters.get("track_len")
    track_media_url =  query_parameters.get("track_media_url")
    track_art_url =  query_parameters.get("track_art_url")
    track_desc = query_parameters.get("track_desc")

    if playlist_id_string is not None and playlist_title is not None and username is not None:
        try:
            playlist = (playlist_id, playlist_title,playlist_description, username, track_id, track_title, \
                        track_album, track_artist, track_len, track_media_url, track_art_url, track_desc)
            session.execute(
                """
                INSERT INTO playlists_by_playlist_id_and_username(playlist_id, playlist_title,playlist_description, username, track_id, track_title, \
                            track_album, track_artist, track_len, track_media_url, track_art_url, track_desc)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                playlist
            )
            #if items is None:
            return "<h1>Success!</h1><p>Congrat</p>", 201
            #else:
            #return Response(json.dumps(newuser_dict, sort_keys=False),headers={'Content-Type':'application/json'},status=201)
        except Exception as err:
            return ('Query Failed: %s\nError %s' % (''' INSERT INTO playlists''', str()))
    else:
        return ("input query parameters")


#retrieve all playlist from a user by playlist id
@app.route('/api/v1/resource/playlists/profile', methods = ['GET'])
def get_user_profile():
    session = get_db_session()
    query_parameters = request.args
    playlist_id_query_string = query_parameters.get("playlist_id_string")
    playlist_id_query = int(playlist_id_query_string)
    session.row_factory = dict_factory
    query = "SELECT * FROM playlists_by_playlist_id_and_username WHERE playlist_id= %s"
    rows = session.execute(query,[playlist_id_query])
    print(rows)
    if rows is None:
        return page_not_found(404)
    else:
        data = []
        for row in rows:
            data.append(row)
        print(data)
        print(json.dumps(data))
        return Response(json.dumps(data, indent=4, sort_keys=False), 200, {'Content-Type': 'application/json'})


#delete a user's playlist by playlist id
@app.route('/api/v1/resource/playlists/removal', methods = ['DELETE'])
def delete_user():
    session = get_db_session()
    query_parameters = request.args
    playlist_id_query_string = query_parameters.get("playlist_id_string")
    playlist_id_query = int(playlist_id_query_string)
    if playlist_id_query_string is not None:
        try:
            query = "DELETE FROM playlists_by_playlist_id_and_username WHERE playlist_id = %s"
            session.execute(query,[playlist_id_query])
            return Response( "200 OK,The user's playlist is deleted successfully", headers={'Content-Type':'application/json'},status=200)
        except Exception as err:
            return ('Query Failed: %s\nError: %s' % (''' DELETE FROM playlists''', str()))


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
# app.run(debug=True, port=5100);
app.run()
