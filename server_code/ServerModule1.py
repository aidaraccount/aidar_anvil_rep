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
# Here is an example - you can replace it with your own:
#

@anvil.server.callable
def check_user_presence():
    user = anvil.users.get_user()
    if (user != None):
      new_user_id = anvil.server.call('CheckUserPresence', user)
      if (new_user_id != None):
        user_row = app_tables.users.get(email = user["email"])
        user_row['user_id'] = new_user_id
        print("user_id filled: " + str(user_row['user_id']))
