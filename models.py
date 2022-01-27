from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

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
                        db.ForeignKey("students.id")
    )

    city=db.Column(
        db.Text,
        nullable=False
    )

    country=db.Column(
        db.String(2),
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

    

