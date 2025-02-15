from flask import render_template, session, request, redirect, Blueprint
from modules.functions import authentication, is_auth


AUTH_Blueprint = Blueprint('Authentication', __name__)


@AUTH_Blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if not is_auth():
        if request.method == 'POST':
            username = request.form['U']
            password = request.form['P']
            if authentication(username, password):
                return redirect('/home')
            return redirect('/Authentication/login')
        else:
            return render_template('Home/login.html')
    return redirect('/home')

@AUTH_Blueprint.route('/Logout')
def Logout():
    session.pop('username', None)
    session.pop('key', None)
    return redirect('/Authentication/login')
