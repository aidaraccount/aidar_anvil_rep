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
    """Triggered when the user clicks the login button"""
    # Get values from the form
    email = self.login_email.text
    password = self.login_pw.text
    remember_me = self.remember_me_checkbox.checked

    try:
      # Log in user with the "Remember me" option
      user = anvil.users.login_with_email(email, password, remember=remember_me)

      # user = anvil.users.get_user()

      save_var("user", user)
      if user is not None:
        anvil.server.call("server_transfer_user_id")

        # Save user_id and model_id to session storage
        if user["user_id"] is not None:
          save_var("user_id", user["user_id"])
          save_var("model_id", anvil.server.call("get_model_id", user["user_id"]))

        # Navigate to main page after successful login
        open_form("MainIn")

        if location.hash == "":
          routing.set_url_hash("home", load_from_cache=False)
        elif location.hash[:8] == "#artists":
          routing.set_url_hash(location.hash, load_from_cache=False)

    except anvil.users.AuthenticationFailed:
      alert(
        "Please check your credentials.",
        title="Login Failed.",
        large=False,
        buttons=[("Go Back", True)],
        role=["forgot-password-success", "remove-focus"],
      )

  def login_email_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    self.login_pw.focus()

  def link_register_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass
