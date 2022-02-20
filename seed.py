from datetime import datetime
from models import Teacher, Student,db,connect_db,Invoice
from app import app
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt()
# Create all tables
db.drop_all()
db.create_all()

password=bcrypt.generate_password_hash('123456').decode('UTF-8')

t1=Teacher(account_id="acct_1KTzulDEIfAFUi70",account_status="complete",email='wiltfong.michael1@gmail.com', username='mdwiltfong', password=password)
t2=Teacher(account_id="acct_1KVKk3RVajsjiwfo",account_status="complete",email='dubuc.andrea@gmail.com', username='lemon_bunny', password=password)
t3=Teacher(account_status="complete",email='teach3@teacher.com', username='ProfessorMcGonagall', password=password)

s1=Student(name="Ron Weasley",email="angryteen@students.com",username="RonWeasley",password=password)
s2=Student(name="Harry Potter",email="teachme@students.com",username="HarryPotter",password=password)
s3=Student(name="Hermione Granger",email="hottopc@students.com",username="HermioneGranger",password=password)

inv1=Invoice(service="Charms Tutoring",hourly_rate=12,start_date=datetime.now(),cadence="monthly")
inv2=Invoice(service="Potions Tutoring",hourly_rate=12,start_date=datetime.now(),cadence="monthly")
inv3=Invoice(service="Quidditch Tutoring",hourly_rate=12,start_date=datetime.now(),cadence="monthly")


t1.students.append(s1)
t2.students.append(s2)
t3.students.append(s3)
t1.invoices.append(inv1)
t2.invoices.append(inv2)
t3.invoices.append(inv3)
s1.invoices.append(inv1)
s2.invoices.append(inv2)
s3.invoices.append(inv3)

db.session.add_all([t1,t2,t3,s1,s2,s3,inv1,inv2,inv3])
db.session.commit()
