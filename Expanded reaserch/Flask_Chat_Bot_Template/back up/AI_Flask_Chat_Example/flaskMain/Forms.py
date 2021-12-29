from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskMain.Models import User


class RegestrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    # add the submit field
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That Username is taken. please choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That Email is taken. please choose another.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('__   Remember Me?')

    # add the submit field
    submit = SubmitField('Log in')


class MWForm(FlaskForm):
    MW = StringField('Example Field', validators=[DataRequired()])

    # add the submit field
    submit = SubmitField('Submit your Content')

