from ._anvil_designer import MainOut_RegisterTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
import re
import json

from anvil_extras import routing
from anvil.js.window import location
from ..nav import click_link, click_button, logout, save_var, load_var
from ..C_ForgotPasswordPopup import C_ForgotPasswordPopup


@routing.route("register", title="Register")
class MainOut_Register(MainOut_RegisterTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # # check for key in url
    # print('add , url_keys=['license_key'] to @routing.route("register", title="Register")')
    # print('add routing.set_url_hash('register?license_key=None', load_from_cache=False) to MainOut - link_register_click')
    # print(anvil.js.window.location.hash.lstrip('#').split('?')[1][12:])
    # if anvil.js.window.location.hash.lstrip('#').split('?')[1][12:] != 'None':
    #   self.license_key.text = anvil.js.window.location.hash.lstrip('#').split('?')[1][12:]
    pass
    
  
  def button_register_click(self, **event_args):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    customer_id = anvil.server.call('check_customer_license_key', self.license_key.text)
    print('MainOut_Register customer_id:', customer_id)
    
    if customer_id is None:
      anvil.server.call('sent_push_over',  'User Registration Failed', f'Wrong Customer License Key: {self.login_email.text}')
      alert(
        title="Wrong Customer License Key!",
        content="Please check your Customer License Key - if the problem remains, get in touch with your admin.",
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )
    elif self.first_name.text == '':
      alert(
        title="Missing Data!",
        content="Please add your first name.",
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )    
    elif self.last_name.text == '':
      alert(
        title="Missing Data!",
        content="Please add your second name.",
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )
    elif re.match(email_regex, self.login_email.text) is None:
      alert(
        title="No valid mail!",
        content="Please enter a valid mail address.",
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )
    elif self.login_pw.text == '':
      alert(
        title="No valid password!",
        content="Please enter a valid password.",
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )      
    elif self.login_pw.text != self.login_pw_conf.text:
      alert(
        title="Passwords do not match!",
        content="Please ensure your password is correct in both fields.",
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )    
    else:
      # create user and sent mail confirmation mail
      # function is placed in the ServerModule
      res = anvil.server.call('sign_up_with_extra_data',
                              customer_id,
                              self.login_email.text,
                              self.login_pw.text,
                              self.first_name.text,
                              self.last_name.text)
      
      # alerts & redirect
      if res == 'success':
        anvil.server.call('sent_push_over',  'User Registration', f'{self.login_email.text} registered for Customer {customer_id}')
        alert(
          title="Registration successful!",
          content="Please confirm your email by clicking the link we just sent you.",
          buttons=[("Close", True)],
          role=["forgot-password-success", "remove-focus"],
        )
        anvil.js.window.location.href = "https://www.aidar.ai"        
      elif res == 'user exists':
        alert(
          title="Registration Failed!",
          content="This user already exists.",
          buttons=[("Go Back", True)],
          role=["forgot-password-success", "remove-focus"],
        )
      elif res == 'other':
        alert(
          title="Registration Failed!",
          content="Please check your credentials.",
          buttons=[("Go Back", True)],
          role=["forgot-password-success", "remove-focus"],
        )
          
  # POSITION JUMPS
  def first_name_pressed_enter(self, **event_args):
    self.last_name.focus()

  def last_name_pressed_enter(self, **event_args):
    self.login_email.focus()

  def login_email_pressed_enter(self, **event_args):
    self.login_pw.focus()

  def login_pw_pressed_enter(self, **event_args):
    self.login_pw_conf.focus()

  def login_pw_conf_pressed_enter(self, **event_args):
    self.license_key.focus()

  # LICENSE KEY
  def license_key_change(self, **event_args):
    # add - after 3 and 7 characters
    if len(self.license_key.text) in (3, 7):
      self.license_key.text = f'{self.license_key.text}-'

    # do not allow --
    if len(self.license_key.text) > 3:
      if self.license_key.text[len(self.license_key.text)-2:len(self.license_key.text)] == '--':
        self.license_key.text = self.license_key.text[:len(self.license_key.text)-1]
    
    # Limit to 11 characters
    self.license_key.text = self.license_key.text[:11]
