from ._anvil_designer import Main_OutTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
from ..Main_In import Main_In
from ..C_Investigate import C_Investigate

class Main_Out(Main_OutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.
    check_log_status(self)
    
  def link_login_click(self, **event_args):
    print(f'Login Click - Start {datetime.datetime.now()}', flush=True)
    anvil.users.login_with_form(allow_cancel=True, remember_by_default=True)
    check_log_status(self)
    user = anvil.users.get_user()
    if (user != None):      
      anvil.server.call('check_user_presence', mail=user['email'])
      open_form('Main_In', temp_artist_id = None, user_id = user["user_id"])
      
  def link_logout_click(self, **event_args):
    anvil.users.logout()
    check_log_status(self)
  
  def button_signup_click(self, **event_args):
    anvil.users.signup_with_form(allow_cancel=True)

  def link_investigate_click(self, **event_args):
    user = anvil.users.get_user()
    if (user != None):
      anvil.server.call('check_user_presence', mail=user['email'])
      open_form('Main_In', temp_artist_id = None, user_id = user["user_id"])

  def linkedin_click(self, **event_args):
    self.linkedin_link.url = 'https://www.linkedin.com/company/aidar-insights/'

  def instagram_click(self, **event_args):
    self.instagram_link.url = 'https://www.instagram.com/aidar_insights/'

  def call2action_text_box_click(self, **event_args):
    status = anvil.server.call('add_waiter', mail=self.call2action_text_box.text)
    if status == 'Success!':
      alert(title='Thanks for joining our Waiting List!',
            content='We appreciate your interest in our product and will get back to you as soon as we have the capacity available.\n\nBest regards\nYour AIDAR Team')
    elif status == 'Error':
      alert(title='Error..', content='Apologies for the inconvenience caused.\n\nIf the error persists, kindly reach out to us via email at info@aidar.ai.\n\nThank you,\nYour AIDAR Team')


def check_log_status(self, **event_args):
  print(f'Check log status - Start {datetime.datetime.now()}', flush=True)
  if (anvil.users.get_user() == None):
    self.link_login.visible = True
    #self.link_register.visible = True
    self.link_logout.visible = False
    self.link_investigate.visible = False
  else:
    self.link_login.visible = False
    #self.link_register.visible = False
    self.link_logout.visible = True
    self.link_investigate.visible = True
  
