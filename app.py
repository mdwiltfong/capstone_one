
import os
import pdb
from flask import Flask, render_template, flash, redirect, session, jsonify,request,send_file
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import Teacher, Student,db,connect_db,Quote
from forms import AddCustomer,StudentLogin, SubscriptionPlan,TeacherInvoice,QuoteForm
from helper_functions import convert_quote
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



@app.route("/about")
def load_about():
    return render_template("about.html")
@app.route('/logout')
def logout():
    if "curr_user" in session:
        session.pop("curr_user")
        flash("See you next time!","success")
        return redirect("/")

#####################################Student Routes


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
            new_teacher_acct=Teacher.signup(
                form
            )

            session["curr_user"]=new_teacher_acct["new_account"]["id"]
            session["teacher"]=True

            return redirect(new_teacher_acct["acc_link"]["url"])
        except IntegrityError as err:
            db.session.rollback()
            existing = Teacher.query.filter_by(email=form.email.data).first()
            flash('* EMAIL IN USE: {} *'.format(existing.email))
            return redirect('/teacher/signup')

    return render_template('add_teacher.html',form=form)

@app.route("/teacher/signup/success",methods=["GET","POST"])
def signup_successful():
    flash("Signup Successful","success")
    return redirect(f'/teacher/{session["curr_user"]}/profile')
######Invoices Created By Teachers#############

@app.route("/teacher/invoice",methods=["GET","POST"])
def teacher_invoice():
    form = TeacherInvoice()
    if "curr_user" not in session:
        flash("You need to be logged in","danger")
        return redirect("/")
    teacher=Teacher.query.filter_by(account_id=session["curr_user"]).first()
    if form.validate_on_submit():
        try:
            new_student=Student.signup(form,teacher)
            if new_student is None:
                raise Exception("Student already added")
            quote=Student.create_quote(new_student,form,session["curr_user"])
            #resp= Student.create_subscription(new_student.stripe_id,form,session["curr_user"])
            if quote.get("error",False):
                flash("There was an issue making the Invoice","danger")
                return redirect(f'/teacher/{teacher.account_id}/profile')

            #flash("Invoice Sent","success")
            #return redirect(f'/teacher/{teacher.account_id}/profile')
            return redirect("/teacher/quote/download")
        except Exception as e:
            flash("Student Already Added", "danger")
            return redirect(f'/teacher/{teacher.account_id}/profile')
    return render_template("invoice_form.html",form=form,teacher=teacher)

@app.route("/teacher/quote/download")
def teacher_quote():
    return send_file("tmp.pdf")






@app.route("/teacher/login", methods=["GET","POST"])
def teacher_login():
    form=StudentLogin()
    if form.validate_on_submit():
        password=form.password.data
        username=form.username.data
        teacher=Teacher.authentication(username,password)
        if teacher:
            session["curr_user"]=teacher.account_id
            session["subscription_status"]=teacher.account_status
            session["teacher"]=True
            flash("You've logged in!","success")
            return redirect("/")
        else:
            flash("Hmmm, password or username are incorrect","danger")
            return redirect("/teacher/login")
    
    return render_template("teacher_login.html",form=form)

@app.route("/convert_quote",methods=["POST", "GET"])
def quote_list():
    form=QuoteForm()
    if form.validate_on_submit():

        data=request.form
        student_email=data["student_email"]
        student_name=data["student_name"]
        try:
            student=Student.query.filter(Student.email==student_email,Student.name==student_name).first()
            quote=stripe.Quote.retrieve(student.quote[0].stripeid,
            stripe_account=student.teacher[0].account_id
            )   
            line_items=stripe.Quote.list_line_items(quote["id"],
            stripe_account=student.teacher[0].account_id
            )
            description=line_items["data"][0]['description']
            session["quote_id"]=quote["id"]
            session["account_id"]=student.teacher[0].account_id
            if student is None:
                raise Exception
            return render_template("convert_quote.html",form=form,quote=quote,student=student,description=description)
        except Exception as e:
            flash("Hmm, there was an issue looking up your quote", "danger")
            return redirect("/convert_quote")
    return render_template("convert_quote.html",form=form)

@app.route("/handle_quote",methods=["post","get"])
def handle_quote():
    #TODO We are creating subscriptions and quotes on the connected account. We should gather customer payment info for charging them later. 
    try:
        resp=stripe.Quote.accept(session["quote_id"],
        stripe_account=session["account_id"]   
        )
        invoice=stripe.Invoice.finalize_invoice(resp["invoice"],
        stripe_account=session["account_id"],
            expand=["payment_intent"]
        )
        session["client_secret"]=invoice["payment_intent"]["client_secret"]
    except Exception as e:
        flash("There was an issue accepting the quote","danger")
        redirect("/handle_quote")
    return redirect("/checkout")

@app.route("/checkout",methods=["POST","GET"])
def handle_checkout():
    if "curr_user" not in session:
        flash("You must be logged in to access this page","danger");
        return redirect("/")
    return render_template("checkout.html",clientSecret=session["client_secret"])

@app.route("/config",methods=["GET"])
def config_details():
    return jsonify(client_secret=session["client_secret"],account_id=session["account_id"])
@app.route("/checkout_successful",methods=["GET","POST"])
def checkout():
    flash("Payment Successful","success")
    return redirect("/")

@app.route("/teacher/<account_id>/profile",methods=["GET","POST"])
def teacher_profile(account_id):
    if "curr_user" not in session:
        flash("You need to be logged in.", "danger")
        return redirect("/")
    
    teacher=Teacher.query.filter_by(account_id=account_id).first()
    balance=stripe.Balance.retrieve(stripe_account=teacher.account_id)
    available=balance["available"][0]["amount"]/100
    pending=balance["pending"][0]["amount"]/100
    return render_template("teacher_profile.html",teacher=teacher,available_bal=available,pending_bal=pending)


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
        #webhook updates student subscription information and status to active
        student=Student.query.filter_by(stripe_id=data_object["customer"]).first()
        Student.handle_subscription_created(student.stripe_id,data_object)
        
        return jsonify({"status":'success'}), 200

    if event_type=="customer.subscription.updated":
        #Webhook listens for subscriptions that become past_due
        student=Student.query.filter(Student.subscription_id==data_object["id"]).first()
        student.subscription_status=data_object["status"]
        db.session.add(student)
        db.session.commit()

        return jsonify(student_id=student.stripe_id,subscription_status=student.subscription_status), 200


    if event_type=="account.updated":
        #during onboarding the account status of the teacher will be `restricted`, until the webhook confirms all details are submited
        try:
            teacher=Teacher.query.filter(Teacher.account_id == data_object["id"], Teacher.account_status != 'complete').first()
            if teacher is None:
                raise Exception("Teacher status is already complete")
            if data_object["details_submitted"]:
                teacher.account_status="complete"
                db.session.add(teacher)
                db.session.commit()
        except Exception as e:
            return e
    if event_type =="quote.finalized" or "quote.accepted":
        try:
            quote=Quote.query.filter(Quote.stripeid == data_object["id"]).first()
            if quote is None:
                raise Exception("Quote not found")
            quote.quote_status=data_object["status"]
            db.session.add(quote)
            db.session.commit()
        except Exception as e:
            return e

    return jsonify({'status': 'success'})