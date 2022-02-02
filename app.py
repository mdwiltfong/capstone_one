from itertools import product
import os
from dotenv import load_dotenv, find_dotenv

from flask import Flask, render_template, request, flash, redirect, session, g,abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import Teacher, Student,db,connect_db, Address
from forms import AddCustomer,PaymentDetails,StudentLogin
import stripe

#PSQL_CONNECTION_STRING=os.getenv('PSQL_CONNECTION_STRING')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///teach'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)
connect_db(app)
db.create_all()

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route("/signup")
def signup():
    return render_template("signup.html",message="Hey")

@app.route('/get-started/payment',methods=["GET","POST"])
def customer_billing():
    form=PaymentDetails()
    
    print('Test')
    ## TODO #18 This rooute doesn't need this much logic. Instead route `/teacher/login` and `student/login` need this 
    if session.get('student',None) or session.get('teacher',None):
        client=Student.query.get(session["curr_user"]) or Teacher.query.get(session["curr_user"])
        if client.stripe_id:
            return redirect('/')
    else:
        flash('You need to be logged in')
        return redirect('/', code=404)

    if form.validate_on_submit():
            new_address=Address(
                city=form.city.data,
                name=form.name.data,
                country=form.country.data,
                address_1=form.address_1.data,
                postal_code=form.postal_code.data,
                state=form.state.data,
                address_2= form.address_2.data or None
            )
            client.address.append(new_address)
            print(client,form)
            new_stripe_customer=Student.stripe_signup(client,form)
            client.stripe_id=new_stripe_customer["customer"].id
            db.session.add(client)
            db.session.commit()
            flash("You've registered!","success")            
            return redirect('/')
    return render_template('add_payment_details.html',form=form)


@app.route('/logout')
def logout():
    if "curr_user" in session:
        session.pop("curr_user")
        flash("See you next time!","success")
        return redirect("/")

#####################################Student Routes


@app.route("/student/login", methods=["GET","POST"])
def student_login():
    form=StudentLogin()
    if form.validate_on_submit():
        password=form.password.data
        username=form.username.data
        student=Student.authentication(username,password)
        if student:
            session["curr_user"]=student.id
            flash("You've logged in!","success")
            return redirect("/")
        else:
            flash("Hmmm, password or username are incorrect","danger")
            return redirect("/student/login")
    
    return render_template("student_login.html",form=form)

@app.route('/student/signup',methods=["GET","POST"])
def add_student():
    form=AddCustomer()
    if form.validate_on_submit():
        try:
            new_student=Student.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )

            db.session.commit()

            session["curr_user"]=new_student.id
            session["student"]=True

            return redirect('/get-started/payment')
        except IntegrityError as err:
            print(err)
            db.session.rollback()
            existing = Student.query.filter_by(email=form.email.data).first()
            flash('* EMAIL IN USE: {} *'.format(existing.email))
            return redirect('/get-started/auth')

    return render_template('add_student.html',form=form)

###########################teacher routes

@app.route('/teacher/signup',methods=["GET","POST"])
def add_teacher():
    form=AddCustomer()
    if form.validate_on_submit():
        try:
            new_teacher=Teacher.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )

            db.session.commit()

            session["curr_user"]=new_teacher.id
            session["teacher"]=True

            return redirect('/teacher/plan/prices')
        except IntegrityError as err:
            print(err)
            db.session.rollback()
            existing = Teacher.query.filter_by(email=form.email.data).first()
            flash('* EMAIL IN USE: {} *'.format(existing.email))
            return redirect('/get-started/auth')

    return render_template('add_teacher.html',form=form)

@app.route("/teacher/login", methods=["GET","POST"])
def teacher_login():
    form=StudentLogin()
    if form.validate_on_submit():
        password=form.password.data
        username=form.username.data
        teacher=Teacher.authentication(username,password)
        if teacher:
            session["curr_user"]=teacher.id
            flash("You've logged in!","success")
            return redirect("/")
        else:
            flash("Hmmm, password or username are incorrect","danger")
            return redirect("/teacher/login")
    
    return render_template("teacher_login.html",form=form)

@app.route("/teacher/plan/prices",methods=["GET","POST"])
def plan_prices():
    products=stripe.Product.list(limit=2)
    prices=stripe.Price.list(limit=2)

     ## TODO The api separates PRICES and PRODUCTS. Two API calls will have to be made here in order to render the data. This information needs to come from the API since it's needed to make subscriptions and invoices. 
    print(prices)
    return render_template('subscription_list.html',prices=prices.data,products=products.data)
