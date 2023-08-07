from ._anvil_designer import Main_Out_v2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime

from ..Main_In import Main_In
from ..C_LandingPage import C_LandingPage
from ..C_LandingPage_v2 import C_LandingPage_v2
from ..C_Investigate import C_Investigate

class Main_Out_v2(Main_Out_v2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #self.content_panel.add_component(C_LandingPage_v2())
    
    # Any code you write here will run before the form opens.
    check_log_status(self)
    
  def link_login_click(self, **event_args):
    print(f'Login Click - Start {datetime.datetime.now()}', flush=True)
    anvil.users.login_with_form(allow_cancel=True, remember_by_default=True)
    check_log_status(self)
    user = anvil.users.get_user()
    if (user != None):
      anvil.server.call('check_user_presence')
      open_form('Main_In', user_id = user["user_id"])
      
  def link_logout_click(self, **event_args):
    anvil.users.logout()
    check_log_status(self)
    

def check_log_status(self, **event_args):
  print(f'Check log status - Start {datetime.datetime.now()}', flush=True)
  if (anvil.users.get_user() == None):
    self.link_login2.visible = True
    self.link_logout2.visible = False
  else:
    self.link_login2.visible = False
    self.link_logout2.visible = True

