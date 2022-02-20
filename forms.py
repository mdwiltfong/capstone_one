from ssl import create_default_context
from tokenize import String
from unicodedata import name
from flask_wtf import FlaskForm
from wtforms import StringField,SelectField, PasswordField, DateField,RadioField, DecimalField,DateField
from wtforms.validators import InputRequired, Email, Optional,Length,url
from countries import US_STATES,months
from helper_functions import dict_to_list

class AddCustomer(FlaskForm):
    email=StringField("Email", validators=[InputRequired(),Email()])
    username=StringField("Username", validators=[InputRequired()])
    password=PasswordField("Password",validators=[InputRequired(), Length(min=6,message="Password need to be 6 characters in length")])
    photo_url=StringField('Profile Picture',validators=[Optional(),url(message="This is not a valid URL")])
    city=StringField("City", validators=[InputRequired()])
    state=StringField("State", validators=[InputRequired()])
    
class PaymentDetails(FlaskForm):    
    name=StringField("Name (as it appears on your card)",validators=[InputRequired()])
    card_number=StringField("Card Number (no dashes or spaces)",validators=[InputRequired()])
    expiration=DateField("MM / YY",format="%m/%y",validators=[InputRequired()])
    city=StringField("City",validators=[InputRequired()])
    state=SelectField("State",choices=dict_to_list(US_STATES),validators=[InputRequired()])
    country=StringField("Country",validators=[InputRequired()])
    address_1=StringField("Address Line 1",validators=[InputRequired()])
    address_2=StringField("Address Line 2",validators=[Optional()])
    postal_code=StringField("Postal Code",validators=[InputRequired()])


class StudentLogin(FlaskForm):
    username=StringField("Username",validators=[InputRequired("Username is Required")])
    password=PasswordField("Password",validators=[InputRequired("Password is Required"), Length(min=6,message="Password need to be 6 characters in length")])

class SubscriptionPlan(FlaskForm):
    plan = RadioField("Subscription Options",choices=[('price_1KNUuRDBo40mpW7dT4BG7Kzl','Basic Plan'),('price_1KNUv7DBo40mpW7dDF2Vuq81',"Premium Plan")])

class TeacherInvoice(FlaskForm):
    student_name=StringField("Student Name", validators=[InputRequired()])
    student_email=StringField("Student Email",validators=[InputRequired(),Email()])
    service_field=StringField("Service",validators=[InputRequired()])
    hourly_rate=DecimalField("Hourly Rate",validators=[InputRequired()])
    sessions=DecimalField("Number of Sessions",validators=[InputRequired()])    
    cadence=SelectField("Cadence",choices=[("month","Monthly"),("week","Weekly")])

class QuoteForm(FlaskForm):
    student_name=StringField("Student Name", validators=[InputRequired()])
    student_email=StringField("Student Email",validators=[InputRequired(),Email()])