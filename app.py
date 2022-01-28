import os
from dotenv import load_dotenv, find_dotenv

from flask import Flask, render_template, request, flash, redirect, session, g,abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import Teacher, Student,db,connect_db
from forms import AddCustomer
import stripe



load_dotenv(find_dotenv())

API_KEY=os.getenv('API_KEY')

stripe.api_key=API_KEY

app = Flask(__name__)
connect_db(app)
db.drop_all()
db.create_all()
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///teach'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

@app.route('/')
def homepage():
    return render_template('index.html',message='Hey')


@app.route('/customers/add',methods=["GET","POST"])
def add_customer():
    form=AddCustomer()
    if form.validate_on_submit():
        Student.signup(form.username.data,form.email.data,form.password.data,form.first_name.data,form.last_name.data)
        db.session.commit()
        flash('Welcome!')
        return render_template('homepage.html')
    return render_template('add_customer.html',form=form)
    