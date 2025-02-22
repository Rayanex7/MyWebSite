from flask import flash, request, session, render_template, redirect, jsonify, url_for
import mysql.connector
from datetime import datetime
import uuid
import json
import base64 ; import zlib
from datetime import datetime


unix_to_formatted = lambda x: datetime.fromtimestamp(x).strftime('%Y/%m/%d')
formatted_to_unix = lambda x: int(datetime.strptime(x, '%Y/%m/%d').timestamp())

notifications = []

CON = mysql.connector.connect (
        host = "127.0.0.1",
        user = "root",
        password = "Meliox7@2013.",
        database = "School"
    )

cursor = CON.cursor()

#Logs
def Logs(WHO, ID, Fname, Lname, IP, Action):
    date = datetime.now()
    if WHO == "Admin":
        try:
            cursor.execute("""INSERT INTO Logs (User_Type, User_Name, User_Id, IP, Action)
                        VALUES (%s,%s,%s,%s,%s)""", (WHO, f"{Fname} {Lname}", ID, IP, Action))
            CON.commit()
        except Exception as e:
            print(e)

    if WHO == "Teacher":
        try:
            cursor.execute("""INSERT INTO Logs (User_Type, User_Name, User_Id, IP, Action)
                        VALUES (%s,%s,%s,%s,%s)""", (WHO, f"{Fname} {Lname}", ID, IP, Action))
            CON.commit()
        except Exception as e:
            print(e)
        
    if WHO == "Student":
        try:
            cursor.execute("""INSERT INTO Logs (User_Type, User_Name, User_Id, IP, Action)
                        VALUES (%s,%s,%s,%s,%s)""", (WHO, f"{Fname} {Lname}", ID, IP, Action))
            CON.commit()
        except Exception as e:
            print(e)

#Authentication
def authentication(who, username, password=None):
    if who == "ADMIN":
        try:
            cursor.execute("""SELECT ID, password FROM AdminsAUTH WHERE ID = %s AND password = %s""", (username, password))
            Admin = cursor.fetchall()
        except Exception as e:
            print(e)
        if Admin:
            key = uuid.uuid4()
            session["admin"] = username
            session["admin_key"] = key
            session["admin_ip"] = request.remote_addr
            session["admin_logs"] = {}

            cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (username,))
            result = cursor.fetchone()
            fname, lname = result
            Logs("Admin", session['admin'], fname, lname, session['admin_ip'], "LOGGED IN")

            return True
            
    if who == "TEACHER":
        try:
            cursor.execute("""SELECT ID, passwd FROM TeachersAUTH WHERE ID = %s AND passwd = %s""", (username, password))
            Teacher = cursor.fetchall()
        except Exception as e:
            print(e)
        if Teacher:
            key = uuid.uuid4()
            session["teacher"] = username
            session["teacher_key"] = key
            session["teacher_ip"] = request.remote_addr
            try:
                cursor.execute("""SELECT First_name, Last_name FROM Teachers WHERE ID = %s""", (username,))
                result = cursor.fetchone()
                Fname, Lname = result
                Logs("Teacher", session['teacher'], Fname, Lname, session['teacher_ip'], "LOGGED IN")
            except Exception as e:
                print(e)
            return True
    
    if who == "STUDENT":
        try:
            cursor.execute("""SELECT Massar_ID, First_name, Last_name, Class_ID FROM Students WHERE Massar_ID = %s""", (username,))
            result = cursor.fetchone()
            ID, Fname, Lname, ClassId = result 
            if all([ID, Fname, Lname, ClassId]):
                session["std"] = ID
                session["std_ip"] = request.remote_addr
                Logs("Student", ID, Fname, Lname, session["std_ip"], Action="LOGGED IN")
                return True
        except Exception as e:
            print(e)
    return False

def is_auth():
    
    admin = session.get('admin')
    Akey = session.get('admin_key')
    if admin and Akey:
        session['who'] = "Admin"
        return "Admin"
    
    teacher = session.get('teacher')
    Tkey = session.get('teacher_key')
    if teacher and Tkey:
        session['who'] = "Teacher"
        return "Teacher"
    
    std = session.get('std')
    if std:
        session['who'] = "Student"
        return "Student"
    
    return False

def WhoIsConnected():
    user = None
    if 'admin' in session:
        user = 'admin'
    elif 'teacher' in session:
        user = 'teacher'
    elif 'std' in session:
        user = 'std'
    else:
        return redirect('/Authentication/login')
    return user

def LogOut():
    who = WhoIsConnected()
    if who == 'admin':
        cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
        result = cursor.fetchone()
        fname, lname = result
        Logs("Admin", session['admin'], fname, lname, session["admin_ip"], "LOGGED OUT")
    if who == 'teacher':
        cursor.execute("""SELECT First_name, Last_name FROM Teachers WHERE ID = %s""", (session['teacher'],))
        result = cursor.fetchone()
        fname, lname = result
        Logs("Teacher", session['teacher'], fname, lname, session["teacher_ip"], "LOGGED OUT")
    if who == 'std':
        cursor.execute("""SELECT First_name, Last_name FROM Students WHERE Massar_ID = %s""", (session['std'],))
        result = cursor.fetchone()
        fname, lname = result
        Logs("Student", session['std'], fname, lname, session["std_ip"], "LOGGED OUT")

    session.clear()
    return redirect('/Authentication/login')

#Encoding
def encode(data):
    return base64.b64encode(zlib.compress(json.dumps(data).encode())).decode()

def decode(encoded_data):
    return json.loads(zlib.decompress(base64.b64decode(encoded_data)).decode())

#Students
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
            flash("Student Deleted Successfully", "Success")
            CON.commit()
            if is_auth() == "Admin":
                cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
                result = cursor.fetchone()
                fname, lname = result
                Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"DELETED {Massar_code}")
            elif is_auth() == "Teacher":
                cursor.execute("""SELECT ID, First_name, Last_name FROM Teachers WHERE ID = %s""", (session['teacher'],))
                result = cursor.fetchone()
                id, fname, lname = result
                Logs("Teacher", id, fname, lname, session['teacher_ip'], f"DELETE {Massar_code}")
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

            if is_auth() == "Admin":
                cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
                result = cursor.fetchone()
                fname, lname = result
                Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"ADDED {Massar}")
            elif is_auth() == "Teacher":
                cursor.execute("""SELECT ID, First_name, Last_name FROM Teachers WHERE ID = %s""", (session['teacher'],))
                result = cursor.fetchone()
                id, fname, lname = result
                Logs("Teacher", id, fname, lname, session['teacher_ip'], f"ADDED {Massar}")

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
        if is_auth() == "Admin":
            cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
            result = cursor.fetchone()
            fname, lname = result
            Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"MODIFIED STUDENT {Massar_code}")
        elif is_auth() == "Teacher":
            cursor.execute("""SELECT ID, First_name, Last_name FROM Teachers WHERE ID = %s""", (session['teacher'],))
            result = cursor.fetchone()
            id, fname, lname = result
            Logs("Teacher", id, fname, lname, session['teacher_ip'], f"MODIFIED STUDENT {Massar_code}")
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
            if is_auth() == "Admin":
                cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
                result = cursor.fetchone()
                fname, lname = result
                Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"LISTED STUDENTS IN CLASS {level}")
            elif is_auth() == "Teacher":
                cursor.execute("""SELECT ID, First_name, Last_name FROM Teachers WHERE ID = %s""", (session['teacher'],))
                result = cursor.fetchone()
                id, fname, lname = result
                Logs("Teacher", id, fname, lname, session['teacher_ip'], f"LISTED STUDENTS IN CLASS {level}")
            session['students'] = students
            return True
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
            if is_auth() == "Admin":
                cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
                result = cursor.fetchone()
                fname, lname = result
                Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"SEARCHED FOR STUDENT {Massar}")
            elif is_auth() == "Teacher":
                cursor.execute("""SELECT ID, First_name, Last_name FROM Teachers WHERE ID = %s""", (session['teacher'],))
                result = cursor.fetchone()
                id, fname, lname = result
                Logs("Teacher", id, fname, lname, session['teacher_ip'], f"SEARCHED FOR STUDENT {Massar}")
            session['searched_stds'] = std
            return True
        except Exception as e:
            flash(f"Error Listing: [{e}]", "Error")
            return False

#Teachers
def teacher_Management():
    if not is_auth():
        return redirect('/Authentication/login')
    if is_auth() != "Admin":
        return redirect('/Info/Contact')
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            AddTeacher()
        elif action == 'del':
            DelTeacher()
        elif action == 'mod':
            if CheckTeacher():
                return redirect('/Teacher/Teachers_management/Modify')
        elif action == 'list':
            return redirect('/Teacher/Teachers_management/List')
        elif action == 'search':
            id = request.form.get('teacher_id')
            session['teacher_id'] = id
            return redirect('/Teacher/Teachers_management/Search')
        elif action == 'viewSchedule':
            id = request.form.get('teacher_id')
            session['teacher_id'] = id
            return redirect(url_for('Teacher.Schedule'))
        return redirect('/Teacher/Teachers_management')
    return render_template('Teachers/teach_home.html')

def AddTeacher():
    subj_id = []
    subjects_dict = {
    1: 'Développement Informatique',
    2: 'Communication Professionnelle',
    3: 'Architecture et technologie des applications informatiques',
    4: 'Environnement économique et juridique de l\'entreprise',
    5: 'Réseau informatique',
    6: 'Système d\'exploitation GNU/Linux',
    7: 'Système d\'exploitation propriétaire',
    8: 'Langue Anglaise',
    9: 'Langue Arabe',
    10: 'Langue Française',
    11: 'Mathématique',
    12: 'الإجتماعيات',
    13: 'التربية الإسلامية',
    14: 'التربية البدنية',
    15: 'Informatique',
    16: 'الفلسفة',
    17: 'Physique-Chimie',
    18: 'Science de vie et terre (SVT)'
}

    teacher_id = request.form.get('teacher_id')
    Fname = request.form.get('first_name')
    Lname = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    gender = request.form.get('gender')

    if gender == 'male':
        gender = 'M'
    else:
        gender = 'F'

    # Get and parse the selected classes and subjects
    classes = json.loads(request.form.get('selected_classes', '[]'))
    subjects = json.loads(request.form.get('selected_subjects', '[]'))

    for sub in subjects:
        for sub_id, sub_name in subjects_dict.items():
            if sub_name == sub:
                subj_id.append(sub_id)

    
    cursor.execute("""INSERT INTO Teachers (ID, First_name, Last_name, Gender, Email, Phone)
                   VALUES (%s,%s,%s,%s,%s,%s)""", (teacher_id, Fname, Lname, gender, email, phone))
    
    for class_id in classes:
        cursor.execute("""INSERT INTO TeachersClasses (Teacher_ID, Class_ID) 
                    VALUES (%s,%s)""", (teacher_id, class_id))
        
    for subject_id in subj_id:
        cursor.execute("""INSERT INTO TeachersSubjects (Teacher_ID, Subject_ID)
                    VALUES (%s,%s)""", (teacher_id, subject_id))
        
    CON.commit()
    cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
    result = cursor.fetchone()
    fname, lname = result
    Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"ADDED [TEACHER: {teacher_id}] [CLASSES: {classes}] [SUBJECTS: {subjects}]")
    flash("Teacher Added Successfully", "success")

def DelTeacher():
    id = request.form['teacher_id']

    cursor.execute("""DELETE FROM TeachersSubjects WHERE Teacher_ID = %s""", (id,))
    cursor.execute("""DELETE FROM TeachersClasses WHERE Teacher_ID = %s""", (id,))
    cursor.execute("""DELETE FROM Teachers WHERE ID = %s""", (id,))
    CON.commit()
    cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
    result = cursor.fetchone()
    fname, lname = result
    Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"DELETED [TEACHER: {id}]")
    flash("Teacher Deleted Successfully", "success")

def ModTeacher():
    if request.method == 'POST':
        subj_id = []
        subjects_dict = {
        1: 'Développement Informatique',
        2: 'Communication Professionnelle',
        3: 'Architecture et technologie des applications informatiques',
        4: 'Environnement économique et juridique de l\'entreprise',
        5: 'Réseau informatique',
        6: 'Système d\'exploitation GNU/Linux',
        7: 'Système d\'exploitation propriétaire',
        8: 'Langue Anglaise',
        9: 'Langue Arabe',
        10: 'Langue Française',
        11: 'Mathématique',
        12: 'الإجتماعيات',
        13: 'التربية الإسلامية',
        14: 'التربية البدنية',
        15: 'Informatique',
        16: 'الفلسفة',
        17: 'Physique-Chimie',
        18: 'Science de vie et terre (SVT)'
    }

        teacher_id = request.form.get('teacher_id')
        Fname = request.form.get('first_name')
        Lname = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        gender = request.form.get('gender')

        if gender == 'male':
            gender = 'M'
        else:
            gender = 'F'

        # Get and parse the selected classes and subjects
        classes = json.loads(request.form.get('selected_classes', '[]'))
        subjects = json.loads(request.form.get('selected_subjects', '[]'))

        for sub in subjects:
            for sub_id, sub_name in subjects_dict.items():
                if sub_name == sub:
                    subj_id.append(sub_id)
                
        cursor.execute("""UPDATE Teachers SET First_name = %s, Last_name = %s, Gender = %s, Email = %s, Phone = %s
                        WHERE ID = %s""", (Fname, Lname, gender, email, phone, teacher_id))
        if subjects:
            cursor.execute("""DELETE FROM TeachersSubjects WHERE Teacher_ID = %s""", (teacher_id,))
            for i in subj_id:
                cursor.execute("""INSERT INTO TeachersSubjects (Teacher_ID, Subject_ID)
                            VALUES (%s,%s)""", (teacher_id, i))

        if classes:
            cursor.execute("""DELETE FROM TeachersClasses WHERE Teacher_ID = %s""", (teacher_id,))
            for i in classes:
                cursor.execute("""INSERT INTO TeachersClasses (Teacher_ID, Class_ID)
                            VALUES (%s,%s)""", (teacher_id, i))
                
        CON.commit()
        cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
        result = cursor.fetchone()
        fname, lname = result
        Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"MODIFIED [TEACHER: {teacher_id}] [CLASSES: {classes}] [SUBJECTS: {subjects}]")
        flash("Teacher Modified Successfully", "success")
        return redirect('/Teacher/Teachers_management')
    return render_template('Teachers/Modify.html')
    
def CheckTeacher():
    id = request.form['teacher_id']
    if id:
        return True

def ListTeachers():
    subjects_dict = {
    1: 'Développement Informatique',
    2: 'Communication Professionnelle',
    3: 'Architecture et technologie des applications informatiques',
    4: 'Environnement économique et juridique de l\'entreprise',
    5: 'Réseau informatique',
    6: 'Système d\'exploitation GNU/Linux',
    7: 'Système d\'exploitation propriétaire',
    8: 'Langue Anglaise',
    9: 'Langue Arabe',
    10: 'Langue Française',
    11: 'Mathématique',
    12: 'الإجتماعيات',
    13: 'التربية الإسلامية',
    14: 'التربية البدنية',
    15: 'Informatique',
    16: 'الفلسفة',
    17: 'Physique-Chimie',
    18: 'Science de vie et terre (SVT)'
}

    classes_dict = {
        1: 'Tronc Commun 1',
        2: 'Tronc Commun 2',
        3: 'Tronc Commun 3',
        4: '1ere BACCALAUREATE 1',
        5: '1ere BACCALAUREATE 2',
        6: '2eme BACCALAUREATE 1',
        7: '2eme BACCALAUREATE 2',
        8: '1ere BTS RSI',
        9: '1ere BTS DAI',
        10: '2eme BTS RSI',
        11: '2eme BTS DAI'
    }

    cursor.execute("SELECT * FROM Teachers")
    teachers_data = cursor.fetchall()

    cursor.execute("SELECT Teacher_ID, Class_ID FROM TeachersClasses")
    classes_data = cursor.fetchall()

    cursor.execute("SELECT Teacher_ID, Subject_ID FROM TeachersSubjects")
    subjects_data = cursor.fetchall()

    # Organize the data
    teachers = {}

    for teacher in teachers_data:
        teacher_id = teacher[0]
        teachers[teacher_id] = {
            "id": teacher[0],
            "first_name": teacher[1],
            "last_name": teacher[2],
            "gender": teacher[3],
            "email": teacher[4],
            "phone": teacher[5],
            "classes": [],
            "subjects": []
        }

    # Convert Classes id to their real name
    for teacher_id, class_id in classes_data:
        if teacher_id in teachers:
            class_name = classes_dict.get(class_id, f"Unknown ({class_id})")
            teachers[teacher_id]["classes"].append(class_name)

    # Convert Subjects id to theire real names
    for teacher_id, subject_id in subjects_data:
        if teacher_id in teachers:
            subject_name = subjects_dict.get(subject_id, f"Unknown ({subject_id})")
            teachers[teacher_id]["subjects"].append(subject_name)

    # Convert dictionary values to a list
    teachers_list = list(teachers.values())

    cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
    result = cursor.fetchone()
    fname, lname = result
    Logs("Admin", session['admin'], fname, lname, session['admin_ip'], "LISTED TEACHERS")

    # Pass `teachers_list` to the template
    return render_template("Teachers/ListTeachers.html", teachers=teachers_list)

def SearchTeacher():
    id = session['teacher_id']
    session.pop('teacher_id', None)

    subjects_dict = {
        1: 'Développement Informatique',
        2: 'Communication Professionnelle',
        3: 'Architecture et technologie des applications informatiques',
        4: 'Environnement économique et juridique de l\'entreprise',
        5: 'Réseau informatique',
        6: 'Système d\'exploitation GNU/Linux',
        7: 'Système d\'exploitation propriétaire',
        8: 'Langue Anglaise',
        9: 'Langue Arabe',
        10: 'Langue Française',
        11: 'Mathématique',
        12: 'الإجتماعيات',
        13: 'التربية الإسلامية',
        14: 'التربية البدنية',
        15: 'Informatique',
        16: 'الفلسفة',
        17: 'Physique-Chimie',
        18: 'Science de vie et terre (SVT)'
    }

    classes_dict = {
        1: 'Tronc Commun 1',
        2: 'Tronc Commun 2',
        3: 'Tronc Commun 3',
        4: '1ere BACCALAUREATE 1',
        5: '1ere BACCALAUREATE 2',
        6: '2eme BACCALAUREATE 1',
        7: '2eme BACCALAUREATE 2',
        8: '1ere BTS RSI',
        9: '1ere BTS DAI',
        10: '2eme BTS RSI',
        11: '2eme BTS DAI'
    }

    # Fetch teacher data
    cursor.execute("SELECT * FROM Teachers WHERE id = %s", (id,))
    teacher_data = cursor.fetchone()

    # Organize the teacher data
    teacher = {
        "id": teacher_data[0],
        "first_name": teacher_data[1],
        "last_name": teacher_data[2],
        "gender": teacher_data[3],
        "email": teacher_data[4],
        "phone": teacher_data[5],
        "classes": [],
        "subjects": []
    }

    # Fetch and convert class IDs to real names
    cursor.execute("SELECT Class_ID FROM TeachersClasses WHERE Teacher_ID = %s", (id,))
    class_ids = cursor.fetchall()
    for class_id in class_ids:
        class_name = classes_dict.get(class_id[0], f"Unknown ({class_id[0]})")
        teacher["classes"].append(class_name)

    # Fetch and convert subject IDs to real names
    cursor.execute("SELECT Subject_ID FROM TeachersSubjects WHERE Teacher_ID = %s", (id,))
    subject_ids = cursor.fetchall()
    for subject_id in subject_ids:
        subject_name = subjects_dict.get(subject_id[0], f"Unknown ({subject_id[0]})")
        teacher["subjects"].append(subject_name)

    # save Logs
    cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
    result = cursor.fetchone()
    fname, lname = result
    Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"SEARCHED FOR [TEACHER: {id}]")

    # Pass teacher data to the template
    return render_template('Teachers/Search.html', teacher=teacher)

def ShowSchedule():
    
    id = session['teacher_id']
    session.pop('teacher_id')

    classes = {
        1: 'Tronc Commun 1',
        2: 'Tronc Commun 2',
        3: 'Tronc Commun 3',
        4: '1ere BACCALAUREATE 1',
        5: '1ere BACCALAUREATE 2',
        6: '2eme BACCALAUREATE 1',
        7: '2eme BACCALAUREATE 2',
        8: '1ere BTS RSI',
        9: '1ere BTS DAI',
        10: '2eme BTS RSI',
        11: '2eme BTS DAI'
    }

    try:
        cursor.execute("""SELECT First_name, Last_name FROM Teachers WHERE ID = %s""", (id,))
        info = cursor.fetchall()
        cursor.execute("""SELECT schedules FROM Schedules WHERE id = %s""", (id,))
        list = cursor.fetchall()
        Encoded_schedule = list[0][0]
        schedules = decode(Encoded_schedule)
        schedule = json.loads(schedules)
        for i in classes:
            for j in schedule:
                for k in schedule[j]:
                    if schedule[j][k] == i:
                        schedule[j][k] = classes[i]

        time_slots = ["8-9", "9-10", "10-11", "11-12", "12-1", "1-2", "2-3", "3-4", "4-5", "5-6"]

        #Svae The Logs
        cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
        result = cursor.fetchone()
        fname, lname = result
        Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"SEEN SCHEDULE OF [TEACHER: {id}]")

        return render_template('Teachers/display_schedule.html', schedule=schedule, time_slots=time_slots, info=info)
    except Exception as e:
        print(e)
        flash("Error Finding Schedule For this Teacher", "danger")
        return redirect("/Teacher/Teachers_management")
    
def CreateSchedule():
    classes = {
        1: 'Tronc Commun 1',
        2: 'Tronc Commun 2',
        3: 'Tronc Commun 3',
        4: '1ere BACCALAUREATE 1',
        5: '1ere BACCALAUREATE 2',
        6: '2eme BACCALAUREATE 1',
        7: '2eme BACCALAUREATE 2',
        8: '1ere BTS RSI',
        9: '1ere BTS DAI',
        10: '2eme BTS RSI',
        11: '2eme BTS DAI'
    }
    if request.method == 'POST':
        teacher = request.form.get('teacher_id')
        schedule = request.form.get('schedule')

        if not teacher or not schedule:
            return render_template('Teachers/new_schedule.html', 
                                error_message='Missing required fields', 
                                classes=classes)
        
        try:
            # First check if teacher exists
            cursor.execute("""SELECT * FROM Schedules WHERE id = %s""", (teacher,))
            checkIfTeacher = cursor.fetchall()
            
            if checkIfTeacher:
                print("Teacher already has a schedule")  # Debug print
                return render_template('Teachers/new_schedule.html', 
                                    error_message='Teacher already has a schedule', 
                                    classes=classes)
            
            # If we get here, teacher doesn't have a schedule
            print("Creating new schedule")  # Debug print
            schedule = encode(schedule)
            cursor.execute("""INSERT INTO Schedules (id, schedules) 
                            VALUES (%s, %s)""", (teacher, schedule))
            CON.commit()

            # Save Logs
            cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
            result = cursor.fetchone()
            fname, lname = result
            Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"CREATED SCHEDULE FOR [TEACHER: {teacher}]")

            print("Schedule created successfully")  # Debug print
            return render_template('Teachers/new_schedule.html', 
                                success_message='Schedule created successfully', 
                                classes=classes)
                                
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debug print
            CON.rollback()
            return render_template('Teachers/new_schedule.html', 
                                error_message=f'Database error: {str(e)}', 
                                classes=classes)    
            
    
    return render_template('Teachers/new_schedule.html', classes=classes)

#Infos
def AboutUs():
    if not is_auth():
        return redirect('/Authentication/login')
    who = WhoIsConnected()
    if who == 'admin':
        cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
        result = cursor.fetchone()
        fname, lname = result
        Logs("Admin", session['admin'], fname, lname, session["admin_ip"], "SEEN [ABOUT US]")
    if who == 'teacher':
        cursor.execute("""SELECT First_name, Last_name FROM Teachers WHERE ID = %s""", (session['teacher'],))
        result = cursor.fetchone()
        fname, lname = result
        Logs("Teacher", session['teacher'], fname, lname, session["teacher_ip"], "SEEN [ABOUT US]")
    if who == 'std':
        cursor.execute("""SELECT First_name, Last_name FROM Students WHERE Massar_ID = %s""", (session['std'],))
        result = cursor.fetchone()
        fname, lname = result
        Logs("Student", session['std'], fname, lname, session["std_ip"], "SEEN [ABOUT US]")
    return render_template('Admin/About.html')

def ContactUS():
    if not is_auth():
        return redirect('/Authentication/login')
    if request.method == 'POST':
        name = request.form['name']
        Email = request.form['email']
        Subject = request.form['subject']
        Message = request.form['message']
        data = {"Name":name, "Email":Email, "Subject":Subject, "Message":Message}
        session['contact_data'] = data
        notifications.append(data)
        if all([name, Email, Subject, Message]):
            flash("We Will Get You Soon ☺️", 'success')
            who = WhoIsConnected()
            if who == 'admin':
                cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
                result = cursor.fetchone()
                fname, lname = result
                Logs("Admin", session['admin'], fname, lname, session["admin_ip"], "FILLED [CONTACT US]")
            if who == 'teacher':
                cursor.execute("""SELECT First_name, Last_name FROM Teachers WHERE ID = %s""", (session['teacher'],))
                result = cursor.fetchone()
                fname, lname = result
                Logs("Teacher", session['teacher'], fname, lname, session["teacher_ip"], "FILLED [CONTACT US]")
            if who == 'std':
                cursor.execute("""SELECT First_name, Last_name FROM Students WHERE Massar_ID = %s""", (session['std'],))
                result = cursor.fetchone()
                fname, lname = result
                Logs("Student", session['std'], fname, lname, session["std_ip"], "FILLED [CONTACT US]")
            return redirect('/Info/Contact')
        else:
            flash("Please Fill The requested form", 'danger')
            return redirect('/Info/Contact')        
    return render_template('Admin/Contact.html')

def Response():
    if is_auth() != "Admin":
        return redirect('/Authentication/login')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        if all([name,email,subject,message]):
            for i in notifications:
                if i['Name'] == name and i['Subject'] == subject and i['Message'] == message:
                    notifications.remove(i)
            cursor.execute("""SELECT Fname, Lname FROM Admins WHERE ID = %s""", (session['admin'],))
            result = cursor.fetchone()
            fname, lname = result
            Logs("Admin", session['admin'], fname, lname, session['admin_ip'], f"SEEN NOTIFICATION FROM [NAME: {name}, EMAIL: {email}]]")
            return render_template('Admin/Response.html', name=name, email=email, subject=subject, message=message)
        flash("Error Sending info To server !", "danger")
        return redirect('/home')


