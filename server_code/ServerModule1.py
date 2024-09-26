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