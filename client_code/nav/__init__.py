import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server
from anvil import open_form
from anvil_extras import routing
import anvil.js
from anvil.js.window import location
from anvil import get_open_form


def click_link(element, target, event_args):
  routing.clear_cache()
  if event_args['keys']['ctrl'] is True:
    element.url = f"{anvil.server.get_app_origin()}/#{target}"
  else:
    routing.set_url_hash(target, load_from_cache=False)

  get_open_form().reset_nav_backgrounds()
  

def click_button(target, event_args):
  routing.clear_cache()
  if event_args != {}:
    if event_args['keys']['ctrl'] is True:
      anvil.js.window.open(f"{anvil.server.get_app_origin()}/#{target}", '_blank')
    else:
      routing.set_url_hash(target, load_from_cache=False)
  else:
    routing.set_url_hash(target, load_from_cache=False)
  
  get_open_form().reset_nav_backgrounds()


def click_box(target):
  routing.clear_cache()
  routing.set_url_hash(target, load_from_cache=False)
  get_open_form().reset_nav_backgrounds()


def logout():
  anvil.users.logout()
  # anvil.js.window.sessionStorage.clear()
  anvil.js.window.sessionStorage.removeItem("model_id")
  # open_form('Main_Out')
  open_form('Main_Out_New')
  routing.set_url_hash('', load_from_cache=False)


def login_check():
  user = anvil.users.get_user()  
  if user:
    status = True
  else:
    status = False
    # open_form('Main_Out')
    open_form('Main_Out_New')
  return status


def save_var(var, value):
  anvil.js.window.sessionStorage.setItem(var, value)
  return value


def load_var(var):
  value = anvil.js.window.sessionStorage.getItem(var)
  if value == 'null':
    value = None
  return value


def refresh():
  #location.reload()
  current_hash = location.hash
  temporary_hash = ''
  location.hash = temporary_hash
  location.hash = current_hash
