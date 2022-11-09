from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,IntegerField
from wtforms.validators import DataRequired,Length,EqualTo,Regexp


class studentlogin(FlaskForm):
    user = StringField("user",validators=[DataRequired(message="*Required")])
    pwd = PasswordField("password",validators=[DataRequired(message="*Required")])
    submit=SubmitField("Login")

class register(FlaskForm):
    
    pwd = PasswordField("password",validators=[DataRequired(message="*Required"),Length(min=8)])
    
    cpwd = PasswordField("Confirm Password",validators=[DataRequired(message="*Required"),Length(min=8),
    EqualTo('pwd',message='Both password fields must be equal!')])
    
    fname = StringField("First Name",validators=[DataRequired(message="*Required"),Length(min=3, max=30)])
    lname = StringField("Last Name",validators=[DataRequired(message="*Required"),Length(min=3, max=30)])
    
    roll = StringField("Rollnumber",validators=[DataRequired(message="*Required"),Regexp('^[0-9]{12}$')])
    user = StringField("Email",validators=[DataRequired(message="*Required"),Length(max=50),Regexp('^[a-z0-9]+[.]?[a-z0-9]+[@]matrusri.edu.in$')])
    mob = StringField("Mobile",validators=[DataRequired(message="*Required"),Regexp('^[6-9]{1}[0-9]{9}$')])
    
    submit=SubmitField("Register")

class Forgotpass(FlaskForm):
    
    user = StringField("Email",validators=[DataRequired(message="*Required"),Length(max=50),Regexp('^[a-z0-9]+[.]?[a-z0-9]+[@]matrusri.edu.in$')]) 
    
    pwd = PasswordField("password",validators=[DataRequired(message="*Required"),Length(min=8)])
    
    cpwd = PasswordField("Confirm Password",validators=[DataRequired(message="*Required"),Length(min=8),
    EqualTo('pwd',message='Both password fields must be equal!')])
    
    submit=SubmitField("Confirm")