import anvil.stripe
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import numpy as np
import datetime


# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.

@anvil.server.callable
def sign_up_with_extra_data(customer_id, customer_name, email, password, first_name, last_name):
  try:
    # Sign up the user
    user = anvil.users.signup_with_email(email, password)
    
    # Add extra data
    user['first_name'] = first_name
    user['last_name'] = last_name
    user['customer_name'] = customer_name

    if customer_id is not None:
      user['customer_id'] = customer_id
    else:
      user['expiration_date'] = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=14)).date()
    
    return 'success'
    
  except anvil.users.UserExists:
    return 'user exists'

  except Exception:
    return 'other'


@anvil.server.callable
def check_user_exists(email):
  # Check if a user exists in the Users table by email
  user = app_tables.users.get(email=email)
  
  # Return True if user exists, otherwise return False
  return user is not None


@anvil.server.callable
def server_transfer_user_id():
  user = anvil.users.get_user()
  if user["user_id"] is None:
    new_user_id = anvil.server.call('check_user_presence', user["customer_id"], user["email"], user["first_name"], user["last_name"])
    if new_user_id is not None:
      user_row = app_tables.users.get(email = user["email"])
      user_row['user_id'] = new_user_id


@anvil.server.callable
def update_slider_start(value):
  print(f"Slider start value: {value}")
  # You can update the graph, filter data, etc., based on this value


@anvil.server.callable
def update_slider_end(value):
  print(f"Slider end value: {value}")
  # Update your logic based on this value


@anvil.server.callable
def update_anvil_user(user_id, first_name, last_name):
  """
  Updates a user's first_name and last_name in the Anvil Users table.
  
  Args:
      user_id: The user ID to update
      first_name: The new first name
      last_name: The new last name
      
  Returns:
      'success' if the update was successful, 'error' otherwise
  """
  try:
    # Get the user row from the Users table
    user_row = app_tables.users.get(user_id=user_id)
    
    if user_row:
      # Update the user's information
      user_row['first_name'] = first_name
      user_row['last_name'] = last_name
      return 'success'
    else:
      return 'error'
  except Exception as e:
    print(f"Error updating Anvil user: {e}")
    return 'error'


@anvil.server.callable
def create_setup_intent():
  import stripe
  import anvil.secrets
  
  stripe.api_key = anvil.secrets.get_secret("STRIPE_API_KEY")
  intent = stripe.SetupIntent.create(
      usage="off_session"
  )
  
  return intent.client_secret


# @anvil.server.callable
# def create_stripe_customer(token, email):
#   # create stripe customer
#   stripe_customer = anvil.stripe.new_customer(email, token)
#   print(stripe_customer)
#   print(stripe_customer['id'])
  
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
  