import stripe
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

API_KEY=os.getenv('API_KEY')

stripe.api_key=API_KEY


def dict_to_list(dict):
    array=dict.items()
    result=[]
    for element in array:
        result.append(element)
    return result


# Stripe helper functions

def stripe_signup(student):
    stripe.Customer.create(
        first_name=student.first_name,
        last_name = student.last_name,
        email=student.email,
        username = student.username,
        address={
            city:student.address[0].city,
            country: 'US',
            line1:student.address[0].address_1,
            line2:student.address[0].address_2,
            postal_code:student.address[0].postal_code,
            state:student.address[0].state
        }
    )
