# -*- coding: utf-8 -*-

import requests, flask
import json
from flask import render_template, Flask,  make_response, g, Response, jsonify
import jinja2, sqlite3, uuid
from itertools import chain
import json, ast
from helper import helper

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: buffer(u.bytes_le))

app = Flask(__name__, template_folder='templates')


#function to call playlist API to get a playlist's track_url
def get_playlist_data(playlist_title,username):
	url = "http://127.0.0.1:5100/api/v1/resource/playlists/profile?playlist_title="+playlist_title+"&username="+username
	response = requests.get(url).text
	res2= json.loads(response)
	track_urls = [item.get("track_url") for item in res2]
	list_guid=[item.split('/')[-1] for item in track_urls]
	guid_list = [uuid.UUID(item) for item in list_guid]
	return guid_list,track_urls


def get_user_data(username):
	url = "http://127.0.0.1:5200/api/v1/resource/users/profile?" + "username=" +username
	response = requests.get(url).text
	res2= json.loads(response)
	displayname = res2[1]
	return displayname


def get_track_description(track_url):
	url = "http://127.0.0.1:5300/api/v1/resources/desc/profile?track_url="+track_url
	response = requests.get(url).text
	res2= json.loads(response)
	return res2

#home
@app.route('/')
def home():
	return '''<h1>Welcome to the xspf Microservice!</h1>
    <p>It will generate xspf xml file for a playlist.</p>

    <h2>to run it</h2>
    from terminal: python xspf.py, 
    <h2> visit: http://localhost:8000/playlist/1 <br/>
    <p>This will bring you a generator to generate a xspf playlist</p>'''

#this is main app to start in order to generate a playlist xspf xml file
@app.route('/playlist/<playlist_id>')
def get_playlist_xml(playlist_id):
	global title,artist,album,length,media_url
	global displayname
	playlist_title="Inspiring Songs"
	username = "mandy"
	guid_list,track_urls = get_playlist_data(playlist_title, username)
	guid = []
	for i in range(len(guid_list)):
		guid.append(guid_list[i])
	values_list = []
	for j in range(len(guid)):
		# title,artist,album,length,media_url = get_track_data(guid[j])
		title,artist,album,length,media_url = helper.get_track_data(guid[j])
		t_desc = get_track_description(track_urls[j])
		track_desc = ast.literal_eval(json.dumps(t_desc))
		v = {'title': title, 'artist': artist, 'album': album, 'location': media_url,'track_desc':track_desc}
		values_list.append(v)

	displayname = get_user_data(username) #creator of a playlist

	values = values_list

	template = render_template('xspf.xml', values=values, displayname=displayname, playlist_title=playlist_title)
	response = make_response(template)
	response.headers['Content-Type'] = 'application/xml'
	return response

if __name__ == "__main__":
	app.run(port=8000)
