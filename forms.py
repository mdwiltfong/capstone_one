from unicodedata import name
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, BooleanField,RadioField,SelectField, PasswordField
from wtforms.validators import InputRequired, Email, Optional
from countries import US_STATES,months
from helper_functions import dict_to_list

class AddCustomer(FlaskForm):
    email=StringField("Email", validators=[InputRequired(),Email()])
    username=StringField("Username", validators=[InputRequired()])
    password=PasswordField("Password",validators=[InputRequired()])
    
class PaymentDetails(FlaskForm):    
    name=StringField("Name (as it appears on your card)",validators=[InputRequired()])
    card_number=StringField("Card Number (no dashes or spaces)",validators=[InputRequired()])
    expirary_month=SelectField("",choices=dict_to_list(months),validators=[InputRequired()])
    city=StringField("City",validators=[InputRequired()])
    state=SelectField("State",choices=dict_to_list(US_STATES),validators=[InputRequired()])
    country=StringField("Country",validators=[InputRequired()])
    address_1=StringField("Address Line 1",validators=[InputRequired()])
    address_2=StringField("Address Line 2",validators=[Optional()])
    postal_code=StringField("Postal Code",validators=[InputRequired()])


class StudentLogin(FlaskForm):
    username=StringField("Username",validators=[InputRequired()])
    password=PasswordField("Password",validators=[InputRequired()])


