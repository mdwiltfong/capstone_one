
import os
import pdb
from flask import Flask, render_template, flash, redirect, session, jsonify,request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import Teacher, Student,db,connect_db
from forms import AddCustomer,PaymentDetails,StudentLogin, SubscriptionPlan,TeacherInvoice
from helper_functions import invoice_price
import stripe
import json

#PSQL_CONNECTION_STRING=os.getenv('PSQL_CONNECTION_STRING')


DOMAIN="http://127.0.0.1:5000"

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
    return render_template("signup.html")


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

            session["curr_user"]=new_teacher.stripe_id
            session["teacher"]=True

            return redirect('/teacher/plan/prices')
        except IntegrityError as err:
            db.session.rollback()
            existing = Teacher.query.filter_by(email=form.email.data).first()
            flash('* EMAIL IN USE: {} *'.format(existing.email))
            return redirect('/teacher/signup')

    return render_template('add_teacher.html',form=form)


@app.route("/teacher/plan/prices",methods=["GET","POST"])
def create_checkout_session():
    form=SubscriptionPlan()

    if form.validate_on_submit():
        price=stripe.Price.retrieve(form.plan.data)
        subscription=Teacher.create_subscription(session["curr_user"],price)
        session["client_secret"]=subscription["clientSecret"]
        return redirect("/checkout")
    return render_template('subscription_list.html',form=form)

@app.route("/create-payment-intent",methods=["GET","POST"])
def create_payment_intent():
    return jsonify(client_secret=session["client_secret"])


@app.route("/checkout",methods=["GET","POST"])
def checkout():
    return render_template('checkout.html')
@app.route("/teacher/plan/prices/success",methods=["GET","POST"])
def success_page():
    flash("Payment Succeeded!","success")
    return redirect("/")

######Invoices Created By Teachers#############

@app.route("/teacher/invoice",methods=["GET","POST"])
def teacher_invoice():
    form = TeacherInvoice()
    if "curr_user" not in session:
        flash("You need to be logged in","danger")
        return redirect("/")
    teacher=Teacher.query.filter_by(stripe_id=session["curr_user"]).first()
    if form.validate_on_submit():
        new_student=Student.signup(form,teacher)
        resp= Student.create_subscription(new_student.stripe_id,form)
        if resp.get("error",False):
            flash("There was an issue making the Invoice","danger")
            return redirect(f'/teacher/{teacher.stripe_id}/profile')

        flash("Invoice Sent","success")
        return redirect(f'/teacher/{teacher.stripe_id}/profile')
    return render_template("invoice_form.html",form=form,teacher=teacher)





@app.route("/teacher/login", methods=["GET","POST"])
def teacher_login():
    form=StudentLogin()
    if form.validate_on_submit():
        password=form.password.data
        username=form.username.data
        teacher=Teacher.authentication(username,password)
        if teacher:
            session["curr_user"]=teacher.stripe_id
            session["subscription_status"]=teacher.subscription_status
            session["teacher"]=True
            flash("You've logged in!","success")
            return redirect("/")
        else:
            flash("Hmmm, password or username are incorrect","danger")
            return redirect("/teacher/login")
    
    return render_template("teacher_login.html",form=form)

@app.route("/teacher/<stripe_id>/profile",methods=["GET","POST"])
def teacher_profile(stripe_id):
    if "curr_user" not in session:
        flash("You need to be logged in.", "danger")
        return redirect("/")
    
    teacher=Teacher.query.filter_by(stripe_id=stripe_id).first()
    teacher.username
    return render_template("teacher_profile.html",teacher=teacher)


@app.route("/webhook",methods=["POST"])
def webhook_received():
    WEBHOOK_SECRET=os.getenv('WEBHOOK_SECRET')
    incoming_data=json.loads(request.data)
    if WEBHOOK_SECRET:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, 
                sig_header=signature, 
                secret=WEBHOOK_SECRET                
                )
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = incoming_data['data']
        event_type = incoming_data['type']

    data_object = data['object']

    if event_type == "customer.subscription.created":
        customer=Teacher.query.filter_by(stripe_id=data_object["customer"]).first()
        if customer:
            Teacher.handle_subscription_created(customer.stripe_id,data_object)
        else:
            customer=Student.query.filter_by(stripe_id=data_object["customer"]).first()
            Student.handle_subscription_created(customer.stripe_id,data_object)
        
        

    if event_type=="customer.subscription.updated":
        subscription_status=data_object["status"]
        customer_id=data_object["customer"]
        teacher=Teacher.query.filter_by(stripe_id=customer_id).first()
        teacher.subscription_status=subscription_status
        db.session.add(teacher)
        db.session.commit()

    return jsonify({'status': 'success'})