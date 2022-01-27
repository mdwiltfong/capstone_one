from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, BooleanField,RadioField,SelectField, PasswordField
from wtforms.fields import choices
from wtforms.fields.numeric import IntegerField
from wtforms.validators import InputRequired, Email, Optional


class AddCustomer(FlaskForm):
    first_name=StringField("First name",validators=[InputRequired()])
    first_name=StringField("Last name",validators=[InputRequired()])
    email=StringField("Email", validators=[InputRequired(),Email()])
    username=StringField("Username", validators=[InputRequired()])
    password=PasswordField("Password",validators=[InputRequired()])


