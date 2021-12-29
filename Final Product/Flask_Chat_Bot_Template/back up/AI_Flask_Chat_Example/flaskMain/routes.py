import io
import random
import base64
from werkzeug import secure_filename
from flask import render_template, url_for, flash, redirect, request, Response
from flaskMain import app, db, bcrypt
from flaskMain.Forms import *
from flaskMain.Models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flaskMain.Scripts.ChatBot import *
questions = []
answers =[]


# Temp list of our dictionary blog post's hard coded
posts = [
    {
    'author': 'Basic Flask Template -Lead',
    'title': 'Announcement 1',
    'content': 'Basic Flask AI Chat Bot Official site. here you will see examples of how to set up a simple AI Chat bot'
            'you can run a simple flask site with this Tensorflow based chatbot set up or build out the chat section as '
            'a full api this site also features an sql data base for user managment',
    'date': 'August / 24 / 2021'
    }
]

#pages
@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About Page')

@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegestrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account has been created for {form.username.data}! You can now Log In', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Log In Failed! Please Check Email and Password', 'danger')
    return render_template('login.html', title='login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='account')

@app.route("/contact", methods=['GET','POST'])
def contact():
    return render_template('contact.html', title='Contact Us')


@app.route('/upload')
def upload_file():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save('flaskMain/Scripts/json_files/'+ secure_filename('intents.json'))
        retrain_model()
        flash(f'New Intents File uploaded successfully Chat Bot Fully Retrained', 'success')
        return redirect(url_for('home'))


@app.route("/Tools/InteractiveFieldExample", methods=['GET','POST'])
def InteractiveFieldExample():
    form = MWForm()
    mw = form.MW.data
    global questions
    global answers
    if form.validate_on_submit() and mw != '':
        if mw == 'clean/':
            questions = []
            answers =[]
            return render_template('interactiveFieldExample.html', title='Interactive Field Example', form=form, content = 'Please type a question to send me lets start a chat')

        result = str(respond(mw))
        questions.append(mw)
        answers.append(result)
        nq = questions.copy()
        nq.reverse()
        na = answers.copy()
        na.reverse()
        return render_template('interactiveFieldExample.html', title='Interactive Field Example', form=form, content = result,
                                q = nq, a = na)
    if respond(mw) == "Error":
        flash('Calculation Failed! Please Check Data Entered', 'danger')

    questions = []
    answers =[]
    return render_template('interactiveFieldExample.html', title='Interactive Field Example', form=form, content = 'Please type a question to send me lets start a chat')










