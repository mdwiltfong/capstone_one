from importlib.metadata import metadata
from locale import currency
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


def invoice_price(form):
    """ returns invoice price in cents"""
    hourly_rate=form.hourly_rate.data * 100
    hours=form.hours.data
    return hourly_rate*hours

def create_product_stripe(service,teacher_stripeid,form):
    price=stripe.Price.create(
        unit_amount=invoice_price(form),
        currency="usd",
        recurring={"interval":form.cadence.data},
        product_data={
            "name":service,
            "metadata":{
                "customer":teacher_stripeid,
            }
        }
    )
    return price


