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
    with open('users/newuser.txt') as json_file:
        data = json.load(json_file)
        desc=(data["username"],data["pwd_hash"],data["displayname"],data["email"],data["url"])
        desc={"username": data["username"], "pwd_hash": data["pwd_hash"],"displayname": data["displayname"],"email": data["email"],"url":data["url"]}
    return desc


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


#list all users
@app.route('/api/v1/resource/users/all', methods=['GET'])
def list_all_users():
    if request.method == 'GET':
        conn = sqlite3.connect('../var/microservices_db.db', check_same_thread=False)
        cur = conn.cursor()
        query = "SELECT * FROM users"
        result = cur.execute(query)
        items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
        cur.close()
    if items is None:
        return page_not_found(404)
    else:
        return Response(json.dumps(items, sort_keys=False), 200, {'Content-Type': 'application/json'})


#function to create a new user from query parameter in the api endpoint
@app.route('/api/v1/resource/users/newuser',methods=['POST'])
def sql_create_user_by_input():
    conn = sqlite3.connect('../var/microservices_db.db', check_same_thread=False)
    # conn = sqlite3.connect('users/users.db', check_same_thread=False)
    cur = conn.cursor()
    query_parameters = request.args
    username = query_parameters.get("username")
    password = query_parameters.get("password")
    displayname = query_parameters.get("displayname")
    email = query_parameters.get("email")
    url = query_parameters.get("url")
    pwd_hash = generate_password_hash(password)
    # newuser_dict={"username":username,
    #             "pwd_hash": pwd_hash,
    #              "displayname": displayname,
    #              "email": email,
    #              "url":url}
    if username is not None and pwd_hash is not None and displayname is not None and email is not None:
        try:
            user = (username, pwd_hash, displayname,email,url)
            result = cur.execute(''' INSERT INTO users (username,pwd_hash,displayname,email,url) VALUES (?,?,?,?,?) ''', user )
            conn.commit()
            cur.close()
            return Response("<h1>Success</h1>",headers={'Content-Type':'application/json'},status=201)
        except Exception as err:
            return ('Query Failed: %s\nError HTTP 409 Conflict., username and email must be unique %s' % (''' INSERT INTO users''', str()))
    else:
        return ("input query parameter")


#function to update a user's password
@app.route('/api/v1/resource/users/password',methods = ['PUT'])
def sql_dataedit_password():
    conn = sqlite3.connect('../var/microservices_db.db', check_same_thread=False)
    cur = conn.cursor()
    query_parameters = request.args
    username = query_parameters.get("username")
    pw_old = query_parameters.get("old_password")
    if username is not None and pw_old is not None:
        query1 = ''' SELECT username, pwd_hash, displayname, email, url FROM users WHERE username = ?'''
        result1= cur.execute(query1,(username,))
        if result1 is None:
            return "user is not in the database"
        else:
            result= cur.fetchall()
            items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
            username_stored = items[0]['username']
            if username_stored != username:
                return"username is not in the database yet, you may want to create a username"
            else:
                pw_old_stored = items[0]["pwd_hash"]
                is_valid = check_password_hash(pw_old_stored,pw_old)
                if is_valid:
                    new_pw = query_parameters.get("new_password")
                    new_pw_hashed = generate_password_hash(new_pw)
                    try:
                        result2=cur.execute(''' UPDATE users set pwd_hash=? WHERE pwd_hash=? ''', (new_pw_hashed,pw_old_stored))
                        conn.commit()
                        cur.close()
                        # items = [dict(zip([key[0] for key in cur.description], row)) for row in result2]
                        # if items is None:
                        #     return page_not_found(404)
                        # else:
                        return Response("200 OK,The user password is changed successfully", headers={'Content-Type':'application/json'},status=200)
                    except Exception as err:
                        return ('Query Failed: %s\nError: %s' % (''' UPDATE INTO users''', str()))
                else:
                    return "password does not match"
        # return "input username and password in the request parameter starting with ?", 404
    return "input request parameters:username and password"

#retrieve a user's profile
@app.route('/api/v1/resource/users/profile', methods = ['GET'])
def get_user_profile():
    # conn = sqlite3.connect('users/users.db', check_same_thread=False)
    conn = sqlite3.connect('../var/microservices_db.db', check_same_thread=False)
    cur = conn.cursor()
    query_parameters = request.args
    username = query_parameters.get("username")
    query = "SELECT username,displayname,email,url FROM users WHERE username=?"
    result = cur.execute(query, (username,))
    r = result.fetchone()
    cur.close()
    if r is None:
        return "this username is not in the database"
    else:
        return Response(json.dumps((r), sort_keys=False),headers={'Content-Type':'application/json'},status=200)


#delete a user
@app.route('/api/v1/resource/users/removal', methods = ['DELETE'])
def delete_user():
    conn = sqlite3.connect('../var/microservices_db.db', check_same_thread=False)
    cur = conn.cursor()
    username = request.args.get('username')
    if username is not None:
        try:
            query = ''' DELETE FROM users where username = ?'''
            cur.execute(query,(username,))
            conn.commit()
            cur.close()
            return Response( "200 OK,The user is deleted successfully", headers={'Content-Type':'application/json'},status=200)
        except Exception as err:
            return ('Query Failed: %s\nError: %s' % (''' DELETE FROM users''', str()))
    return ("input username as a query parameter")


app.run()
# if __name__ == "__main__":
#     app.run(debug=True)
