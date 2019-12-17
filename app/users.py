#!/usr/bin/env python3

from flask import Flask, request, jsonify, g, Response
import sqlite3
import json
from werkzeug.security import generate_password_hash,check_password_hash
from os.path import isfile
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

app = Flask(__name__)
#app.config.from_envvar('APP_CONFIG')


# This is a helper function to modularize the database connection
def get_db_session():
    cluster = Cluster(['172.17.0.2'], port=9042)
    session = cluster.connect('xspf')
    return session


# """
# helper functions
# """
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


#homepage
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome to User Microservice API</h1>

<h2>Retrieve all users</h2>
<p>/api/v1/resource/users/all, method: GET: list all users in the database.<br/>
sample call: <br/>
/api/v1/resource/users/all <br/>
    [<br/>
        {<br/>
            "username": "jeff", <br/>
            "displayname": "Jeff Bezos", <br/>
            "url": "https://www.google.com/Jeffbezos", <br/>
            "pwd_hash": "pbkdf2:sha256:150000$BN1bCsqI$26b5192c6a29ce9b8b6a70253eebfef7745013484a802c0e88c976cc628cc885",<br/>
            "email": "jbezos@amazon.com" <br/>
        }, <br/>
        {<br/>
            "username": "mandy", <br/>
            "displayname": "Mandy He", <br/>
            "url": "https://www.google.com/mandyhe",<br/>
            "pwd_hash": "pbkdf2:sha256:150000$7aKmozcN$ed4a89b58dc1547baa5bf27c20416d6442554aef9d82a6393035031802226f65",<br/>
            "email": "mandy2.he@gmail.com"<br/>
        }<br/>
    ]<br/>

</p>

<h2>Create new user</h2>
<p>/api/v1/resource/users/newuser, method: POST: to create a new user from query parameters, <br/>
    sampple input like this: <br/>
    /api/v1/resource/users/newuser?username=jeff&password=5678&displayname=Jeff Bezos&email=jbezos@amazon.com&url=https://www.google.com/Jeffbezos<br/>
</p>


<h2>Change a user's password</h2>
<p>/api/v1/resource/users/password, method: PUT: to change a user's password, input old password then hashed, <br/>
    if it matches with the stored hash password, it will ask new password then strored the hashed password. <br/>
    Input query parameter like: <br/>
    sample call: <br/>
    /api/v1/resource/users/password?username=mandy&old_password=1234&new_password=5678 <br/>
</p>

<h2>Retrieve a user profile except the password</h2>
<p>/api/v1/resource/users/profile, method: GET: to retrieve a user's profile except hashed password. <br/>
    /api/v1/resource/users/profile?username=mandy <br/>
    sample response: <br/>
    [ <br/>
        "mandy",<br/>
        "Mandy He",<br/>
        "mandy2.he@gmail.com",<br/>
        "https://www.google.com/mandyhe"<br/>
    ]<br/>
</p>

<h2>Delete a user</h2>
<p>
    /api/v1/resource/users/removal, method: DELETE: to delete a specific user, <br/>
    input query parameter: /api/v1/resource/users/removal?username=mandy.<br/>
</p>'''


# #list all users
@app.route('/api/v1/resource/users/all', methods=['GET'])
def list_all_users():
    session = get_db_session()
    session.row_factory = dict_factory
    rows = session.execute("SELECT username,displayname,email,url FROM users_by_username")
    if rows is None:
        return page_not_found(404)
    else:
        data = []
        for row in rows:
            data.append(row)
        return Response(json.dumps(data, indent=4, sort_keys=False), 200, {'Content-Type': 'application/json'})


#function to create a new user from query parameter in the api endpoint
@app.route('/api/v1/resource/users/newuser',methods=['POST'])
def create_a_user():
    session = get_db_session()
    query_parameters = request.args
    username = query_parameters.get("username")
    password = query_parameters.get("password")
    displayname = query_parameters.get("displayname")
    email = query_parameters.get("email")
    url = query_parameters.get("url")
    pwd_hashed = generate_password_hash(password)
    if username is not None and pwd_hashed is not None and displayname is not None and email is not None:
        try:
            user = (username, pwd_hashed, displayname,email,url)
            session.execute(
                """
                INSERT INTO users_by_username (username, pwd_hashed, displayname,email,url)
                VALUES (%s, %s, %s, %s, %s)
                """,
                user
            )
            return ("<h2>Success, new user has been successfully created!</h2>",201)
        except Exception as err:
            return ("Query of insert failed")
    else:
        return ("input query parameter")


# #function to update a user's password
@app.route('/api/v1/resource/users/password',methods = ['PUT'])
def edit_user_password():
    session = get_db_session()
    session.row_factory = dict_factory
    query_parameters = request.args
    username1 = query_parameters.get("username")
    pw_old = query_parameters.get("old_password")
    if username1 is not None and pw_old is not None:
        query1 = "SELECT * FROM users_by_username WHERE username = %s"
        result1= session.execute(query1,[username1])
        if result1 is None:
            return "user is not in the database"
        else:
            username_stored = result1[0]['username']
            if username_stored != username1:
                return"username is not in the database yet, you may want to create a username"
            else:
                pw_old_stored = result1[0]["pwd_hashed"]
                is_valid = check_password_hash(pw_old_stored,pw_old)
                if is_valid:
                    new_pw = query_parameters.get("new_password")
                    new_pw_hashed = generate_password_hash(new_pw)
                    try:
                        session.execute("UPDATE users_by_username SET pwd_hashed=%s WHERE username= %s", (new_pw_hashed,username1))
                        return Response("200 OK,The user password is changed successfully", headers={'Content-Type':'application/json'},status=200)
                    except Exception as err:
                        return ('Query Failed: %s\nError: %s' % (''' UPDATE INTO users_by_username''', str()))
                else:
                    return "password does not match"
    return "input request parameters:username and password"


#retrieve a user's profile
@app.route('/api/v1/resource/users/profile', methods = ['GET'])
def get_user_profile():
    session = get_db_session()
    query_parameters = request.args
    username = query_parameters.get("username")
    session.row_factory = dict_factory
    query = "SELECT username, displayname, email, url FROM users_by_username WHERE username= %s"
    rows = session.execute(query,[username])
    if rows is None:
        return page_not_found(404)
    else:
        data = []
        for row in rows:
            data.append(row)
        print(json.dumps(data))
        return Response(json.dumps(data, indent=4, sort_keys=False), 200, {'Content-Type': 'application/json'})


#delete a user
@app.route('/api/v1/resource/users/removal', methods = ['DELETE'])
def delete_user():
    session = get_db_session()
    username = request.args.get('username')
    if username is None:
        return ("input username as a query parameter")
    else:
        try:
            query = "DELETE FROM users_by_username WHERE username = %s"
            session.execute(query,[username])
            return Response( "200 OK,The user is deleted successfully", headers={'Content-Type':'application/json'},status=200)
        except Exception as err:
            return ('Query Failed: %s\nError: %s' % (''' DELETE FROM users''', str()))



app.run()
# if __name__ == "__main__":
#     app.run(debug=True, port=5200)
