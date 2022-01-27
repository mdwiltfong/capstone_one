from models import Teachers, Students,db,connect_db
from app import app
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt()
# Create all tables
db.drop_all()
db.create_all()

password=bcrypt.generate_password_hash('123456').decode('UTF-8')

t1=Teachers(email='teach1@teacher.com', username='homeworkqueen92', password=password)
t2=Teachers(email='teach2@teacher.com', username='YourIdealTeacher', password=password)
t3=Teachers(email='teach3@teacher.com', username='ProfessorMcGonagall', password=password)

s1=Students(email="angryteen@students.com",username="RonWeasley",password=password)
s2=Students(email="teachme@students.com",username="HarryPotter",password=password)
s3=Students(email="hottopc@students.com",username="HermioneGranger",password=password)

db.session.add_all([t1,t2,t3,s1,s2,s3])
db.session.commit()
