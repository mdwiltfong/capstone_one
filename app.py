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


@app.route('/get-started/auth',methods=["GET","POST"])
def add_customer():
    form=AddCustomer()
    if form.validate_on_submit():
        try:
            new_student=Student.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                last_name=form.last_name.data,
                first_name=form.first_name.data
            )

            db.session.commit()

            session["curr_user"]=new_student.id

            return redirect('/get-started/payment')
        except IntegrityError as err:
            db.session.rollback()
            existing = Student.query.filter_by(email=form.email.data).one()
            flash('* EMAIL IN USE: {} *'.format(existing.email))
            return redirect('/get-started/auth')

    return render_template('add_customer.html',form=form)

@app.route('/get-started/payment',methods=["GET","POST"])
def customer_billing():
    form=AddCustomer()
        if "curr_user" in session:
                    student=Student.query.get(session["curr_user"])
        else:
            flash('You need to be logged in')
            return redirect('/')

    if form.validate_on_submit():
            new_address=Address.signup(
                city=form.city.data,
                country=form.country.data,
                address_1=form.address_1.data,
                address_2=form.address_2.data,
                postal_code=form.postal_code.data,
                state=form.state.data
            )
            student.address.append(new_address)
            db.session.add(student)
            db.session.commit()
            flash("You've registered!")            
            return redirect('/')
    return render_template('add_payment_details.html',form=AddCustomer)
            