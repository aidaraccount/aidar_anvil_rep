from ._anvil_designer import MainOut_RegisterTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
import re

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
    pass

  
  def button_register_click(self, **event_args):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if self.first_name.text == '':
      alert(
        "Please add your first name.",
        title="Missing Data!",
        large=False,
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )
    
    elif self.last_name.text == '':
      alert(
        "Please add your second name.",
        title="Missing Data!",
        large=False,
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )

    elif re.match(email_regex, self.login_email.text) is None:
      alert(
        "Please enter a valid mail address.",
        title="No valid mail!",
        large=False,
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )        
    
    elif self.login_pw.text == '':
      alert(
        "Please enter a valid password.",
        title="No valid password!",
        large=False,
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )
      
    elif self.login_pw.text != self.login_pw_conf.text:
      alert(
        "Please ensure your password is correct in both fields.",
        title="Passwords do not match!",
        large=False,
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )

      # LICENSE KEY
    
    else:
      # create user and sent mail confirmation mail
      res = anvil.server.call('sign_up_with_extra_data',
                        self.login_email.text,
                        self.login_pw.text,
                        self.first_name.text,
                        self.last_name.text)

      # alerts & redirect
      if res == 'success':
        alert(
          "Please confirm your email by clicking the link we just sent you.",
          title="Registration successful!",
          large=False,
          buttons=[("Go Back", True)],
          role=["forgot-password-success", "remove-focus"],
        )
        anvil.js.window.location.href = "https://www.aidar.ai"
        
      elif res == 'user exists':
        alert(
          "This user already exists.",
          title="Registration Failed!",
          large=False,
          buttons=[("Go Back", True)],
          role=["forgot-password-success", "remove-focus"],
        )
      elif res == 'other':
        alert(
          "Please check your credentials.",
          title="Registration Failed!",
          large=False,
          buttons=[("Go Back", True)],
          role=["forgot-password-success", "remove-focus"],
        )
  
  def login_email_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    # self.login_pw.focus()
    pass

  def link_get_access_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

