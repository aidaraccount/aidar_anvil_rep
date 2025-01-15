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
    """Triggered when the user clicks the register button"""
    try:
      # Log in user with the "Remember me" option
      sign_up = anvil.users.signup_with_email(self.login_email.text,
                                              self.login_pw.text)
      print(sign_up)

    except anvil.users.AuthenticationFailed:
      alert(
        "Please check your credentials.",
        title="Registration Failed.",
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

