#!/usr/bin/env python3
import requests, flask
import json
from flask import render_template, Flask,  make_response, g, Response, jsonify
import jinja2
from helper.helper import get_track_data
from pymemcache.client import base

app = Flask(__name__, template_folder='templates')

#start the memcached server
client = base.Client(('localhost',11211))

def get_user_data(username):
	url = "http://127.0.0.1:5200/api/v1/resource/users/profile?username=" +username
	response = requests.get(url).text
	res2= json.loads(response)
	dname = res2[0]["displayname"]
	return dname


#function to get a playlist full data by playlist_id string
#in the main function, the string is converted to int
#to align with cassandra database defined datatype
def get_playlist_data(playlist_id_string):
	url = "http://127.0.0.1:5100/api/v1/resource/playlists/profile?playlist_id_string="+playlist_id_string
	response = requests.get(url).text
	res2= json.loads(response)
	return res2

#query a playlist by its playlist_title, and username
#as usually peoply remember the title and their own username
def get_a_playlist_data_for_xspf(playlist_id_string):
	response = get_playlist_data(playlist_id_string)

	playlist_id = [item.get("playlist_id") for item in response]
	playlist_title = [item.get("playlist_title") for item in response]
	playlist_description = [item.get("playlist_description") for item in response]
	username = [item.get("username") for item in response]
	track_id = [item.get("track_id") for item in response]
	track_title = [item.get("track_title") for item in response]
	track_album = [item.get("track_album") for item in response]
	track_artist = [item.get("track_artist") for item in response]
	track_len = [item.get("track_len") for item in response]
	track_media_url = [item.get("track_media_url") for item in response]
	track_desc = [item.get("track_desc") for item in response]

	tracks_list = []
	for i in range(len(track_id)):
		title = track_title[i]
		artist = track_artist[i]
		album = track_album[i]
		length = track_len[i]
		media_url = track_media_url[i]
		desc = track_desc[i]
		v = {'title': title, 'artist': artist, 'album': album, 'location': media_url,'track_desc':desc}
		tracks_list.append(v)

	displayname = get_user_data(username[0])
	d = "playlist_" + playlist_id_string

	data = {d:{"title": playlist_title[0], "creator": displayname ,"info": playlist_description[0], "tracks_list": tracks_list}}
	return data
	# return data, playlist_id[0]

#home
@app.route('/')
def home():
	return '''<h1>Welcome to the xspf Microservice!</h1>
    <p>It will generate xspf xml file for a playlist.</p>

    <h2>to run it</h2>
    from terminal: python xspf.py,
    <h2> visit: http://localhost:8000/playlist/1 <br/>
    <p>This will bring you a generator to generate a xspf playlist</p>'''

#queary the xspf playlist by a playlist id
@app.route('/playlist/<playlist_id_string>')
def get_playlist_xml(playlist_id_string):
# def get_playlist_xml(playlist_title, username):
	# global title,artist,album,length,media_url
	# global displayname
	d="playlist_" + playlist_id_string

	result = client.get(d)
	if result is not None:
		data = result
		return data
	else:
		data  = get_a_playlist_data_for_xspf(playlist_id_string)
		client.add(d, data, 60)

	template = render_template('xspf.xml', values=data[d]["tracks_list"],displayname=data[d]["creator"],\
				playlist_title=data[d]["title"],playlist_description=data[d]["info"])
	response = make_response(template)
	response.headers['Content-Type'] = 'application/xml'
	return response

if __name__ == "__main__":
	app.run(port=5400)
# app.run()
