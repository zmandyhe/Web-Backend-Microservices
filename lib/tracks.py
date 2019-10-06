# This is the tracks microservice Python script.
# TODO: Work on this.

import flask;
from flask import request, jsonify;
import sqlite3;

# This is a helper function. TODO: Hopefully we can centralize DB code like this.
def dict_factory(cursor, row):
    d = {};
    for (idx, col) in enumerate(cursor.description):
        d[col[0]] = row[idx];
    return d;
# End of dict_factory

# This function runs when the users requests all of the information in the tracks
# table in the database.
def tracks_all():
    conn = sqlite3.connect("./var/micro_playlist.db");
    conn.row_factory = dict_factory;
    curr = conn.cursor();
    all_tracks = curr.execute("SELECT * FROM tracks;").fetchall();

    return jsonify(all_tracks);
# End of tracks_all()
