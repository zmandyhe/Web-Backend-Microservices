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

#for test purpose, only convert 1 row of json data
def convert_to_json():
    with open('desc/desc.txt') as json_file:
        data = json.load(json_file)
        desc=(data["username"],data["tracktitle"],data["trackdesc"])
        desc={"username": data["username"], "tracktitle": data["tracktitle"],"trackdesc": data["trackdesc"]}
    return desc


'''homepage'''
@app.route('/', methods=['GET'])
def home():
    return'''<h1> Welcome to Description Microservice </h1>'''


'''endpoint to retrieve a user's description of a track'''
@app.route('/api/v1/resources/desc/profile', methods = ['GET'])
def get_user_profile():
    # conn = sqlite3.connect('desc.db', check_same_thread=False)
    conn = sqlite3.connect('../var/micro_playlist.db', check_same_thread=False)
    cur = conn.cursor()
    query_parameters = request.args
    username = query_parameters.get("username")
    track_url= query_parameters.get("track_url")
    if username is not None and track_url is not None:
        query = "SELECT username,track_url,trackdesc FROM desc WHERE username=username AND track_url=track_url"
        result = cur.execute(query)
        items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
        cur.close()
        if items is None:
            return page_not_found(404)
        else:
            return Response(json.dumps(items, sort_keys=False),headers={'Content-Type':'application/json'},status=200)
    else:
        return ("input query parameter with ?username=your-query-username & tracktitle=your-query-tracktitle")


#function to set a track's description by a user
@app.route('/api/v1/resources/desc/newdesc',methods=['POST'])
def sql_set_desc():
    # conn = sqlite3.connect('desc.db', check_same_thread=False)
    conn = sqlite3.connect('../var/micro_playlist.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
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


if __name__ == "__main__":
    app.run(debug=True, port=6789)
