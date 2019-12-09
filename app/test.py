# -*- coding: utf-8 -*-

import requests, flask
import json
from flask import render_template, Flask,  make_response, g, Response, jsonify
import jinja2, sqlite3, uuid
from itertools import chain
import json, ast
from helper import helper
from pymemcache.client import base

track_url = "http://127.0.0.1:5000/api/v1/resources/tracks/b7c25310-6750-4c2b-91a9-eaf44b0c1981"
url = "http://127.0.0.1:5300/api/v1/resources/desc/profile?track_url="+track_url
response = requests.get(url).text
res2 = json.loads(response)
# print(type(res2))

# print(type(res))
# print(type(response))
description = res2["trackdesc"]
# print(res2)
# description = [response[key] for key in response]
# print(description)
# print(response)

# sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
# sqlite3.register_adapter(uuid.UUID, lambda u: buffer(u.bytes_le))


# app = Flask(__name__, template_folder='templates')

# def get_playlist_data(playlist_title, username):
# 	url = "http://127.0.0.1:5100/api/v1/resource/playlists/profile?playlist_title="+playlist_title+"&username="+username
# 	response = requests.get(url).text
# 	res2= json.loads(response)
# 	playlist_id = [item.get("playlist_id") for item in res2]
# 	track_urls = [item.get("track_url") for item in res2]
# 	list_guid=[item.split('/')[-1] for item in track_urls]
# 	guid_list = [uuid.UUID(item) for item in list_guid]
# 	return guid_list,track_urls,playlist_id

# def get_user_data(username):
# 	url = "http://127.0.0.1:5200/api/v1/resource/users/profile?" + "username=" +username
# 	response = requests.get(url).text
# 	res2= json.loads(response)
# 	displayname = res2[1]
# 	return displayname


# def get_track_description(track_url):
# 	url = "http://127.0.0.1:5300/api/v1/resources/desc/profile?track_url="+track_url
# 	response = requests.get(url).text
# 	res2= json.loads(response)
# 	return res2


# #function to call playlist API to get a playlist's track_url
# # def get_playlist_data(playlist_title,username):
# # 	url = "http://127.0.0.1:5100/api/v1/resource/playlists/profile?playlist_title="+playlist_title+"&username="+username
# # 	response = requests.get(url).text
# # 	res2= json.loads(response)
# # 	track_urls = [item.get("track_url") for item in res2]
# # 	list_guid=[item.split('/')[-1] for item in track_urls]
# # 	guid_list = [uuid.UUID(item) for item in list_guid]
# # 	return guid_list,track_urls
# with app.app_context():
#     # within this block, current_app points to app.
# 	global title,artist,album,length,media_url
# 	global displayname
# 	playlist_title="Inspiring Songs"
# 	username = "mandy"
# 	# url = "http://127.0.0.1:5100/api/v1/resource/playlists/profile?playlist_title="+playlist_title+"&username="+username
# 	# response = requests.get(url).text
# 	# res2= json.loads(response)
# 	# playlist_id = [item.get("playlist_id") for item in res2]
# 	# track_urls = [item.get("track_url") for item in res2]
# 	# list_guid=[item.split('/')[-1] for item in track_urls]
# 	# guid_list = [uuid.UUID(item) for item in list_guid]
# 	guid_list,track_urls, playlist_id = get_playlist_data(playlist_title, username)

# 	guid = []
# 	for i in range(len(guid_list)):
# 		guid.append(guid_list[i])
# 	values_list = []
# 	for j in range(len(guid)):
# 		print(type(guid[i]))
# 		#rusult_2 = client.get_many(("title","artist","album","media_url"))
# 		title,artist,album,length,media_url = helper.get_track_data(guid[j])
			
# 		t_desc = get_track_description(track_urls[j])
				
# 		track_desc = ast.literal_eval(json.dumps(t_desc))
# 		v = {'title': title, 'artist': artist, 'album': album, 'location': media_url,'track_desc':track_desc}
# 		values_list.append(v)

# 	displayname = get_user_data(username) #creator of a playlist

# 	tracks = values_list

# 	d = "playlist_" + str(playlist_id[0])
# 	d_track = d + "tracks"
# 	# print(d)
# 	data = {d:{"title": playlist_title, "creator": displayname , d_track: tracks}}
# 	x = json.dumps(data)

# 	print(x)


# 	#print(guid_list,track_urls, playlist)

# 	client = base.Client(('localhost',11211))


# 	# result = client.get("playlist_01")
# 	# if result is not None:
# 	# 	return result
# 	# else:
# 	# 	result = query()
# 	# 	client.add(key, value, 60)