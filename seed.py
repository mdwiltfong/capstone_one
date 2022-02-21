from datetime import datetime
from models import Teacher, Student,db,connect_db,Invoice
from app import app
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt()
# Create all tables
db.drop_all()
db.create_all()

password=bcrypt.generate_password_hash('123456').decode('UTF-8')


t1=Teacher(city="Detroit",state="Michigan",account_id="acct_1KTzulDEIfAFUi70",account_status="complete",email='wiltfong.michael1@gmail.com', username='mdwiltfong', password=password)
t2=Teacher(city="Detroit",state="Michigan",account_id="acct_1KVKk3RVajsjiwfo",account_status="complete",email='dubuc.andrea@gmail.com', username='lemon_bunny', password=password)
t3=Teacher(city="Detroit",state="Michigan",account_status="complete",email='teach3@teacher.com', username='ProfessorMcGonagall', password=password)

s1=Student(name="Andrea Dubuc",email="dubuc.andrea@gmail.com",stripe_id="cus_LBHwFu4e4jOoI4",subscription_status="active",subscription_id="sub_1KUvNqDEIfAFUi70YzkIXL4a")
s2=Student(name="Harry Potter",email="wiltfong.michael1@gmail.com",stripe_id="cus_LBHtfyDJvnziAa",subscription_status="active",subscription_id="sub_1KUvK2DEIfAFUi70yR0wj5Go")



t1.students.append(s1)
t2.students.append(s2)


db.session.add_all([t1,t2,t3,s1,s2])
db.session.commit()
