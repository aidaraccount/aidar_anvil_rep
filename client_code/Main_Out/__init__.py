from ._anvil_designer import Main_OutTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

from ..Main_In import Main_In
from ..C_LandingPage import C_LandingPage
from ..C_Investigate import C_Investigate


class Main_Out(Main_OutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.content_panel.add_component(C_LandingPage())
    
    # Any code you write here will run before the form opens.
    check_log_status(self)
    
  def link_login_click(self, **event_args):
    anvil.users.login_with_form(allow_cancel=True, remember_by_default=True)
    check_log_status(self)
    user = anvil.users.get_user()
    if (user != None):
      check_user_presence(self)
      open_form('Main_In', user_id = user["user_id"])
      
  def link_logout_click(self, **event_args):
    anvil.users.logout()
    check_log_status(self)
    

def check_log_status(self, **event_args):
  if (anvil.users.get_user() == None):
    self.link_login.visible = True
    self.link_logout.visible = False
  else:
    self.link_login.visible = False
    self.link_logout.visible = True

def check_user_presence(self, **event_args):
    user = anvil.users.get_user()
    if (user != None):
      new_user_id = anvil.server.call('CheckUserPresence', user)
      alert(new_user_id)
      if (new_user_id != None):
        alert(new_user_id)