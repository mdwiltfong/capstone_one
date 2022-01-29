import os
from dotenv import load_dotenv, find_dotenv

from flask import Flask, render_template, request, flash, redirect, session, g,abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import Teacher, Student,db,connect_db, Address
from forms import AddCustomer,CustomerAddress
import stripe


#PSQL_CONNECTION_STRING=os.getenv('PSQL_CONNECTION_STRING')


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
            
        except IntegrityError:
            db.session.rollback()
            existing = Student.query.filter_by(email=form.email.data).one()
            flash('* EMAIL IN USE: {} *'.format(existing.email))
            return redirect('/get-started/auth')

    return render_template('add_customer.html',form=form)

@app.route('/get-started/payment',methods=["GET","POST"])
def customer_billing():
    form=CustomerAddress()
    if "curr_user" in session:
        student=Student.query.get(session["curr_user"])
    else:
        flash('You need to be logged in')
        return redirect('/')

    if form.validate_on_submit():
            new_address=Address(
                city=form.city.data,
                country=form.country.data,
                address_1=form.address_1.data,
                postal_code=form.postal_code.data,
                state=form.state.data,
                address_2= form.address_2.data or None
            )
            student.address.append(new_address)

            db.session.add(student)
            db.session.commit()
            new_stripe_customer=Student.stripe_signup(student)

            print(new_stripe_customer)
            flash("You've registered!")            
            return redirect('/')
    return render_template('add_payment_details.html',form=form)
            