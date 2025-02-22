from flask import render_template, session, request, redirect, flash, Blueprint
from modules.functions import Del_STD, Add_STD, Check_STD, ModSTD, List_STD, Search_STD, is_auth
from datetime import datetime

STD_Blueprint = Blueprint('Student', __name__)

unix_to_formatted = lambda x: datetime.fromtimestamp(x).strftime('%Y/%m/%d')
formatted_to_unix = lambda x: int(datetime.strptime(x, '%Y/%m/%d').timestamp())

@STD_Blueprint.route('/Student_management', methods=['GET', 'POST'])
def Student_management():
    if not is_auth():
        return redirect('/Authentication/login')
    
    if is_auth() not in ["Admin", "Teacher"]:
        return redirect("/Info/Contact")
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == "add":
            Add_STD()
        elif action == "del":
            Del_STD()
        elif action == "mod":
            if Check_STD():
                return redirect('/Student/ModSTD')
            else:
                flash("No Student With This Massar Code", "danger")
        elif action == "list":
            if List_STD():
                return redirect('/Student/ListSTD')
        elif action == "search":
            if Search_STD():
                return redirect('/Student/SearchSTD')
            
    return render_template("Students/Students.html")

@STD_Blueprint.route('/ModSTD', methods=['GET', 'POST'])
def Modify():
    if not is_auth():
        return redirect('/Authentication/login')
    
    if is_auth() not in ["Admin", "Teacher"]:
        return redirect("/Info/Contact")

    if request.method == 'POST':
        if ModSTD():
            flash("Student Modified Successfully", "success")
            return redirect('/Student/Student_management')
    else:
        return render_template('Students/Mod.html') 

@STD_Blueprint.route('/ListSTD', methods=['GET', 'POST'])
def List():
    if not is_auth():
        return redirect('/Authentication/login')
    
    if is_auth() not in ["Admin", "Teacher"]:
        return redirect("/Info/Contact")
    
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

        return render_template('Students/list.html', new_students=new_students)
    else:
        flash("There Is No Students In This Class", "danger")
        return redirect('/Student/Student_management')

@STD_Blueprint.route('/SearchSTD', methods=['GET', 'POST'])
def Search():
    if not is_auth():
        return redirect('/Authentication/login')
    
    if is_auth() not in ["Admin", "Teacher"]:
        return redirect("/Info/Contact")
    
    std = session.get('searched_stds')

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
        return render_template('Students/Search.html', std=std)
    else:
        flash("There Is No Student With This Massar Code", "danger")
        return redirect('/Student/Student_management')
