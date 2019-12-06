from flask import Flask, request, jsonify, g, Response
import sqlite3
import json
from werkzeug.security import generate_password_hash,check_password_hash
#from os.path import isfile


app = Flask(__name__)
#app.config.from_envvar('APP_CONFIG')

'''helper function'''
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

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
                "track_url":"http://127.0.0.1:5000/api/v1/resources/tracks/b7c25310-6750-4c2b-91a9-eaf44b0c198", <br/>
                "trackdesc":"Like the sound of silence calling,I hear your voice and suddenly I'm falling,Lost in a dream,Like the echoes of our souls are meeting." <br/>
            }
        </p>

        <h2>Retrieve</h2>
        URL: <i>/api/v1/resources/desc/profile</i>, METHOD: GET <br/>
        <p>This function allows you to retrieve a track's description from the tracks table. The user
        will perform a GET request on the tracks endpoint, and it will take the search
        parameters of track_url. It returns a 200 and the data
        if the data is in the table, and a 404 with an error message if not.

        <p>Example Call: <br/>
            /api/v1/resource/tracks?track_url="http://127.0.0.1:5000/api/v1/resources/tracks/b7c25310-6750-4c2b-91a9-eaf44b0c198" <br/>
        <b>Which returns:</b> <br/>
            { <br/>
                "username":"mandy", <br/>
                "track_url":"http://127.0.0.1:5000/api/v1/resources/tracks/b7c25310-6750-4c2b-91a9-eaf44b0c198", <br/>
                "trackdesc":"Like the sound of silence calling,I hear your voice and suddenly I'm falling,Lost in a dream,Like the echoes of our souls are meeting." <br/>
            }
        </p>'''


#endpoint to retrieve a user description of a track description'
@app.route('/api/v1/resources/desc/profile', methods = ['GET'])
def get_user_profile():
    conn = get_db()
    cur = conn.cursor()
    query_parameters = request.args
    # username = query_parameters.get("username")
    track_url= query_parameters.get("track_url")
    if track_url is not None:
        # query = "SELECT username,track_url,trackdesc FROM desc WHERE username=username AND track_url=track_url"
        query = "SELECT trackdesc FROM desc WHERE track_url=track_url"
        result = cur.execute(query)
        #items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
        items = cur.fetchone()
        cur.close()
        if items is None:
            return page_not_found(404)
        else:
            return Response(json.dumps(items, sort_keys=False),headers={'Content-Type':'application/json'},status=200)
    else:
        return ("input query parameter with track_url= track_url")


#function to set a track's description by a user
@app.route('/api/v1/resources/desc/newdesc',methods=['POST'])
def sql_set_desc():
    # conn = sqlite3.connect('desc.db', check_same_thread=False)
    conn = get_db()
    cur = conn.cursor()
    query_parameters = request.args
    username = query_parameters.get("username")
    trackdesc = query_parameters.get("trackdesc")
    track_url = query_parameters.get("track_url")
    track_desc = (username,trackdesc,track_url)
    # desc_dict = convert_to_json()
    # user_desc = (desc_dict["username"], desc_dict["tracktitle"],desc_dict["trackdesc"])
    cur.execute(''' INSERT INTO desc (username,trackdesc,track_url) VALUES (?,?,?) ''', track_desc)
    conn.commit()
    #items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
    items = cur.fetchall()
    cur.close()
    if items is None:
        return page_not_found(404)
    else:
        #return items
        return Response(json.dumps(track_desc, indent=4),mimetype="application/json",status=201)


app.run()
# if __name__ == "__main__":
#     app.run(debug=True, port=6789)
