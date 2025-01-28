from flask import Flask, render_template, url_for, session, request, redirect, flash
import uuid
import mysql.connector
from datetime import datetime
from functions import Del_STD, Add_STD, Check_STD, ModSTD, List_STD, Search_STD
import ast

ADMIN = {"ryn":"123"}

CON = mysql.connector.connect (
        host = "127.0.0.1",
        user = "root",
        password = "Meliox7@2013.",
        database = "School"
    )

unix_to_formatted = lambda x: datetime.fromtimestamp(x).strftime('%Y/%m/%d')
formatted_to_unix = lambda x: int(datetime.strptime(x, '%Y/%m/%d').timestamp())

cursor = CON.cursor()

app = Flask(__name__)
app.secret_key = "102030"

def authentication(username, password):
    if username in ADMIN and ADMIN[username] == password:
        key = uuid.uuid4()
        session["username"] = username
        session["key"] = key
        return True
    return False

def is_auth():
    username = session.get('username')
    key = session.get('key')
    if username and key:
        return True
    return False

@app.route('/')
def main():
    if is_auth():
        return redirect('/home')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not is_auth():
        if request.method == 'POST':
            username = request.form['U']
            password = request.form['P']
            if authentication(username, password):
                return redirect('/home')
            return redirect('/login')
        else:
            return render_template('login.html')
    return redirect('/home')

@app.route('/home')
def home():  
    if is_auth():
        return render_template('index.html')
    return redirect('/')

@app.route('/Student_management', methods=['GET', 'POST'])
def Student_management():
    if not is_auth():
        return redirect('/login')
    if request.method == 'POST':
        action = request.form.get('action')
        if action == "add":
            Add_STD()
        elif action == "del":
            Del_STD()
        elif action == "mod":
            if Check_STD():
                return redirect('/Student_management/ModSTD')
            else:
                flash("No Student With This Massar Code", "danger")
        elif action == "list":
            if List_STD():
                _, students = List_STD()
                session['students'] = students
                return redirect('/Student_management/ListSTD')
        elif action == "search":
            if Search_STD():
                _, std = Search_STD()
                session['std'] = std
                return redirect('/Student_management/SearchSTD')
            
    return render_template("Students.html")

@app.route('/Student_management/ModSTD', methods=['GET', 'POST'])
def Modify():
    if not is_auth():
        return redirect('/login')
    if request.method == 'POST':
        if ModSTD():
            flash("Student Modified Successfully", "success")
            return redirect('/Student_management')
    else:
        return render_template('Mod.html') 

@app.route('/Student_management/ListSTD', methods=['GET', 'POST'])
def List():
    if not is_auth():
        return redirect('/login')
    students = session.get('students')
    
    new_students = []
    if students:
        for records in students:
            Massar = records[0]  # Massar_ID
            Fname = records[1]  # First_name
            Lname = records[2]  # Last_name
            date = records[3]  # Convert Birthdate
            Birthdate = unix_to_formatted(date)
            Gender = records[4]  # Gender
            Email = records[5]  # Email
            Country = records[6]  # Country
            City = records[7]  # City
            Address = records[8]  # Address
            Phone = records[9] # Phone
            Class_id = records[10]  # Class_id
            data = (Massar, Fname, Lname, Birthdate, Gender, Email, Country, City, Address, Phone, Class_id)
            new_students.append(data)

        return render_template('list.html', new_students=new_students)
    else:
        flash("There Is No Students In This Class", "danger")
        return redirect('/Student_management')

@app.route('/Student_management/SearchSTD', methods=['GET', 'POST'])
def Search():
    if not is_auth():
        return redirect('/login')
    std = session.get('std')

    if std:
        for i in std:
            data = (
                i[0],
                i[1],
                i[2],
                unix_to_formatted(i[3]),
                i[4],
                i[5],
                i[6],
                i[7],
                i[8],
                i[9],
                i[10]
            )
        std = data
        return render_template('Search.html', std=std)
    else:
        flash("There Is No Student With This Massar Code", "danger")
        return redirect('/Student_management')

@app.route('/Direction')
def Direction():
    if not is_auth():
        return redirect('/login')
    return "<h1>Direction Page</h1>"

@app.route('/Teachers_management')
def Teachers_management():
    if not is_auth():
        return redirect('/login')
    return "<h1>Direction Page</h1>"

@app.route('/Logout')
def Logout():
     session.pop('username')
     session.pop('key')
     return redirect('/')

'''@app.route('/hello')
def hello():
    if is_auth():
        return f"Hello {session['username']}!"
    return redirect('/')'''
    

if __name__ == "__main__":
    app.run(debug=True)