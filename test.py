from http import client
import json
from unittest import TestCase
import unittest
from flask import request,session
from sqlalchemy import null, true
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
            teacher=Teacher.query.filter_by(username="teachertest").first()
            self.assertEqual(resp.status_code, 200)
            self.assertIn("/teacher/plan/prices",request.path)
            self.assertEqual(session['curr_user'],teacher.stripe_id)   



class TeacherStripeOnboarding(TestCase):
    def setUp(self):
        with app.test_client() as client:
            resp=client.post("/teacher/signup",data={
                "username":"stripe_testuser",
                "email": "wiltfong.michael1@gmail.com",
                "password": "123456"
            })

    def tearDown(self):
        teacher=Teacher.query.filter_by(username="stripe_testuser").first()
        stripe.Customer.delete(teacher.stripe_id)
        db.session.query(Teacher).filter(Teacher.username=="stripe_testuser").delete()
        db.session.commit()

    def test_teacher_signup(self):
        teacher=Teacher.query.filter_by(username="stripe_testuser").first()
        self.assertIsNotNone(teacher.stripe_id)
    
    @unittest.skip
    def test_teacher_subscription(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                teacher=Teacher.query.filter_by(username="stripe_testuser").first()
                sess["curr_user"]=teacher.stripe_id

            resp=client.post("/teacher/plan/prices",data={
                'plan': "prod_L3c8LwHYwslzi1",
                'name':'Michael Wiltfong',
                'card_number':"4242424242424242",
                'expiration':'01/25',
                'city':'Kanata',
                'state':'AL',
                'country':'US',
                'address_1':'8 Bishops Mills Way',
                'address_2':None,
                'postal_code':'K2K3B9'
            })
            html=resp.get_data(as_text=true)
        
        ## TODO: This test is not passing the form.validate function. 
        self.assertIn("TEST",html)
        self.assertEqual(resp.status_code,200)

            
            

        