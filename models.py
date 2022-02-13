from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
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

    plan=db.Column(
       db.Text,
        nullable=True

    )
    
    subscription_status=db.Column(
        db.Text,
        nullable=True
    )
    subscription_id=db.Column(
        db.Text,
        nullable=True
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
    def authentication(cls,username,password):
            teacher=Teacher.query.filter_by(username=username).first()
            if teacher:
                is_auth = bcrypt.check_password_hash(teacher.password, password)
                subscription_status=teacher.subscription_status
                if is_auth and subscription_status=="active":
                    return teacher
            return False

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
    def signup(cls,form):

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
                }
            )
        new_student.stripe_id=customer.id
        db.session.add(new_student)
        db.session.commit()
        return new_student


    @classmethod
    def create_subscription(cls,customer_id,form):      
        try:
            price=create_product_stripe(customer_id,form)
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
    def authentication(cls,username,password):
      
            student=Student.query.filter_by(username=username).first()
            if student:
                is_auth = bcrypt.check_password_hash(student.password, password)
                print(is_auth)
                if is_auth:
                    return student
            return False




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