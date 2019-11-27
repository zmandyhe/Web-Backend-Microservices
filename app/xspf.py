# -*- coding: utf-8 -*-

import requests, flask
import json
from flask import render_template, Flask,  make_response, g, Response, jsonify
import jinja2, sqlite3, uuid
from itertools import chain
import json

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: buffer(u.bytes_le))

app = Flask(__name__, template_folder='templates')

# This is a helper function to convert the database rows returned into dictionaries.
def dict_factory(cursor, row):
    d = {};
    for (idx, col) in enumerate(cursor.description):
        d[col[0]] = row[idx];
    return d;


def get_which_db(uuid_data):
	data = uuid_data.int
	mod_id = data % 3
	if mod_id == 0:
		which_db = "../var/tracks_shard0.db"
	elif mod_id == 1:
		which_db = "../var/tracks_shard1.db"
	else:
		which_db = "../var/tracks_shard2.db"
	return which_db


def get_db_by_uuid(which_db):
	db = getattr(g,'_database', None)
	if db is None:
		db = g._database = sqlite3.connect(which_db, detect_types=sqlite3.PARSE_DECLTYPES)
		db.row_factory = dict_factory
	return db

#function to call playlist API to get a playlist's track_url
def get_playlist_data():
	url = "http://127.0.0.1:5100/api/v1/resource/playlists/profile?playlist_title=Inspiring Songs&username=mandy"
	response = requests.get(url).text
	res2= json.loads(response)
	track_urls = [item.get("track_url") for item in res2]
	list_guid=[item.split('/')[-1] for item in track_urls]
	guid_list = [uuid.UUID(item) for item in list_guid]
	# desc = res2["description"]
	return guid_list


def get_track_data(track_guid):
	global title,album,length,media_url
	which_db = get_which_db(track_guid)
	conn = get_db_by_uuid(which_db)
	cur = conn.cursor()
	query = "SELECT * FROM tracks WHERE guid = ?;"
	item = cur.execute(query, (track_guid,))
	results = cur.fetchone()
	cur.close()

	if results:
		title = results["title"]
		album = results["album"]
		length = results["len"]
		media_url = results["media_url"]
	return title,album,length,media_url



@app.route('/playlist/<playlist_id>')
def get_playlist_xml(playlist_id):
	global title,album,length,media_url
	guid_list = get_playlist_data()
	guid = []
	for i in range(len(guid_list)):
		guid.append(guid_list[i])
	values_list = []
	for j in range(len(guid)):
		title,album,length,media_url = get_track_data(guid[j])
		v = {'title': title, 'album': album, 'length': length, 'location': media_url}
		values_list.append(v)

	values = values_list
	print(values)
	template = render_template('xspf.xml', values=values)
	response = make_response(template)
	response.headers['Content-Type'] = 'application/xml'
	return response

if __name__ == "__main__":
	app.run(debug=True, port=8080)
