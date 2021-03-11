import datetime

from flask_wtf import Form
from wtforms import (TextAreaField, StringField, PasswordField,
                     DateTimeField, DateField, IntegerField)
from wtforms.validators import (DataRequired, Regexp, ValidationError, 
                                Email, Length, EqualTo)

from models import User

def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with this name already exists.')

def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with this email already exists.')


class RegisterForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters,"
                 "numbers and underscores only.")
            ), name_exists
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(),
        Length(min=2),
        EqualTo('password2', message='Passwords must match')]
    )
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )

    
class EntryForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    time_spent = IntegerField('Time Spent(in hours only)', validators=[DataRequired()])
    content = TextAreaField('What I learned', validators=[DataRequired()])
    resources = TextAreaField('Resources to Remember',validators=[DataRequired()])
    date = DateField("Date as in MM/DD/YYYY", format="%m/%d/%Y", validators=[DataRequired()])


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

