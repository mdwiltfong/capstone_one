from models import Teacher, Student,db,connect_db,Address
from app import app
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt()
# Create all tables
db.drop_all()
db.create_all()

password=bcrypt.generate_password_hash('123456').decode('UTF-8')

t1=Teacher(email='teach1@teacher.com', username='homeworkqueen92', password=password)
t2=Teacher(email='teach2@teacher.com', username='YourIdealTeacher', password=password)
t3=Teacher(email='teach3@teacher.com', username='ProfessorMcGonagall', password=password)

s1=Student(email="angryteen@students.com",username="RonWeasley",password=password)
s2=Student(email="teachme@students.com",username="HarryPotter",password=password)
s3=Student(email="hottopc@students.com",username="HermioneGranger",password=password)

a1=Address(city='Devon',country='EN',address_1='Ottery St Catchpole',postal_code='12345',state='ON')
s1.address.append(a1)


t1.students.append(s1)
t2.students.append(s2)
t3.students.append(s3)

db.session.add_all([t1,t2,t3,s1,s2,s3])
db.session.commit()
