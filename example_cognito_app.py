from boto3 import client, resource
from dateutil import tz
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory, Response, session, flash, send_file
from flask_login import login_required, LoginManager, login_user, logout_user, UserMixin
from flask_security.utils import encrypt_password
import os
import pytz
from waitress import serve
from werkzeug.utils import secure_filename
from cognito_functions import register_new_user, log_user_out, authenticate_user, start_reset_password, confirm_reset_password, get_list_of_user_emails, send_an_email, password_check
from tzlocal import get_localzone
from multiprocessing import Process
from flask_executor import Executor
import subprocess
import boto3
import mysql.connector
import sys

#Use this to confirm a password maually after creating an account if you don't want to validate via email or other method
# aws cognito-idp admin-set-user-password --user-pool-id pool_id_replace_me --username guest --password MattIsCool123* --permanent

basedir = os.path.abspath(os.path.dirname(__file__)) #where this file lives
#load the environmental variables to keep us nice and secure! 
load_dotenv(find_dotenv())

#define our flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('flask_secret_key')
app.config['UPLOAD_PATH'] = 'uploads'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['EXAMPLES'] = "examples"

#set up a background executor
executor = Executor(app)

#manager for login information
login_manager = LoginManager()
login_manager.init_app(app)

# Our mock database until we set up cognito
users = {os.getenv("username"): {'password': os.getenv('password')}}



#where to send unauthenticated users
@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for("login"))

@login_manager.user_loader
def user_loader(email):
    """uses flask authentication to create a loader function and validate the user entering information is an actual user"""
    the_user = Flask_User()
    the_user.id = email
    return the_user


@login_manager.request_loader
def request_loader(request):
    """uses flask authentication to check if the email/pass entered in the request form authenticates in the DB"""
    if request.form.get('email') not in get_list_of_user_emails():
        return

        #make the user
    the_user = Flask_User()
    the_user.id = email

    #use pycognito to check the user authentication and if it returns True, they are who they say they are
    if authenticate_user(request.form['email'], request.form['password']) == True:
        flash('You were successfully logged in')
        the_user.is_authenticated = True

        #try to make a new upload folder on the server for the user if it doesn't exist
        try:
            os.mkdir(os.path.join(app.config['UPLOAD_PATH'], ))
        except OSError as error:
            pass 
        return the_user

    else:
        return redirect(url_for(login))

############### General Routes
 

@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Main login page and requires them to validate in the user database"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        #check if their username matches the username/password combo in the database
        if "@" not in request.form['username1']:
            user, pass_or_not = authenticate_user(request.form['username1'], request.form['username2'])
        else:
            user, pass_or_not = authenticate_user(str(request.form['username1']).split("@")[0], request.form['username2'])
        if pass_or_not== True:
            flash('You were successfully logged in')
            My_User = Flask_User()
            if "@" not in request.form['username1']:
                My_User.id = request.form['username1']
                session['username'] = request.form['username1']
                login_user(My_User)
            else:
                My_User.id = str(request.form['username1']).split("@")[0]
                session['username'] = str(request.form['username1']).split("@")[0]
                login_user(My_User)
            #track in the database
            try:
                #track in the database
          # Add an insert statement into a SQL database here 
            except Exception as e:
                print(e)
                print("didn't log to db...")
            return redirect(url_for('home'))
        else:
            print("unsuccessful for {} : {}".format(request.form['username1'], request.form['username2']))
            

            return redirect(url_for("login"))
         

@app.route("/register", methods=['GET','POST'])
@login_required
def register():
	""" registers a new user to our cognito database"""
    if request.method == "POST":

        if request.form['password'] != request.form['password2']:
            flash("Passwords entered do not match")

        else:
            # pw_valid, error_val = password_check(request.form['password'])
        #if registering the new user works, redirect them to the login page to login
            pw_valid, error_val = register_new_user(request.form['email'], request.form['password'])
            
            if pw_valid == True:
                flash("Successfully created an account.")
                return redirect(url_for("login"))
            else:
                flash(error_val, "error")
                return render_template("register.html")


    return render_template('register.html', errors="")


@app.route("/forgot_password", methods=['GET','POST'])
def forgot_password():
	""" start the reset process"""
    if request.method == "POST":
        #value, error_msg = start_reset_password(request.form['email']) # Commented out so you don't actually reset the password until youre really ready
        if error_msg:
            flash(error_msg)
            return render_template("forgot_password.html")
        return redirect(url_for("forgot_password_validation"))
    return render_template('forgot_password.html')

        
@app.route("/forgot_password_validation", methods=['GET','POST'])
def forgot_password_validation():
	""" sends a validation post request to the user who is interested in resetting their password"""
    if request.method == "POST":
        print("posting...")
        if request.form['password'] != request.form['password2']:
            print("passwords don't match")
            flash("Passwords entered do not match")
        else:
            print("Passwords matched, checking for special characters...")
            val, error_msg = password_check(request.form['password'])
            if error_msg != None:
                flash(error_msg)
            else:
                print("You have successfully reset your password.")
                # confirm_reset_password(request.form['email'], request.form['password']. request.form['secret_code']) # Secret code is the secret code from the email
    return render_template('forgot_password_validation.html')


@app.route("/logout")
@login_required
def logout():
    """logs out the user"""
    logout_user()
    return redirect(url_for("login"))

class Flask_User(UserMixin):
    pass

@app.route('/home')
@login_required
def home():
    """Home page user views when they log in"""
    return render_template("home.html", username = session['username']) 



#When running the scrip by itself
if __name__ == '__main__':
    # serve(app, host='0.0.0.0', port=80) #Http serving with Waitress - much safer then flask dev server - need HTTPS though, might need GNUICORN
    app.run(host='0.0.0.0', port=8000) # Local flask app for debug