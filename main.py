from bottle import default_app, route, run, template, post, request, abort, response, error

import sqlite3
#from datetime import datetime
#import random



USERNAME = "username"
PASSWORD = "password"

@route('/')
def home():
    return template("index.html",var2="Nothing")

@post('/')
def postTest():
    username = request.forms.get("username")
    password = request.forms.get("password")

    if (username or password != ""):

        # create the connection
        conn = sqlite3.connect("sqlite.db")
        # cursor to control db
        c = conn.cursor()

        # get the names from the residents table
        resultPassword = c.execute(f"SELECT password FROM userinfo WHERE username = ?;", (username, ))
        # fetch the needed data
        resultPassword = str(resultPassword.fetchall())
        #print(resultPassword)

        if (str(f"[('{password}',)]") == resultPassword):
            conn.commit()
            conn.close()
            #Set the cookies, YUMMY :>
            response.set_cookie(USERNAME, username)
            response.set_cookie(PASSWORD, password)
            return Login(username)
        return template("index.html",var2="Failed") #left is variable name, right is what it is equal to, it could be result=var2, and then change {{var2}} to {{result}}
    
    return template("index.html",var2="Nothing")

def Login(username):
    # Custom list of items
    items = ["Apples", "Bananas", "Cherries", "Dates", "Grapes"]


    conn = sqlite3.connect("sqlite.db")
    c = conn.cursor()
    result = c.execute(f"SELECT id, balance FROM userinfo WHERE username = ?;", (username,) )
    result = result.fetchall()
    # Parsing the data
    for item in result:
        id_value, balance = item  # Unpacking the tuple
        #print(f'ID: {id_value}, Name: {name}')
    return template("login.html", loginID=username, id=id_value, bal=f"{balance:.2f}", items=items)



@post('/c')
def createaccount():
    return template("signup.html", response="")




@post('/s')
def signup():
    username = request.forms.get("username")
    password = request.forms.get("password")

    conn = sqlite3.connect("sqlite.db")
    c = conn.cursor()
    resultPassword = c.execute(f"SELECT password FROM userinfo WHERE username = ?;", (username,) )
    resultPassword = str(resultPassword.fetchall())
    print(resultPassword)

    response = ""
    if (username == ""):
        response = "No Username Entered"
        return template("signup.html", response=response)
    elif (resultPassword != "[]"):
        response = "Username Already Exists"
        return template("signup.html", response=response)
    
    #Create the Account
    c.execute(f"INSERT into userinfo (username, password) VALUES (?, ?);", (username, password))
    conn.commit()
    conn.close()
    response = "Account Created! :>"



    return template("signup.html", response=response)


    #return template("index.html",var2="Nothing")




@post('/m')
def AddFunds():
    money = request.forms.get("money")
    #username = request.forms.get("username")
    #replaced with delcious home baked cookies, and I aint using googles grill
    username = request.get_cookie(USERNAME)

    conn = sqlite3.connect("sqlite.db")
    c = conn.cursor()
    
    # Add the Funds
    c.execute(f"UPDATE userinfo SET balance=? WHERE username=?;", (money,username) )

    result = c.execute(f"SELECT id, balance FROM userinfo WHERE username = ?;", (username,) )
    result = result.fetchall()

    conn.commit()
    conn.close()

    # Parsing the data
    for item in result:
        id_value, balance = item  # Unpacking the tuple
        #print(f'ID: {id_value}, Name: {name}')
    # Custom list of items
    items = ["Apples", "Bananas", "Cherries", "Dates", "Grapes"]
    return template("login.html", loginID=username, id=id_value, bal=f"{balance:.2f}", items=items)


    #return template("index.html",var2="Nothing")







application = default_app()
run(host='localhost', port=5500, debug=True)    #port is the same as the index.html