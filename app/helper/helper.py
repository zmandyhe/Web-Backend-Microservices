import requests, flask
import json
from flask import render_template, Flask,  make_response, g, Response, jsonify
import jinja2, sqlite3, uuid
from itertools import chain
import json, ast
from uuid import UUID

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
# sqlite3.register_adapter(uuid.UUID, lambda u: buffer(u.bytes_le))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)

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


#have to call here, as calling from tracks.py endpoint does not work
def get_track_data(track_guid):
    global title,artist,album,length,media_url
    which_db = get_which_db(track_guid)
    conn = get_db_by_uuid(which_db)
    cur = conn.cursor()
    query = '''SELECT * FROM tracks WHERE guid = ?'''
    print(track_guid, type(track_guid))
    item = cur.execute(query, (track_guid,))
    results = cur.fetchone()
    cur.close()

    if results:
        title = results["title"]
        artist = results["artist"]
        album = results["album"]
        length = results["len"]
        media_url = results["media_url"]
    return title,artist,album,length,media_url
