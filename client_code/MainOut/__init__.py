from ._anvil_designer import MainOutTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime
import re

from anvil_extras import routing
from anvil.js.window import location
from ..nav import click_link, click_button, logout, save_var, load_var
from ..C_ForgotPasswordPopup import C_ForgotPasswordPopup


@routing.route('login', title='Login')
class MainOut(MainOutTemplate):
  def __init__(self, **properties):
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    global user
    user = None
        
    # Any code you write here will run before the form opens.
    # check for register page url
    url_hash = anvil.js.window.location.hash.lstrip('#')
    if url_hash.split('?')[0] == 'register':
      if '?' in url_hash and url_hash.split('?')[1].startswith('license_key='):
        license_key_part = url_hash.split('?')[1]
        if len(license_key_part) > 12:
          license_key = license_key_part[12:]
          self.link_register_click(license_key)
        else:
          self.link_register_click('None')
      else:
        self.link_register_click('None')
    

  def button_login_click(self, **event_args):
    try:
      # Log in user with the "Remember me" option
      user = anvil.users.login_with_email(self.login_email.text,
                                          self.login_pw.text,
                                          remember=self.remember_me_checkbox.checked)

      if user is not None:
        # Get user's timezone from browser
        timezone = anvil.js.call_js('() => Intl.DateTimeFormat().resolvedOptions().timeZone')

        # copies the user to postgres db (via ServerModule) with timezone
        anvil.server.call("server_transfer_user_id", timezone)
        
        # Save user_id and model_id to session storage
        if user["user_id"] is not None:
          save_var("user_id", user["user_id"])
          save_var("model_id", anvil.server.call('get_model_id',  user["user_id"]))

        # Navigate to main page after successful login
        anvil.server.call('login_updates',  user["user_id"])
        open_form("MainIn")
      
        if location.hash == '':
          routing.set_url_hash('home', load_from_cache=False)
        elif location.hash[:8] == '#artists':
          routing.set_url_hash(location.hash, load_from_cache=False)

      else:        
        alert(
          "Please check your credentials or contact our support at info@aidar.ai.",
          title="Login Failed.",
          large=False,
          buttons=[("Go Back", True)],
          role=["forgot-password-success", "remove-focus"]
        )
        
    except anvil.users.AuthenticationFailed:
      alert(
        "Please check your credentials.",
        title="Login Failed.",
        large=False,
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"]
      )

  def link_forgot_password_click(self, **event_args):
    alert(
      content=C_ForgotPasswordPopup(),
      buttons=[]
    )

  def login_email_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    self.login_pw.focus()

  def link_register_click(self, license_key='None', **event_args):
    # routing.set_url_hash('register', load_from_cache=False)
    routing.set_url_hash(f'register?license_key={license_key}', load_from_cache=False)
    open_form('MainOut_Register')