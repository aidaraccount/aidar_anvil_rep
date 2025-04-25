import anvil.secrets
import anvil.stripe
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import json


# -----------------------------------------
# 1. SERVER MODULE FOR STRIPE
# -----------------------------------------


@anvil.server.callable
def create_setup_intent():
  import stripe
  import anvil.secrets
  
  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
  intent = stripe.SetupIntent.create(
      usage="off_session"
  )
  
  return intent.client_secret


@anvil.server.callable
def create_stripe_customer(token, email):
  stripe_customer = anvil.stripe.new_customer(email, token)
  print(stripe_customer)
  print(stripe_customer['id'])
  


#   # # get stripe customer
#   # customer = anvil.stripe.get_customer(stripe_customer['id'])
#   # print(customer)
#   # print(customer['id'])

#   # # charge customer
#   # c = customer.charge(amount=999, currency="EUR")
#   # print(c)

#   # create subscription
#   subscription = stripe_customer.new_subscription("price_1RH2eaKpYockGiqNOasQNTNj")
#   print(subscription)
#   print(subscription[0])
  