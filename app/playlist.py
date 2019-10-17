from flask import Flask, request, jsonify, g, Response
import sqlite3
import json
from werkzeug.security import generate_password_hash,check_password_hash
from os.path import isfile

app = Flask(__name__)
#app.config.from_envvar('APP_CONFIG')


"""
helper functions
"""
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

#for test purpose, only convert 1 row of json data
def convert_to_json():
    with open('playlists/playlist.txt') as json_file:
        data = json.load(json_file)
        d=(data["playlist_title"],data["playlist_track_url"],data["username"],data["description"])
        playlist={"playlist_title": data["playlist_title"],"playlist_track_url": data["playlist_track_url"], "username": data["username"],"description": data["description"]}
    return playlist


#homepage
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome to Playlist Microservice</h1>
<h2> '/api/v1/resource/playlists/all', methods=['GET'] to list all playlist </h2>
<h2> Create a new playlist by input query parameters</h2>
<p> api/v1/resource/playlists/new, methods=['POST'] </p>
<p> query example: /api/v1/resource/playlists/new?playlist_title=popular&username=mandy&playlist_track_url=http://www.google.com&description=yes it is the most popular music for today.</p>
<h2>Retrieve a playlist for a user </h2>
<p> /api/v1/resource/playlists/profile, methods = ['GET'] </p>
<h2> Delete a user's playlist </h2>
<p> api/v1/resource/playlists/removal, methods = ['DELETE'] </p>
<h2> Lists playlists created by a particular user </h2>
<p>/api/v1/resource/playlists/user_all', methods=['GET']</p>
<h2>List all playlists</h2>
<p> api/v1/resource/playlists/all, methods=['GET'] </p>'''


#list all playlists
@app.route('/api/v1/resource/playlists/all', methods=['GET'])
def list_all_users():
    # conn = sqlite3.connect('playlists/playlists.db', check_same_thread=False)
    conn = sqlite3.connect('../var/micro_playlist.db', check_same_thread=False)
    cur = conn.cursor()
    #query_parameters = request.args
    #username = query_parameters.get("username")
    query = "SELECT * FROM playlists;"
    result = cur.execute(query)
    #items = cur.fetchall()
    items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
    cur.close()
    if items is None:
        return page_not_found(404)
    else:
        return Response(json.dumps(items[0], sort_keys=False), 200, {'Content-Type': 'application/json'})

#list all user's playlists
@app.route('/api/v1/resource/playlists/user_all', methods=['GET'])
def list_user_all():
    # conn = sqlite3.connect('playlists/playlists.db', check_same_thread=False)
    conn = sqlite3.connect('../var/micro_playlist.db', check_same_thread=False)
    cur = conn.cursor()
    query_parameters = request.args
    username = query_parameters.get("username")
    query = "SELECT * FROM playlists WHERE username=?;"
    result = cur.execute(query, [username])
    items = cur.fetchall()
    #items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
    cur.close()
    if items is None:
        return page_not_found(404)
    else:
        return Response(json.dumps(items[0], sort_keys=False), 200, {'Content-Type': 'application/json'})


#function to create a new playlist for a user from query parameter in the api endpoint
@app.route('/api/v1/resource/playlists/new',methods=['POST'])
def sql_create_user_by_input():
    # conn = sqlite3.connect('playlists/playlists.db', check_same_thread=False)
    conn = sqlite3.connect('../var/micro_playlist.db', check_same_thread=False)
    cur = conn.cursor()
    query_parameters = request.args
    playlist_title = query_parameters.get("playlist_title")
    #will read tracks table to get it
    playlist_track_url = query_parameters.get("playlist_track_url")
    username = query_parameters.get("username")
    description = query_parameters.get("description")
    newuser_dict={"playlist_title":playlist_title,
                "playlist_track_url": playlist_track_url,
                 "username": username,
                 "description": description}
    if playlist_title is not None and playlist_track_url is not None and username is not None:
        try:
            playlist = (playlist_title, playlist_track_url, username)
            if description is not None:
                playlist.append(description);

            execute_string = "INSERT INTO playlists(playlist_title, playlist_track_url, username"
            if description is not None:
                execute_string += ", description) "
            else:
                execute_string += ") "
            execute_string += "VALUES (?,?,?"
            if description is not None:
                execute_string += ",?);"
            else:
                execute_string += ");"
            result = cur.execute(execute_string, playlist)
            conn.commit()
            #items = cur.fetchall()
            #items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
            cur.close()
            #if items is None:
            return "<h1>Success!</h1><p>Congrats!</p>", 201
            #else:
            #return Response(json.dumps(newuser_dict, sort_keys=False),headers={'Content-Type':'application/json'},status=201)
        except Exception as err:
            return ('Query Failed: %s\nError %s' % (''' INSERT INTO playlists''', str()))
    else:
        return ("input query parameters")
#End create_sql

#retrieve all playlist from a user
@app.route('/api/v1/resource/playlists/profile', methods = ['GET'])
def get_user_profile():
    # conn = sqlite3.connect('playlists/playlists.db', check_same_thread=False)
    conn = sqlite3.connect('../var/micro_playlist.db', check_same_thread=False)
    cur = conn.cursor()
    conn.row_factory = sqlite3.Row
    query_parameters = request.args
    playlist_title = query_parameters.get("playlist_title")
    username = query_parameters.get("username")
    query = "SELECT playlist_title, playlist_track_url,username,description FROM playlists WHERE playlist_title=? AND username=?"
    result = cur.execute(query, (playlist_title,username))
    #items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
    items = cur.fetchall()
    cur.close()
    if items is None:
        return page_not_found(404)
    else:
        return Response(json.dumps(items[0]),mimetype="application/json",status=200)


#delete a user's playlist
#query parameters: e.g. username=HLMN, playlist_title=Trending
@app.route('/api/v1/resource/playlists/removal', methods = ['PUT'])
def delete_user():
    # conn = sqlite3.connect('playlists/playlists.db', check_same_thread=False)
    conn = sqlite3.connect('../var/micro_playlist.db', check_same_thread=False)
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


if __name__ == "__main__":
    app.run(debug=True)
