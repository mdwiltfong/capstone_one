from unittest import TestCase
from flask import request,session
from app import app
from models import Student, db,connect_db
app.config['WTF_CSRF_ENABLED'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///teach'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

class OnBoarding(TestCase):
    def setUp(self):
        """ Creates Student """

        s1=Student(email="test@students.com",username="tester92",password="123456")
        db.session.add(s1)
        db.session.commit()
    def tearDown(self):
        """Clearup db from last commit"""
        db.session.rollback()
    def test_signup(self):
        with app.test_client() as client:
            resp=client.post("/get-started/auth",data={
                "username":"mdwiltfong",
                "email":"wiltfong.michael1@gmail.com",
                "password":"123456"
            }, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("/get-started/payment",request.path)
            self.assertIsNotNone(session['curr_user'])
    def test_stripe_paymentmethod(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                s=Student.query.filter_by(username='testers92').first()
                sess['curr_user']=s.id
                resp=client.post("/get-started/payment",data={
                    "name":"Test User",
                    "city":"Test City",
                    "country":"US",
                    "line1":"Test Street"
                })
                self.assertEqual(resp.status_code, 200)
                self.assertIsNotNone(s.stripe_id)



        