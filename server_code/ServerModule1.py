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
  print(f'server_transfer_user_id: ..')
  user = anvil.users.get_user()
  print(f'UserID = {user["user_id"]}')
  if (user["user_id"] == None):
    print(f'CheckUserPresence (from DB): -> new_user_id')
    new_user_id = anvil.server.call('check_user_presence', user["email"])
    print(f'NewUserID = {new_user_id}')
    if (new_user_id != None):
      user_row = app_tables.users.get(email = user["email"])
      user_row['user_id'] = new_user_id
