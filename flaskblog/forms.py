from wtforms import Form, BooleanField, StringField,FileField, PasswordField, validators, TextAreaField,ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired


class SignUpForm(Form):
    name = StringField('Name', [validators.Length(min=2, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password',[validators.DataRequired()])
     

class PostForm(Form):
    title = StringField('Title',[validators.DataRequired()])
    content = TextAreaField('Content', [validators.DataRequired()])
    photo = FileField()
   
    
    