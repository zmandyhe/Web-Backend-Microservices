from flask import Flask, request, jsonify, g, Response
import json
from cassandra.cluster import Cluster
from cassandra.query import dict_factory


app = Flask(__name__)
#app.config.from_envvar('APP_CONFIG')


# This is a helper function to modularize the database connection
def get_db_session():
    cluster = Cluster(['172.17.0.2'], port=9042)
    session = cluster.connect('xspf')
    return session


'''helper function'''
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


'''homepage'''
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome to the Description Microservice API!</h1>
        <p>This is a documentation page for the way to interface with
        the description microservice via Create a track's description,and, Retrieve a track's description functions.</p>

        <h2>Create</h2>
        URL: <i>/api/v1/resources/desc/newdesc</i>, METHOD: POST <br/>
        <p>This function allows a user to add new description to a track to the database through
        a POST request. On success, it'll give the user back a 201 - Created.
        On failure, it'll return a 404 - Conflict. .</p>

        <p>Example Call: <br/>
            /api/v1/resource/tracks , METHOD: POST<br/>
            { <br/>
                "username":"mandy", <br/>
                "track_id": 004, <br/>
                "trackdesc":"Like the sound of silence calling,I hear your voice and suddenly I'm falling,Lost in a dream,Like the echoes of our souls are meeting." <br/>
            }
        </p>

        <h2>Retrieve</h2>
        URL: <i>/api/v1/resources/desc/profile</i>, METHOD: GET <br/>
        <p>This function allows you to retrieve a track's description. The user
        will perform a GET request on the tracks endpoint, and it will take the search
        parameters of track_url. It returns a 200 and the data
        if the data is in the table, and a 404 with an error message if not.

        <p>Example Call: <br/>
            /api/v1/resource/tracks?track_id=004 <br/>
        <b>Which returns:</b> <br/>
            { <br/>
                "username":"mandy", <br/>
                "track_id": 004, <br/>
                "trackdesc":"Like the sound of silence calling,I hear your voice and suddenly I'm falling,Lost in a dream,Like the echoes of our souls are meeting." <br/>
            }
        </p>'''


#endpoint to retrieve a user description of a track description'
# it shares the table of playlists_by_playlist_id_and_username
#when playlist is not created, it assigns the playlist_id = 0
@app.route('/api/v1/resources/desc/profile', methods = ['GET'])
def get_track_profile():
    playlist_id = 0
    session = get_db_session()
    query_parameters = request.args
    track_id_s = query_parameters.get("track_id_string")
    track_id = int(track_id_s)
    username_query = query_parameters.get("username")
    session.row_factory = dict_factory
    query = "SELECT * FROM playlists_by_playlist_id_and_username WHERE playlist_id=%s AND track_id=%s AND username= %s"
    rows = session.execute(query,(playlist_id, track_id, username_query))
    if rows is None:
        return page_not_found(404)
    else:
        data = []
        for row in rows:
            data.append(row)
        print(json.dumps(data))
        return Response(json.dumps(data, indent=4, sort_keys=False), 200, {'Content-Type': 'application/json'})


#function to set a track's description by a user
@app.route('/api/v1/resources/desc/newdesc',methods=['POST'])
def create_track_desc():
    session = get_db_session()
    query_parameters = request.args
    playlist_id = 0
    track_id = int(query_parameters.get("track_id_string"))
    username = query_parameters.get("username")
    desc = query_parameters.get("track_desc")
    if username is not None and track_id is not None and desc is not None:
        try:
            trackdesc = (playlist_id, track_id, username, desc)
            session.execute(
                """
                INSERT INTO playlists_by_playlist_id_and_username (playlist_id, track_id, username, track_desc)
                VALUES (%s, %s, %s, %s)
                """,
                trackdesc
            )
            return ("<h2>Success, new track description has been successfully created!</h2>",201)
        except Exception as err:
            return ("Query of insert failed")
    else:
        return ("input query parameter")


# if __name__ == "__main__":
#     app.run(debug=True, port=6789)
app.run()
