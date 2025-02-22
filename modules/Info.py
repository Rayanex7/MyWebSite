from flask import render_template, session, request, redirect, flash, Blueprint
from modules.functions import is_auth, AboutUs, ContactUS, Response


INFO_Blueprint = Blueprint('Info', __name__)



@INFO_Blueprint.route('/About')
def About():
    return AboutUs()

@INFO_Blueprint.route('/Contact', methods=['GET', 'POST'])
def Contact():
    return ContactUS()

@INFO_Blueprint.route('/response_center', methods=['POST'])
def response_center():
    return Response()
