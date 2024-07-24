import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server
from anvil import open_form
from anvil_extras import routing
import anvil.js


def click_link(element, target, event_args):
  if event_args['keys']['ctrl'] is True:
    element.url = f"{anvil.server.get_app_origin()}/#{target}"
  else:
    element.url = ''
    routing.set_url_hash(target)

def click_button(target, event_args):
  if event_args['keys']['ctrl'] is True:
    anvil.js.window.open(f"{anvil.server.get_app_origin()}/#{target}", '_blank')
  else:
    routing.set_url_hash(target)

def logout():
  anvil.users.logout()
  open_form('Main_Out')

def login_check():
  user = anvil.users.get_user()  
  if user:
    status = True
  else:
    status = False
    open_form('Main_Out')
  return status

def save_var(var, value):
  anvil.js.window.sessionStorage.setItem(var, value)

def load_var(var):
  val = anvil.js.window.sessionStorage.getItem(var)
  if val == 'null':
    val = None
  return val
