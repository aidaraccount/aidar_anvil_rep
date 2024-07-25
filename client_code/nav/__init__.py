import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server
from anvil import open_form
from anvil_extras import routing
import anvil.js
from anvil.js.window import location


def click_link(self, element, target, event_args, reload):
  if event_args['keys']['ctrl'] is True:
    element.url = f"{anvil.server.get_app_origin()}/#{target}"
  else:
    if reload:
      self.content_panel.clear()
    element.url = ''
    routing.set_url_hash(target)

def click_button(self, target, event_args, reload):
  if event_args['keys']['ctrl'] is True:
    anvil.js.window.open(f"{anvil.server.get_app_origin()}/#{target}", '_blank')
  else:
    if reload:
      self.content_panel.clear()
    routing.set_url_hash(target)

def click_box(self, target, reload):
  if reload:
    self.content_panel.clear()
  routing.set_url_hash(target)

def logout():
  anvil.users.logout()
  anvil.js.window.sessionStorage.clear()
  anvil.js.window.sessionStorage.removeItem("model_id")
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
  return value

def load_var(var):
  value = anvil.js.window.sessionStorage.getItem(var)
  if value == 'null':
    value = None
  return value

def refresh():
  #location.reload()
  current_hash = location.hash
  print(current_hash)
  temporary_hash = ''
  location.hash = temporary_hash
  location.hash = current_hash
