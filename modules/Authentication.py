from flask import render_template, session, request, redirect, Blueprint
from modules.functions import authentication, is_auth


AUTH_Blueprint = Blueprint('Authentication', __name__)


@AUTH_Blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if not is_auth():
        if request.method == 'POST':
            try:
                admin = request.form['U']
                passwd = request.form['P']
                if authentication("ADMIN", admin, passwd):
                    return redirect('/home')
            except Exception:
                pass

            try:
                teacher = request.form['T']
                passwd = request.form['P']
                if authentication("TEACHER",teacher, passwd):
                    return redirect('/Student/Student_management')
            except Exception:
                pass

            try:
                std = request.form['stdId']
                if authentication("STUDENT", std):
                    return redirect('/Info/About')
            except Exception as e:
                print(e)
            print("ERROR")
            return redirect('/Authentication/login')
        else:
            return render_template('Home/login.html')
    return redirect('/home')

@AUTH_Blueprint.route('/Logout')
def Logout():
    session.clear()
    return redirect('/Authentication/login')
