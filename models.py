from itertools import product
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify,send_file
import stripe
import os
from dotenv import load_dotenv, find_dotenv
from helper_functions import create_product_stripe

load_dotenv(find_dotenv())

API_KEY=os.getenv('API_KEY')

stripe.api_key=API_KEY

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)


class Teacher(db.Model):
    __tablename__='teachers'

    id = db.Column(
        db.Integer,
        autoincrement=True,
        primary_key=True
    )

    
    account_status=db.Column(
        db.Text,
        nullable=True
    )
    account_id=db.Column(
        db.Text,
        nullable=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    def __repr__(self):
        return f"<Teacher #{self.id}: {self.username}, {self.email}>"
    
    students=db.relationship('Student',
                            secondary='teachers_students',
                            backref='teacher'
    )


    @classmethod
    def signup(cls,username,email,password):
        hashed_pwd=bcrypt.generate_password_hash(password).decode('UTF-8')
        new_teacher=Teacher(
            username=username,
            email=email,
            password=hashed_pwd          
        )
        new_account=stripe.Account.create(
            type="express",
            country="US",
            email=email,
            capabilities={
                "card_payments":{"requested":True},
                "transfers":{"requested":True}
            },
            business_type="individual",            
        )

        ## TODO #41 We will need to change the Teacher model to handle this new onboarding
        acc_link=stripe.AccountLink.create(
            account=new_account["id"],
            refresh_url="http://127.0.0.1:5000/teacher/signup",
            return_url="http://127.0.0.1:5000/teacher/signup/success",
            type="account_onboarding"
        )

        new_teacher.account_status='restricted'
        new_teacher.account_id=new_account["id"]
        db.session.add(new_teacher)
        db.session.commit()

        return {
            "new_teacher":new_teacher,
            "new_account":new_account,
            "acc_link":acc_link
        }
    @classmethod
    def create_subscription(cls,customer_id,price):      
        try:
            subscription=stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    'price': price["id"]
                }],
                payment_behavior='default_incomplete',  
                expand=['latest_invoice.payment_intent',]
            )
            return {
                "subscriptionId":subscription.id,
                "clientSecret":subscription.latest_invoice.payment_intent.client_secret
                }
        except Exception as e:
            return jsonify(error={'message': e}), 400
    @classmethod
    def authentication(cls,username,password):
            teacher=Teacher.query.filter_by(username=username).first()
            if teacher:
                is_auth = bcrypt.check_password_hash(teacher.password, password)
                account_status=teacher.account_status
                if is_auth and account_status=="complete":
                    return teacher
            return False
    @classmethod
    def handle_subscription_created(cls,customer_id,data_object):
        subscription_id=data_object["id"]
        customer_id=data_object["customer"]
        teacher=Teacher.query.filter_by(stripe_id=customer_id).first()
        teacher.subscription_id=subscription_id
        teacher.subscription_status=data_object["status"]
        teacher.plan= data_object["plan"]["id"]
        db.session.add(teacher)
        db.session.commit()
class Student(db.Model):
    __tablename__='students'

    id = db.Column(
        db.Integer,
        autoincrement=True,
        primary_key=True
    )
    subscription_status=db.Column(
        db.Text,
        nullable=True
    )
    subscription_id=db.Column(
        db.Text,
        nullable=True
    )
    active_quote_id=db.Column(
        db.Text,
        nullable=True
    )
    name=db.Column(
        db.Text,
        nullable=False
    )

    stripe_id=db.Column(
        db.Text,
        nullable=True
    )
    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )
    username = db.Column(
        db.Text,
        nullable=True,
        unique=True,
    )
    password = db.Column(
        db.Text,
        nullable=True,
    )

    def __repr__(self):
        return f"<Student #{self.id}: {self.name}, {self.email}>"



    @classmethod
    def signup(cls,form,teacher):

        new_student=Student(
            email=form.student_email.data,
            name=form.student_name.data
        )
        customer=stripe.Customer.create(
                email=new_student.email,
                metadata={
                    "username": new_student.username,
                    "db_id":new_student.id,
                    "customer_type":"student"
                },
                stripe_account=teacher.account_id
            )
        new_student.stripe_id=customer.id
        new_student.teacher.append(teacher)
        db.session.add(new_student)
        db.session.commit()
        return new_student

    @classmethod
    def create_quote(cls,student,form,account_id):
        price=create_product_stripe(account_id,form)
        quote=stripe.Quote.create(
            customer=student.stripe_id,
            line_items=[{
                "price": price["id"],"quantity":1
            }],
            collection_method="send_invoice",
            application_fee_percent=10,
            invoice_settings={
                "days_until_due":2
            },
            stripe_account=account_id
        )

        student.active_quote_id=quote["id"]
        db.session.add(student)
        db.session.commit()
        quote=stripe.Quote.finalize_quote(
            quote["id"],
            stripe_account=account_id
            )
        resp=stripe.Quote.pdf(quote["id"],
        stripe_account=account_id
        )
        file=open("tmp.pdf","wb")
        file.write(resp.io.read())
        file.close()
    
        return quote
    @classmethod
    def create_subscription(cls,customer_id,form,account_id):      
        try:

            ## TODO For some reason the subscriptions are created as 'active' despite having an open invoice. 
            price=create_product_stripe(customer_id,form)
            subscription=stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    'price': price["id"]
                }],
                collection_method="send_invoice",
                days_until_due=1,
                expand=['latest_invoice.payment_intent'],
                application_fee_percent=10,
                stripe_account=account_id
            )


            
            return {
                "subscriptionId":subscription.id
                }
        except Exception as e:
            return {
                "error":{
                    "message":e
                }
            }
    @classmethod
    def authentication(cls,username,password):
      
            student=Student.query.filter_by(username=username).first()
            if student:
                is_auth = bcrypt.check_password_hash(student.password, password)
                print(is_auth)
                if is_auth:
                    return student
            return False
    @classmethod
    def handle_subscription_created(cls,customer_id,data_object):
        subscription_id=data_object["id"]
        student=Student.query.filter_by(stripe_id=customer_id).first()
        student.subscription_id=subscription_id
        student.subscription_status=data_object["status"]
        db.session.add(student)
        db.session.commit()

class Invoice(db.Model):
    __tablename__="invoices"

    id = db.Column(
        db.Integer,
        autoincrement=True,
        primary_key=True
    )
    
    teacher_id=db.Column(db.Integer,
                        db.ForeignKey("teachers.id", ondelete="cascade"),        
            )
    student_id=db.Column(db.Integer,
                        db.ForeignKey("students.id",ondelete="cascade"),
    )
    service=db.Column(
        db.Text
    )

    hourly_rate=db.Column(
        db.Integer
    )

    start_date=db.Column(
        db.DateTime
    )

    cadence=db.Column(
        db.Text
    )

    def __repr__(self):
        return f"<Invoice #{self.id}: {self.student_id}, {self.id}>"
        
    student=db.relationship('Student',
                            backref='invoices'
    )
    teacher=db.relationship('Teacher',
                                backref="invoices"
    )


class Teacher_Student(db.Model):
    __tablename__='teachers_students'
    teacher_id=db.Column(db.Integer,
                        db.ForeignKey("teachers.id", ondelete="cascade"),
                        primary_key=True
            )
    student_id=db.Column(db.Integer,
                        db.ForeignKey("students.id",ondelete="cascade"),
                        primary_key=True
    )