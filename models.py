from datetime import datetime
import json
from locale import currency
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify,session 
import stripe
import os
from dotenv import load_dotenv, find_dotenv
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
        primary_key=True
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
                            backref='teachers'
    )

    address=db.relationship("Address")

    @classmethod
    def signup(cls,username,email,password):
        hashed_pwd=bcrypt.generate_password_hash(password).decode('UTF-8')
        new_teacher=Teacher(
            username=username,
            email=email,
            password=hashed_pwd          
        )
        customer=stripe.Customer.create(
                email=new_teacher.email,
                metadata={
                    "username": new_teacher.username,
                    "db_id":new_teacher.id,
                    "customer_type":"teacher"
                }
            )
        new_teacher.stripe_id=customer.id
        db.session.add(new_teacher)
        return new_teacher
    @classmethod
    def create_subscription(cls,customer_id,price):      
        try:
            subscription=stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    'price': price["id"]
                }],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )
            return {
                "subscriptionId":subscription.id,
                "clientSecret":subscription.latest_invoice.payment_intent.client_secret
                }
        except Exception as e:
            return jsonify(error={'message': e}), 400
    @classmethod
    def create_paymentintent(cls,price,customer_stripe_id):
        intent=stripe.PaymentIntent.create(
            amount=price["unit_amount"],
            currency="usd",
            automatic_payment_methods={"enabled":True},
            customer=customer_stripe_id
        )
        return {
            "client_secret":intent["client_secret"]
            }
    @classmethod
    def authentication(cls,username,password):
            teacher=Teacher.query.filter_by(username=username).first()
            if teacher:
                is_auth = bcrypt.check_password_hash(teacher.password, password)
                
                if is_auth:
                    return teacher
            return False

class Student(db.Model):
    __tablename__='students'

    id = db.Column(
        db.Integer,
        primary_key=True
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
        nullable=False,
        unique=True,
    )
    password = db.Column(
        db.Text,
        nullable=False,
    )

    
    def __repr__(self):
        return f"<Student #{self.id}: {self.username}, {self.email}>"

    address=db.relationship("Address")

    @classmethod
    def signup(cls,username,email,password):
        hashed_pwd=bcrypt.generate_password_hash(password).decode('UTF-8')
        new_student=Student(
            username=username,
            email=email,
            password=hashed_pwd          
        )
        db.session.add(new_student)
        return new_student

        ## TO-DO: add more error handling to this method versus on ther server. Throw-catch methodology. 
    @classmethod
    def stripe_signup(cls,student,form):
        try:
            customer=stripe.Customer.create(
                name= student.address[0].name,
                email=student.email,
                metadata={
                    "username": student.username,
                    "db_id":student.id,
                    "customer_type":"student"
                },
                address={
                    "city":student.address[0].city,
                    "country": 'US',
                    "line1":student.address[0].address_1,
                    "line2":student.address[0].address_2,
                    "postal_code":student.address[0].postal_code,
                    "state":student.address[0].state
                }
            )
            student_address=student.address[0]
            card=stripe.PaymentMethod.create(
                    type="card",
                    billing_details={
                        "address":{
                            "city":student_address.city,
                            "country":"US",
                            "line1":student_address.address_1,
                            "line2":student_address.address_2,
                            "postal_code":student_address.postal_code,
                            "state":student_address.state
                        }
                    },
                    card={
                        "number": form.card_number.data,
                        "exp_month":f"{form.expiration.data : %m}".strip(),
                        "exp_year":f"{form.expiration.data : %y}".strip()
                    }
                ) or None
            if card:
                    payment_method=stripe.PaymentMethod.attach(
                    card.id,
                    customer=customer.stripe_id
                )
            
            return {
                "customer":customer,
                "card":card,
                "payment_method":payment_method
            }
        except Exception as err:
            print(err)
        else:
            print("Stripe Sign On done")

    @classmethod
    def authentication(cls,username,password):
      
            student=Student.query.filter_by(username=username).first()
            if student:
                is_auth = bcrypt.check_password_hash(student.password, password)
                print(is_auth)
                if is_auth:
                    return student
            return False



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

class Address(db.Model):
    __tablename__='addresses'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id=db.Column(db.Integer,
                        db.ForeignKey("students.id",ondelete="cascade")
    )

    teacher_id=db.Column(db.Integer,
                        db.ForeignKey("teachers.id", ondelete="cascade")
    )

    name=db.Column(
        db.String,
        nullable=False
    )

    city=db.Column(
        db.Text,
        nullable=False
    )

    country=db.Column(
        db.String(50),
        nullable=False
    )

    address_1=db.Column(
        db.Text,
        nullable=False
    )

    address_2=db.Column(
        db.Text,
        nullable=True
    )

    postal_code=db.Column(
        db.Text,
        nullable=False
    )

    state=db.Column(
        db.Text,
        nullable=False
    )

    def __repr__(self):
        return f"<Address #{self.id}: {self.student_id}, {self.id}>"


