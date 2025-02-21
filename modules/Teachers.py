from flask import Blueprint
from modules.functions import ModTeacher, ListTeachers, SearchTeacher, ShowSchedule, CreateSchedule, teacher_Management

TEA_Blueprint = Blueprint("Teacher", __name__)

@TEA_Blueprint.route('/Teachers_management', methods=['GET', 'POST'])
def Teacher_management():
    return teacher_Management()

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