from http import client
from unicodedata import name
from unittest import TestCase
import unittest
from flask import request,session
from sqlalchemy import null
from app import app
from forms import PaymentDetails
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
        test_user=Student(email="test@test.com",username="test21312",password="test")
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
         
        
        user= Student.query.filter_by(username="tester91").first() if Student.query.filter_by(username="tester91").first() else Teacher.query.filter_by(username="teachertest").first()
       
    
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
            s=Student.query.filter_by(username='tester91').first()
            print(s.id)
            self.assertIsNotNone(session['curr_user'])
                        
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
    @unittest.skip
    def test_stripe_signup(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['student']=True
                sess['curr_user']=2

            student=Student.query.get(sess['curr_user'])
            ''' resp=client.post("/get-started/payment",data={
                "city": "Test City",
                "name": "Test Stripe Client",
                "country":"US",
                "address_1":"8 Bishops Mills Way",
                "address_2": None,
                "postal_code":"89052",
                "state":"TX",
                "card_number":"4242424242424242",
                "expiration":"01/25"
            }) '''

            resp=client.get("/get-started/payment")
            html=resp.get_data(as_text=True)

        s=Student.query.get(2)
        self.assertEqual(resp.status_code,200)
        self.assertIn('Billing Address',html)
        