import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import asyncio
import numpy as np



# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.

@anvil.server.callable
def sign_up_with_extra_data(customer_id, email, password, first_name, last_name):
  try:
    # Sign up the user
    user = anvil.users.signup_with_email(email, password)
    
    # Add extra data
    user['customer_id'] = customer_id
    user['first_name'] = first_name
    user['last_name'] = last_name

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

# # Take 1
# @anvil.server.callable
# def launch_anvil_get_observed():
#   task = anvil.server.launch_background_task('anvil_get_observed')
#   return task
  
# @anvil.server.background_task
# def anvil_get_observed():
#   import time
#   time.sleep(10)
#   print('waited enough!')

# # Take 2
# @anvil.server.callable
# def anvil_get_observed():
#     return asyncio.run(async_anvil_get_observed())

# async def async_anvil_get_observed():
#     print('Hello ...')
#     # asyncio.sleep(10)
#     asyncio.run('test_pause')
#     print('... World!')
#     return 42

# def test_pause():
#   import time
#   time.sleep(10)
#   print('... yes?!')

@anvil.server.callable
def update():
  """
  Simulates a long-running server function.
  This function updates a database (or does something else) and returns a result.
  """
  import time
  time.sleep(7)  # Simulate a delay (e.g., database update)
  return "Database Updated!"
  