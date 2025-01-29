from flask import flash, request, redirect, url_for, session, render_template
import mysql.connector
from datetime import datetime
import uuid

ADMIN = {"ryn":"123"}

unix_to_formatted = lambda x: datetime.fromtimestamp(x).strftime('%Y/%m/%d')
formatted_to_unix = lambda x: int(datetime.strptime(x, '%Y/%m/%d').timestamp())

CON = mysql.connector.connect (
        host = "127.0.0.1",
        user = "root",
        password = "Meliox7@2013.",
        database = "School"
    )

cursor = CON.cursor()

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

def Del_STD():
    if not CON.is_connected():
        CON.reconnect()
    cursor = CON.cursor()

    Massar_code = request.form['massar_id']
    try:
        cursor.execute("""SELECT * FROM Students WHERE Massar_ID = %s""", (Massar_code,))
        user = cursor.fetchall()
        if user:
            cursor.execute("""DELETE FROM Students WHERE Massar_ID = %s""", (Massar_code,))
            CON.commit()
            flash("Student Deleted Successfully", "Success")
        else:
            raise Exception("NO STUDENT WITH THIS MASSAR ID")
    except Exception as e:
        flash(f"Error Deleting Student [{e}]", "danger")

def Add_STD():
        if not CON.is_connected():
            CON.reconnect()
        cursor = CON.cursor()

        Massar = request.form['massar_id']
        Fname = request.form['first_name']
        Lname = request.form['last_name']
        Birthday = request.form['birthdate']
        Gender = request.form['gender']
        Email = request.form['email']
        Country = request.form['country']
        City = request.form['city']
        Address = request.form['address']
        Phone = request.form['parent_phone']
        Class_id = request.form['class_id']

        Birth = formatted_to_unix(Birthday)
        if Gender == "male":
            Gender = 'M'
        else:
            Gender = 'F'
        try:   
            cursor.execute('''INSERT INTO Students (Massar_ID, First_name, Last_name, Birthdate, Gender, Email , Country, City, Address, Parent_Phone, Class_ID)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (Massar, Fname, Lname, Birth, Gender, Email, Country, City, Address, Phone, Class_id))
            
            CON.commit()

            flash("Student Added Succesfuly","Success")
        except Exception as e:
            flash(f"Error Adding Student [{e}]","Error")

def Check_STD():
    if not CON.is_connected():
        CON.reconnect()
    cursor = CON.cursor()

    Massar_code = request.form['massar_id']
    session['massar_code'] = Massar_code
    cursor.execute("""SELECT * FROM Students WHERE Massar_ID = %s""", (Massar_code,))
    student = cursor.fetchone()
    if student:
        return True
    else:
        return False

def ModSTD():
    if not CON.is_connected():
        CON.reconnect()
    cursor = CON.cursor()

    Massar_code = session.get('massar_code')
    
    #Massar = request.form.get('massar_id')
    Fname = request.form.get('first_name')
    Lname = request.form.get('last_name')
    Birthdate = request.form.get('birthdate')
    Gender = request.form.get('gender')
    Email = request.form.get('email')
    Country = request.form.get('country')
    City = request.form.get('city')
    Address = request.form.get('address')
    Phone = request.form.get('parent_phone')
    Class_id = request.form.get('class_id')

    Birthday = formatted_to_unix(Birthdate)
    if Gender == "Male":
        Gender = 'M'
    else:
        Gender = 'F'
    
    # Proceed with the update if all fields are present
    if all([Fname, Lname, Birthday, Gender, Email, Country, City, Address, Phone, Class_id]):
        cursor.execute("""
            UPDATE Students
            SET First_name = %s, Last_name = %s, Birthdate = %s, Gender = %s, Email = %s, Country = %s, City = %s, Address = %s, Parent_Phone = %s, Class_ID = %s
            WHERE Massar_ID = %s
        """, (Fname, Lname, Birthday, Gender, Email, Country, City, Address, Phone, Class_id, Massar_code))
        CON.commit()
        return True
    
def List_STD():
    if not CON.is_connected():
        CON.reconnect()
    cursor = CON.cursor()

    if request.method == 'POST':
        level = request.form.get('level')
        try:
            cursor.execute("""SELECT * FROM Students WHERE Class_ID = %s""", (level,))
            students = cursor.fetchall()
            return True, students
        except Exception as e:
            flash(f"Error Listing: [{e}]", "Error")
            return False
        
def Search_STD():
    if not CON.is_connected():
        CON.reconnect()
    cursor = CON.cursor()

    if request.method == 'POST':
        Massar = request.form['massar_id']
        try:
            cursor.execute("""SELECT * FROM Students WHERE Massar_ID = %s""", (Massar,))
            std = cursor.fetchall()
            return True, std
        except Exception as e:
            flash(f"Error Listing: [{e}]", "Error")
            return False