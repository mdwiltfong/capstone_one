from http import client
from unittest import TestCase
from flask import request,session
from sqlalchemy import null
from app import app
from models import Student, db,connect_db,Teacher
import stripe
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

API_KEY=os.getenv('API_KEY')

stripe.api_key=API_KEY

app.config['WTF_CSRF_ENABLED'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///teach'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

class OnBoarding(TestCase):
    def setUp(self):
        s1=Student(email="test@students.com",username="test01",password="123456")
        t1=Teacher(email='testteacher1@teacher.com', username='testteacher', password="123456")
        db.session.add_all([s1,t1])
        db.session.commit()
    def tearDown(self):
        user=Student.query.filter_by(username="tester91").first() or Teacher.query.filter_by(username="teachertest")
        print("tearDown")
        print(user)
        if user.username == "tester91":
            db.session.query(Student).filter(Student.username=="tester91").delete()
            db.session.commit()
        else:
            db.session.query(Teacher).filter(Teacher.username=="teachertest").delete()
            db.session.commit()

    def test_student_signup(self):
        with app.test_client() as client:
            resp=client.post("/student/signup",data={
                "username":"tester91",
                "email":"test91@students.com",
                "password":"123456"
            }, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("/get-started/payment",request.path)
            self.assertIsNotNone(session['curr_user'])


    def test_stripe_paymentmethod(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                s=Student.query.filter_by(username="tester91").first()
                sess['curr_user']=s.id
                sess['student']=True
            resp=client.post("/get-started/payment",data={
                    "name":"Test User",
                    "card_number": "4242424242424242",
                    "expiration":"01/25",
                    "city":"Kanata",
                    "country":"US",
                    "line1":"8 Bishops Mills Way",
                    "line2": None,
                    "postal_code": "89052",
                    "state":"TX"
                    },follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            s=Student.query.filter_by(username="tester91").first()
            
    def test_teacher_signup(self):
        with app.test_client() as client:
            resp=client.post("/teacher/signup",data={
                "username":"teachertest",
                "email":"teachertest@teachers.com",
                "password":"123456"
            }, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("/get-started/payment",request.path)
            self.assertIsNotNone(session['curr_user'])

    


        