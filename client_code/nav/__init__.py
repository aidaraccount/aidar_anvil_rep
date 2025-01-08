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
import time


def click_link(element, target, event_args):
  routing.clear_cache()
  if event_args['keys']['ctrl'] is True:
    # 1. change element.url as fast as possible/ before the browser is running the click
    element.url = f"{anvil.server.get_app_origin()}/#{target}"
    
    # 2. wait till browser did the action and reset element.url to avoid new tabs being opened every time onwards
    time.sleep(0.3)
    element.url = ""
    
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
  open_form('MainOut')
  routing.set_url_hash('', load_from_cache=False)


def login_check():
  user = anvil.users.get_user()  
  if user:
    status = True
  else:
    status = False
    open_form('MainOut')
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
