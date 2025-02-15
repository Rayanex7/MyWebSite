from flask import render_template, session, request, redirect, flash, Blueprint
from modules.functions import is_auth


INFO_Blueprint = Blueprint('Info', __name__)
notifications = []


@INFO_Blueprint.route('/About')
def About():
    if not is_auth():
        return redirect('/Authentication/login')
    return render_template('Admin/About.html')

@INFO_Blueprint.route('/Contact', methods=['GET', 'POST'])
def Contact():
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
            return redirect('/home')
        else:
            flash("Please Fill The requested form", 'danger')
            return redirect('/Info/Contact')        
    return render_template('Admin/Contact.html')

@INFO_Blueprint.route('/response_center', methods=['POST'])
def response_center():
    if not is_auth():
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
            return render_template('Admin/Response.html', name=name, email=email, subject=subject, message=message)
        flash("Error Sending info To server !", "danger")
        return redirect('/home')
