from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

    
class Teachers(db.Model):
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



class Students(db.Model):
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

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    def __repr__(self):
        return f"<Student #{self.id}: {self.username}, {self.email}>"
