from flask import Flask, request, jsonify, g, Response
import sqlite3
import json
import pandas as pd
from werkzeug.security import generate_password_hash,check_password_hash
from os.path import isfile

app = Flask(__name__)
#app.config.from_envvar('APP_CONFIG')

"""Initialize users.db and users table"""
if not isfile('users.db'):
    data_url = 'users.csv'
    headers = ['username', 'pwd_hash', 'displayname', 'email','url']
    users = pd.read_csv(data_url, header=None, names=headers, converters={'zip': str})
    password = users['pwd_hash']
    users['pwd_hash'] = generate_password_hash(password[0])
    # Create a database
    conn = sqlite3.connect('users.db', check_same_thread=False)
    # Add the data to our database with table name of users
    users.to_sql('users', conn, dtype={
        'username':'VARCHAR',
        'pwd_hash':'VARCHAR',
        'displayname':'VARCHAR',
        'email':'VARCHAR',
        'url': 'VARCHAR'
    })
else:
    pass

"""
helper functions
"""
#helper func to convert to json format
def convert_json():
    f = open("newuser.txt", "r")
    data = f.readlines()
    open("newuser.json", "w").close()
    with open('newuser.json', 'w') as f:
        #epsg_json = json.loads(response_read.replace("\'", '"'))
        json.dump(data, f,ensure_ascii=False)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

#newuser = ('Andrew', '6578w', 'BMW', 'hihi@yahoo.com','love@hotmail.com')


#homepage
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome to User Microservice</h1>
<p>/users/all: list all users.</p>
<p>/users/create: to create a new user from query parameters, input like this: http://127.0.0.1:7890/users/createbyinput?username=mary&password=jfk&displayname=MaryKing&email=mary@163.com&url=https://kdkdk.com</p>
<p>/users/edit: to change a user's password, input query parameer like: /users/edit?username=mandy&old_password=fdgd&new_password=fdgd</p>
<p>/users/profile: to retrieve a user's profile except password.</p>
<p>/users/delete: to delete a specific user, input query parameter: /users/delete?username=mandy.</p>'''


#list all users
@app.route('/users/all', methods=['GET'])
def list_all_users():
    if request.method == 'GET':
        conn = sqlite3.connect('users.db', check_same_thread=False)
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
@app.route('/users/create',methods=['POST','GET'])
def sql_create_user_by_input():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cur = conn.cursor()

    query_parameters = request.args
    username = query_parameters.get("username")
    password = query_parameters.get("password")
    displayname = query_parameters.get("displayname")
    email = query_parameters.get("email")
    url = query_parameters.get("url")   
    pwd_hash = generate_password_hash(password)

    user = (username, pwd_hash, displayname,email,url)
    result = cur.execute(''' INSERT INTO users (username,pwd_hash,displayname,email,url) VALUES (?,?,?,?,?) ''', user )
    conn.commit()
    items = [dict(zip([key[0] for key in cur.description], row)) for row in result]   
    cur.close()
    if items is None:
        return page_not_found(404)
    else:
        return Response(json.dumps(items, sort_keys=False),headers={'Content-Type':'application/json'},status=201)



#function to update a user's password
@app.route('/users/edit',methods = ['GET','POST'])
def sql_dataedit():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cur = conn.cursor()
    if request.method == 'GET':
        query_parameters = request.args
        urname = query_parameters.get("username")
        pw_old = query_parameters.get("old_password")
        if urname:
            query1 = ''' SELECT username, pwd_hash, displayname, email, url FROM users where username = ?'''
            result1= cur.execute(query1,(urname,))
            if result1 is None:
                return "user is not in the database"
            else:
                result= cur.fetchall()
                items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
                username_stored = items[0]['username']
                if username_stored != urname:
                    return"username is not correct"
                else:
                    pw_old_stored = items[0]["pwd_hash"]
                    is_valid = check_password_hash(pw_old_stored,pw_old)
                    if is_valid:
                        new_pw = query_parameters.get("new_password")
                        new_pw_hashed = generate_password_hash(new_pw)
                        if request.method == 'POST':
                            result2=cur.execute(''' UPDATE users set username=?,pwd_hash=? WHERE pwd_hash=? ''', (urname,new_pw_hashed,pw_old_stored))
                            conn.commit()
                            cur.close()
                            items = [dict(zip([key[0] for key in cur.description], row)) for row in result2]
                            if items is None:
                                return page_not_found(404)
                            else:
                                return Response(json.dumps(items, sort_keys=False), "200 OK,The user password is changed successfully", headers={'Content-Type':'application/json'},status=200)
                    else:
                        return "password does not match"
        return "input username in the request parameter starting with ?", 404
    return "input request parameters"

#retrieve a user's profile
@app.route('/users/profile', methods = ['GET'])
def get_user_profile():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cur = conn.cursor()
    query_parameters = request.args
    username = query_parameters.get("username")
    query = "SELECT username,displayname,email,url FROM users WHERE username==username"
    result = cur.execute(query)
    items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
    cur.close()
    if items is None:
        return page_not_found(404)
    else:
        return Response(json.dumps(items[0], sort_keys=False),headers={'Content-Type':'application/json'},status=200)


#delete a user
@app.route('/users/delete', methods = ['POST','GET'])
def delete_user():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cur = conn.cursor()
    if request.method == 'GET':
        urname = request.args.get('username')
        query = ''' DELETE FROM users where username = ?'''
        cur.execute(query,(urname,))
        conn.commit()
        cur.execute(''' SELECT * FROM users''')
        result= cur.fetchall()
        items = [dict(zip([key[0] for key in cur.description], row)) for row in result]
        cur.close()
    return "<h1>200 OK</h1><p>The user is deleted successfully", 200


if __name__ == "__main__":
    app.run(debug=True, port=7890)