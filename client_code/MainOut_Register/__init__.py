from ._anvil_designer import MainOut_RegisterTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime
import re
import json

from anvil_extras import routing
from anvil.js.window import location
from ..nav import click_link, click_button, logout, save_var, load_var
from ..C_ForgotPasswordPopup import C_ForgotPasswordPopup


@routing.route("register", url_keys=['license_key'], title="Register")
class MainOut_Register(MainOut_RegisterTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.    
    # check for key in url
    if anvil.js.window.location.hash.lstrip('#').split('?')[1][12:] != 'None':
      # save license_key for later usage
      self.license_key = anvil.js.window.location.hash.lstrip('#').split('?')[1][12:]
      
      # add the subscribing company name to the header      
      self.customer = json.loads(anvil.server.call('check_customer_license_key', self.license_key))
      print(self.customer[0])
      if self.customer is not None:
        self.customer_id = self.customer[0]['customer_id']
        self.customer_name = self.customer[0]['name']
        self.company_pre_label.visible = True
        self.company_label.visible = True
        self.login_company.visible = False
        self.company_label.text = f"{self.customer_name}"
      else:
        self.customer_id = None
        self.customer_name = None
    
    else:
      self.customer_id = None
      self.customer_name = None
      self.company_pre_label.visible = False
      self.company_label.visible = False
    
    # add link to Privacy Policy
    self.label_privacy.content = 'I have read and agree to the <a href="https://www.aidar.ai/terms.html" target="_blank">Terms of Service</a> and <a href="https://www.aidar.ai/privacy.html" target="_blank">Privacy Policy</a>.'
    
  
  def button_register_click(self, **event_args):
    if self.confirm_privacy.checked is True:
      email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
      if self.customer_id is None:
        self.customer_name = self.login_company.text
      
      if self.first_name.text == '':
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
                                self.customer_id,
                                self.customer_name,
                                self.login_email.text,
                                self.login_pw.text,
                                self.first_name.text,
                                self.last_name.text)
        
        # alerts & redirect
        if res == 'success':
          anvil.server.call('sent_push_over',  'User Registration', f'{self.login_email.text} registered for Customer {self.customer_name}')
          alert(
            title="Registration successful!",
            content="Please confirm your email by clicking the link we just sent you.",
            buttons=[("Close", True)],
            role=["forgot-password-success", "remove-focus"],
          )
          anvil.js.window.location.replace("https://www.aidar.ai")        
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
    else:
      Notification("", title="Privacy Policy has to be read and confirmed!", style="warning").show()
  
          
  # POSITION JUMPS
  def first_name_pressed_enter(self, **event_args):
    self.last_name.focus()

  def last_name_pressed_enter(self, **event_args):
    self.login_email.focus()

  def login_email_pressed_enter(self, **event_args):
    self.login_company.focus()

  def login_company_pressed_enter(self, **event_args):
    self.login_pw.focus()
  
  def login_pw_pressed_enter(self, **event_args):
    self.login_pw_conf.focus()

  def login_pw_conf_pressed_enter(self, **event_args):
    self.confirm_privacy.focus()

  def confirm_privacy_change(self, **event_args):
    if self.confirm_privacy.checked is True:
      self.register_button.role = 'call-to-action-button'
    else:
      self.register_button.role = 'call-to-action-button-disabled'

  def link_login_click(self, **event_args):
    routing.set_url_hash('login', load_from_cache=False)
    open_form('MainOut')
