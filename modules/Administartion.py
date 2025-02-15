from flask import Flask, Blueprint, redirect
from modules.functions import is_auth

Dire_Blueaprint = Blueprint('Administration', __name__)


@Dire_Blueaprint.route('/Home')
def Direction():
    if not is_auth():
        return redirect('/Authentication/login')
    return "<h1>Direction Page</h1>"

