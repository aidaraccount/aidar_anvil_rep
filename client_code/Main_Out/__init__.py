from ._anvil_designer import Main_OutTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
import re

from anvil_extras import routing
from ..nav import click_link, click_button, logout, save_var, load_var


@routing.route('login', title='Login')
class Main_Out(Main_OutTemplate):
  def __init__(self, **properties):    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    model_id = load_var("model_id")
    print(f"Main_Out model_id: {model_id}")
    
    # Any code you write here will run before the form opens.
    check_log_status(self)

  
  def link_login_click(self, **event_args):
    anvil.users.login_with_form(allow_cancel=True, remember_by_default=True)
    #print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 1", flush=True)
    check_log_status(self)
    #print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 2", flush=True)
    user = anvil.users.get_user()
    #print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 3", flush=True)
    if user is not None:
      try:
        anvil.server.call("server_transfer_user_id")
        #print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 4", flush=True)
        user = anvil.users.get_user()
        #print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 5", flush=True)
        open_form("Main_In")
        routing.set_url_hash('home', load_from_cache=False)
        #print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 6", flush=True)
      except:
        alert(
          title="Unveiling New Features!",
          content="Apologies for any inconvenience caused.\n\nWe are presently integrating new features and will have the site accessible again shortly.\n\nFeel free to contact us via email at info@aidar.ai.\n\nThank you,\nYour AIDAR Team",
        )

  def button_login_click(self, **event_args):
    try:
      user = anvil.users.login_with_email(self.login_email.text,self.login_pw.text)
      check_log_status(self)
      user = anvil.users.get_user()
      if user is not None:
        try:
          anvil.server.call("server_transfer_user_id")
          user = anvil.users.get_user()
          open_form("Main_In")
          routing.set_url_hash('home', load_from_cache=False)
        except:
          alert(
            title="Unveiling New Features!",
            content="Apologies for any inconvenience caused.\n\nWe are presently integrating new features and will have the site accessible again shortly.\n\nFeel free to contact us via email at info@aidar.ai.\n\nThank you,\nYour AIDAR Team",
          )
    except:
      print("ERROR!!")
      Notification("",
        title="Authentification failed!",
        style="danger").show()
  
  def link_logout_click(self, **event_args):
    anvil.users.logout()
    anvil.js.window.sessionStorage.clear()
    check_log_status(self)

  def button_signup_click(self, **event_args):
    anvil.users.signup_with_form(allow_cancel=True)

  def link_home_click(self, **event_args):
    user = anvil.users.get_user()
    if user is not None:
      anvil.server.call("check_user_presence", mail=user["email"])
      open_form("Main_In")

def check_log_status(self, **event_args):
  if anvil.users.get_user() is None:    
    self.link_login.visible = True
    # self.link_register.visible = True
    self.link_logout.visible = False
    self.link_home.visible = False
    
  else:
    self.link_login.visible = False
    # self.link_register.visible = False
    self.link_logout.visible = True
    self.link_home.visible = True
    
  if self.updates_sign.visible is True:
    self.link_login.visible = False
    self.link_register.visible = False
    self.link_logout.visible = False
    self.link_home.visible = False
