# -*- coding: utf-8 -*-

import requests
import json
from flask import render_template, Flask,  make_response
import jinja2

# response = requests.get("http://127.0.0.1:5000/api/v1/resources/tracks?guid_string=93a07604-f953-408e-a6ba-ac69c6a40762")

# print(response.content)

# app = Flask(__name__)
app = Flask(__name__, template_folder='templates')

#function to call playlist API to get a playlist's track_url
def get_playlist_data():
	url = "http://127.0.0.1:5100/api/v1/resource/playlists/profile?playlist_title=Inspiring Songs&username=mandy"
	response = requests.get(url).text
	res2= json.loads(response)
	track_urls = [item.get("track_url") for item in res2]
	guid = [item.get("guid") for item in res2]
	# username = res2["username"]
	# playlist_title = res2["playlist_title"]
	# track_url = res2["track_url"]
	# desc = res2["description"]
	return track_urls


@app.route('/playlist')
def get_playlist_xml():
	track_urls = get_playlist_data()
	location_name = "location"
	values = [{location_name: track_urls[i]} for i in range(len(track_urls))]
	# values = [
 #    	# {'creator': creator, 'location': location}
 #    	{'location': track_url}
	# ]
	# template = render_template('xspf.xml', values=values)
	template = render_template('xspf.xml', values=values)
	response = make_response(template)
	response.headers['Content-Type'] = 'application/xml'
	return response

if __name__ == "__main__":
	app.run(debug=True, port=8080)
