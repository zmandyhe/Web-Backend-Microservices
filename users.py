from flask import Flask, request, jsonify, g
import sqlite3
import json
import pandas as pd

app = Flask(__name__)
#app.config.from_envvar('APP_CONFIG')

conn = sqlite3.connect('users.db')
conn.row_factory = sqlite3.Row

def create_db_and_users_table():
    data_url = 'users.csv'
    headers = ['username', 'password', 'displayname', 'email','url']
    users = pd.read_csv(data_url, header=None, names=headers, converters={'zip': str})
    # Create a database
    conn = sqlite3.connect('users.db')
    # Add the data to our database
    users.to_sql('users', conn, dtype={
        'uername':'VARCHAR',
        'password':'VARCHAR',
        'displayname':'VARCHAR',
        'email':'VARCHAR',
        'url': 'VARCHAR'
    })

#homepage to list all books/users
@app.route('/')
def list_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    query = "SELECT * FROM users"
    result = c.execute(query)
    items = [dict(zip([key[0] for key in c.description], row)) for row in result]
    return json.dumps(items, sort_keys=True)


#function to create a new user from hardcode
@app.route('/insert')
def sql_datainsert():
    # if request.method == 'POST':
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    username = 'helloworld'
    password = 'life'
    displayname = 'HW'
    email = 'helloworld@gmail.com'
    url = 'http://helloworld.com'
    cur.execute(''' INSERT INTO users (username,password,displayname,email,url) VALUES (?,?,?,?,?) ''', (username,password,displayname,email,url) )
    conn.commit()
    return username

newuser = ('Andrew', '6578w', 'BMW', 'hihi@yahoo.com','love@hotmail.com')

#function to create a new user from a json file
@app.route('/insertfromjson')
def sql_create_user(user=newuser):
    # if request.method == 'POST':
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute(''' INSERT INTO users (username,password,displayname,email,url) VALUES (?,?,?,?,?) ''', user )
    conn.commit()
    return user[0]
    

@app.route('/edit',methods = ['POST', 'GET'])
def sql_dataedit():
    # if request.method == 'POST':
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    old_password = 'life'
    username = 'helloworld'
    password = 'lifeisgood'
    displayname = 'HW'
    email = 'helloworld@gmail.com'
    url = 'http://helloworld.com'
    cur.execute(''' UPDATE users set username=?,password=?,displayname=?,email=?,url=? WHERE password=? ''', (username,password,displayname,email,url, old_password) )
    return username




if __name__ == "__main__":
    app.run(debug=True, port=7890)