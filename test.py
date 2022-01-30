from unittest import TestCase
from flask import request,session
from sqlalchemy import null
from app import app
from models import Student, db,connect_db
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
    def test_signup(self):
        with app.test_client() as client:
            resp=client.post("/get-started/auth",data={
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
            



        