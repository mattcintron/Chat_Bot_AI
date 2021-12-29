# site built from examples taken from here -
# https://www.youtube.com/watch?v=MwZwr5Tvyxo&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH
from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# how to build the data base
# first open up the terminal than in the python shell write
# from flaskblog import db
# then to create the db at this directory location
# db.create_all()
# to import Models
# from FlaskBlog import User, Post
# to add user
# user2 =User(username='Jhon', email='J@demo.com', password='password')
# db.session.add(user1)
# to commit changes
# db.session.commit()
# to query users
# User.query.all()
# User.query.first()
# User.query.filter_by(username='Matt').all()
# get user with id
# User.query.get(1)
# to make a post
#  post_1 = Post(title='Blog 1', content='First Post Content!', user_id=user.id)
# to clear all data
# db.drop_all()
app = Flask(__name__)
app.config['SECRET_KEY']= 'kiah7tsytdfra54sr987yau512wa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from ..flaskMain import routes
