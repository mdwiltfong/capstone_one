from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, BooleanField,RadioField,SelectField, PasswordField
from wtforms.validators import InputRequired, Email, Optional
from countries import US_STATES
from helper_functions import dict_to_list

class AddCustomer(FlaskForm):
    first_name=StringField("First name",validators=[InputRequired()])
    last_name=StringField("Last name",validators=[InputRequired()])
    email=StringField("Email", validators=[InputRequired(),Email()])
    username=StringField("Username", validators=[InputRequired()])
    password=PasswordField("Password",validators=[InputRequired()])
    
class CustomerAddress(FlaskForm):    
    city=StringField("City",validators=[InputRequired()])
    state=SelectField("State",choices=dict_to_list(US_STATES),validators=[InputRequired()])



