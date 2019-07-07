from flask import Flask, request, render_template, redirect, flash, session, g
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import os
from flask_wtf.csrf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
from sklearn.naive_bayes import GaussianNB
import numpy as np
import pandas as pd
import datetime

app = Flask(__name__)
#app._static_folder = '/s'
csrf = CSRFProtect()
csrf = CSRFProtect(app)

csrf.init_app(app)

secret_key = os.urandom(24)

s = URLSafeTimedSerializer(secret_key)

app.secret_key = secret_key
mysql = MySQL(app)
mail = Mail(app)

sender_email = 'urwithkdsingh@gmail.com'
sender_password = 'JPMCcfg19'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'anthill'
app.config["SECRET_KEY"] = "abcd4321"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = sender_email
app.config['MAIL_PASSWORD'] = sender_password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# ROUTES

# SESSION MGT
@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

# HOME PAGE
@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

# ADMIN LOGIN
@app.route('/adlogin', methods=['GET', 'POST'])
def adlogin():
    if request.method == 'GET':
        return render_template('admin_login.html')

    else:
        adminDetails = request.form
        password = adminDetails['password']
        user = adminDetails['username']
        curr = mysql.connection.cursor()
        resultSet = curr.execute(
            "SELECT * FROM admin WHERE username='" + user + "'")
        if resultSet == 1:
            ad = curr.fetchall()
            if ad[0][2] == password:
                session.pop('user', None)
                session['user'] = user
                return redirect("/admin_dashboard")
            else:
                # FLASH MESSAGE
                flash("Passwords do not match", "danger")
                return redirect("/adlogin")
        return redirect("/adlogin")


# CLIENT LOGIN
@app.route('/clogin', methods=['GET', 'POST'])
def clogin():
    if request.method == 'GET':
        return render_template('client_login.html')

    else:
        clientDetails = request.form
        password = clientDetails['password']
        user = clientDetails['username']
        curr = mysql.connection.cursor()
        resultSet = curr.execute(
            "SELECT * FROM client WHERE username='" + user + "'")
        if resultSet == 1:
            ad = curr.fetchall()
            if check_password_hash(ad[0][2], password):
                session.pop('user', None)
                session['user'] = user
                return redirect("/client_homepage")
            else:
                # FLASH Message
                return "False"
        else:
            # FLASH Message
            return "false"


# CLIENT SIGNUP
@app.route('/csignup', methods=['GET', 'POST'])
def csignup():
    if request.method == 'GET':
        return render_template('client_register.html')

    else:
        clientDetails = request.form
        user = clientDetails['username']
        email = clientDetails['email']
        password = createHash(clientDetails['password'])
        name = clientDetails['name']
        phone = clientDetails['phone']
        curr = mysql.connection.cursor()
        resultSet = curr.execute(
            "SELECT * FROM client WHERE username='" + user + "'")
        if resultSet != 0:
            # FLASH Message
            return "False"
        else:
            token = s.dumps(user, salt="emailConfirm")
            msg = Message("Welcome to Anthill!",
                          sender=sender_email, recipients=[email])
            msg.body = "Welcome to Anthill. Thank you for registering with us. We hope to create great projects together.\nYour link is: localhost:5000/confirmEmail/{}".format(
                token)
            with app.open_resource("broucher.png") as fp:
                msg.attach("broucher.png", "image/png", fp.read())
            mail.send(msg)
            resultSet2 = curr.execute(
                "INSERT INTO client(username,email,password,name,phone) VALUES ('"+user+"','"+email+"','"+password+"','"+name+"','"+phone+"')")
            mysql.connection.commit()
            return redirect("/home")


# REG CNFRM
@app.route("/confirmEmail/<token>")
def confirmEmail(token):
    try:
        user = s.loads(token, salt="emailConfirm", max_age=3600)
    except SignatureExpired:
        return "Token Expired"
    session.pop('user', None)
    session['user'] = user
    return redirect("/survey")


# NEW PLAYGROUND
@app.route('/newPlayground', methods=['GET'])
def newPlayGround():
    if g.user:
        return redirect('/survey')
    return redirect('/clogin')


# SURVEY FORM
@app.route("/survey", methods=['GET', 'POST'])
def survey():
    if g.user:
        if request.method == 'POST':
            print("Here")
            surveyDetails = request.form
            curr = mysql.connection.cursor()
            # `latitude`, `longitude`,
            #+ "'" + surveyDetails['latitiude'] + "'," + "'" + surveyDetails['longitude'] + "',"
            curr.execute("INSERT INTO survey(client_username, proj_name, budget, addr, student_no, age_from, age_to, area, snake, public_avail, vandalism, soil_condition, play_elements, underground, poles, plants, rocks, logging, highway, water_body, disability, maintenance, equipment, routine) VALUES ('" + g.user + "','" + surveyDetails['proj_name'] + "'," + surveyDetails['budget'] + ",'" + surveyDetails['addr'] + "'," + surveyDetails['student_no'] + "," + surveyDetails['age_from'] + "," + surveyDetails['age_to'] + "," + surveyDetails['area'] + "," + surveyDetails['snake'] + "," + surveyDetails[
                         'public_avail'] + "," + surveyDetails['vandalism'] + ",'" + surveyDetails['soil_condition'] + "'," + surveyDetails['play_elements'] + "," + surveyDetails['underground'] + "," + surveyDetails['poles'] + "," + surveyDetails['plants'] + "," + surveyDetails['rocks'] + "," + surveyDetails['logging'] + "," + surveyDetails['highway'] + ",'" + surveyDetails['water_body'] + "'," + surveyDetails['disability'] + "," + surveyDetails['maintenance'] + ",'" + surveyDetails['equipment'] + "','" + surveyDetails['routine'] + "');")
            mysql.connection.commit()

            curr.execute(
                "SELECT survey_id from survey ORDER BY survey_id DESC")
            sur_id = curr.fetchone()[0]
            filename = "model.pkl"
            model_unpickle = open(filename, "rb")
            class_model = pickle.load(model_unpickle)
            pred = np.array([int(int(surveyDetails['budget'])/50000), int(int(surveyDetails['area'])/200), int(int(
                surveyDetails['student_no'])/20), surveyDetails['disability'], surveyDetails['snake'], surveyDetails['play_elements']]).astype(int)
            template_id = class_model.predict(pred.reshape(1, -1))
            pdate = datetime.datetime.now().strftime("%Y-%m-" + "%" + "d")
            print(pdate)
            curr.execute("INSERT INTO project(client_username,survey_id,template_id,status,pdate) VALUES (" "'" +
                         g.user + "'," + str(sur_id) + "," + str(template_id[0]) + ",'pending','" + pdate + "')")
            mysql.connection.commit()
            curr.execute(
                "SELECT path from template WHERE template_id=" + str(template_id[0]))
            img_path = curr.fetchone()[0]
            curr.execute(
                "SELECT email from client WHERE username='" + g.user + "'")
            email = curr.fetchone()[0]
            msg = Message("Your first design!",
                          sender=sender_email, recipients=[email])
            msg.body = "PFA your first design, suggested by our top designers."
            with app.open_resource(img_path) as fp:
                msg.attach(img_path, "image/jpg", fp.read())
            mail.send(msg)
            return render_template("survey.html")
        else:
            return render_template("survey.html")
    else:
        return redirect("/clogin")


# ADMIN DASHBOARD
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if g.user:
        return render_template("admin_dashboard.html")
    return redirect('/adlogin')


# CLIENT HOMEPAGE
@app.route('/client_homepage', methods=['GET', 'POST'])
def client_homepage():
    if g.user:
        p = pending()
        c = completed()
        m = modified()
        arr = [p, c, m]
        return render_template('client_homepage.html', value=arr)
    return redirect('/clogin')


# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/home')


# Functions

def maintenanceDetails():
    curr = mysql.connection.cursor()
    resultSet = curr.execute(
        "SELECT client.email, survey.addr FROM project LEFT JOIN client ON project.client_username=client.username && project.pdate>" + datetime.datetime.now().strftime("%Y-%m-" + "%" + "d") + " LEFT JOIN survey ON project.survey_id=survey.survey_id")
    ip = mycursor.fetchall()
    resultSet = curr.execute("SELECT email FROM admin")
    email = mycursor.fetchone()[0]
    for i in ip:
        msg = Message("Maintenance Due",
                      sender=sender_email, recipients=[email])
        msg.body = "The maintenance is due for user: " + ip[0]
        msg.body = msg.body + " at area: " + ip[1]
        mail.send(msg)


def pending():
    curr = mysql.connection.cursor()
    resultSet = curr.execute(
        "SELECT * FROM survey LEFT JOIN project ON project.status = 'pending' && project.survey_id=survey.survey_id")
    pd = curr.fetchall()
    return pd


def completed():
    curr = mysql.connection.cursor()
    resultSet = curr.execute(
        "SELECT * FROM survey LEFT JOIN project ON project.status = 'completed' && project.survey_id=survey.survey_id")
    cd = curr.fetchall()
    return cd


def modified():
    curr = mysql.connection.cursor()
    resultSet = curr.execute(
        "SELECT * FROM survey WHERE maintenance=1 ORDER_BY pdate DESC")
    md = curr.fetchall()
    return md


def createHash(password):
    h_pass = generate_password_hash(password)
    return h_pass
