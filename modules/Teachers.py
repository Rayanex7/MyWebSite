from flask import render_template, request, redirect, Blueprint, session, url_for, jsonify
from modules.functions import is_auth, AddTeacher, DelTeacher, ModTeacher, CheckTeacher, ListTeachers, SearchTeacher, ShowSchedule, CreateSchedule
import json

TEA_Blueprint = Blueprint("Teacher", __name__)

@TEA_Blueprint.route('/Teachers_management', methods=['GET', 'POST'])
def Teacher_management():
    if not is_auth():
        return redirect('/Authentication/login')
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

@TEA_Blueprint.route('/Teachers_management/Modify', methods=['GET', 'POST'])
def Modify():
    return ModTeacher()

@TEA_Blueprint.route('/Teachers_management/List', methods=['GET', 'POST'])
def List():
    return ListTeachers()

@TEA_Blueprint.route('/Teachers_management/Search', methods=['GET', 'POST'])
def Search():
    return SearchTeacher()

@TEA_Blueprint.route('/Teachers_management/Schedule', methods=['GET', 'POST'])
def Schedule():
    return ShowSchedule()

@TEA_Blueprint.route('/Teachers_management/Create_Schedule', methods=['GET', 'POST'])
def New_schedule():
    return CreateSchedule()