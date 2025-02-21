from flask import Flask, render_template, session, redirect
from modules.functions import is_auth
from modules.Authentication import AUTH_Blueprint 
from modules.Students import STD_Blueprint
from modules.Info import notifications, INFO_Blueprint
from modules.Teachers import TEA_Blueprint
from modules.Administartion import Dire_Blueaprint

app = Flask(__name__)
app.secret_key = "102030"

app.register_blueprint(AUTH_Blueprint, url_prefix='/Authentication')
app.register_blueprint(STD_Blueprint, url_prefix='/Student')
app.register_blueprint(INFO_Blueprint, url_prefix='/Info')
app.register_blueprint(TEA_Blueprint, url_prefix='/Teacher')
app.register_blueprint(Dire_Blueaprint, url_prefix='/Administration')

@app.route('/')
@app.route('/home')
def home():
    if is_auth() == "Admin":
        try:
            session.pop('contact_data')
        except KeyError:
            return render_template('Home/index.html', notifications=notifications)
    return redirect('/Info/Contact')

if __name__ == "__main__":
    app.run(debug=True)