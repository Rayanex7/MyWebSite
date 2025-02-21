from flask import flash, request, session, render_template, redirect, jsonify, url_for
import mysql.connector
from datetime import datetime
import uuid
import json
import base64 ; import zlib

ADMIN = {"ryn":"123"}
Teachers = {"ysf":"123","morad":"123"}

unix_to_formatted = lambda x: datetime.fromtimestamp(x).strftime('%Y/%m/%d')
formatted_to_unix = lambda x: int(datetime.strptime(x, '%Y/%m/%d').timestamp())

CON = mysql.connector.connect (
        host = "127.0.0.1",
        user = "root",
        password = "Meliox7@2013.",
        database = "School"
    )

cursor = CON.cursor()

#Authentication
def authentication(who, username, password=None):
    if who == "ADMIN":
        if username in ADMIN and ADMIN[username] == password:
            key = uuid.uuid4()
            session["admin"] = username
            session["admin_key"] = key
            return True
        
    if who == "TEACHER":
        if username in Teachers and Teachers[username] == password:
            key = uuid.uuid4()
            session["teacher"] = username
            session["teacher_key"] = key
            return True
    
    if who == "STUDENT":
        try:
            cursor.execute("""SELECT Massar_ID FROM Students WHERE Massar_ID = %s""", (username,))
            stdId = cursor.fetchall()
            print(f"The ID = {stdId}")
            if stdId:
                session["std"] = stdId
                return True
        except Exception as e:
            pass
    return False

def is_auth():  
    admin = session.get('admin')
    Akey = session.get('admin_key')
    if admin and Akey:
        return "Admin"
    
    teacher = session.get('teacher')
    Tkey = session.get('teacher_key')
    if teacher and Tkey:
        return "Teacher"
    
    std = session.get('std')
    if std:
        return "Student"
    
    return False

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
    flash("Teacher Added Successfully", "success")

def DelTeacher():
    id = request.form['teacher_id']

    cursor.execute("""DELETE FROM TeachersSubjects WHERE Teacher_ID = %s""", (id,))
    cursor.execute("""DELETE FROM TeachersClasses WHERE Teacher_ID = %s""", (id,))
    cursor.execute("""DELETE FROM Teachers WHERE ID = %s""", (id,))
    CON.commit()
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

    # Convert **Class IDs** to real names
    for teacher_id, class_id in classes_data:
        if teacher_id in teachers:
            class_name = classes_dict.get(class_id, f"Unknown ({class_id})")
            teachers[teacher_id]["classes"].append(class_name)

    # Convert **Subject IDs** to real names
    for teacher_id, subject_id in subjects_data:
        if teacher_id in teachers:
            subject_name = subjects_dict.get(subject_id, f"Unknown ({subject_id})")
            teachers[teacher_id]["subjects"].append(subject_name)

    # Convert dictionary values to a list
    teachers_list = list(teachers.values())

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
