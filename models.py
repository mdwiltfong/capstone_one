from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
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
    first_name=db.Column(
        db.Text, 
        nullable=False
    )

    last_name=db.Column(
        db.Text,
        nullable=False
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
    def signup(cls,username,email,password,first_name,last_name):
        hashed_pwd=bcrypt.generate_password_hash(password).decode('UTF-8')
        new_student=Student(
            username=username,
            email=email,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name            
        )
        db.session.add(new_student)
        return new_student
    @classmethod
    def stripe_signup(cls,student):
        try:
            customer=stripe.Customer.create(
                name= f'{student.first_name} {student.last_name}',
                email=student.email,
                metadata={
                    "username": student.username
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
            print(customer)
            return customer
        except Exception as err:
            print(err)
        else:
            print("Stripe Sign On done")

class Teacher_Student(db.Model):
    __tablename__='teachers_students'
    teacher_id=db.Column(db.Integer,
                        db.ForeignKey("teachers.id"),
                        primary_key=True
            )
    student_id=db.Column(db.Integer,
                        db.ForeignKey("students.id"),
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


