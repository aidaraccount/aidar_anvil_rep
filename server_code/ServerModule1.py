import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.

@anvil.server.callable
def server_transfer_user_id():
  user = anvil.users.get_user()
  if user["user_id"] is None:
    new_user_id = anvil.server.call('check_user_presence', user["email"])
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
def check_user_exists(email):
  # Check if a user exists in the Users table by email
  user = app_tables.users.get(email=email)
  
  # Return True if user exists, otherwise return False
  return user is not None

@anvil.server.callable
def shorten_number(num):
  thresholds = [
      (1_000_000_000_000, 'T'),  # Trillion
      (1_000_000_000, 'B'),      # Billion
      (1_000_000, 'M'),          # Million
      (1_000, 'K')               # Thousand
  ]
  
  def shorten_single_number(n):
      if n is None or not isinstance(n, (int, float)):
          return '-'
      for threshold, suffix in thresholds:
          if n >= threshold:
              return f'{n / threshold:.1f}{suffix}'
      return f'{n:.0f}'
  
  # If input is a list, process each number
  if isinstance(num, list):
      return [shorten_single_number(n) for n in num]
  # If input is a single number, just process it
  else:
      return shorten_single_number(num)
