from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random
import string
from anvil.js.window import navigator

from anvil_extras import routing
from ..nav import click_link, click_button, save_var

from ..C_ForgotPasswordPopup import C_ForgotPasswordPopup


@routing.route("settings", title="Settings")
class Settings(SettingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    self.nav_account_click()
    self.key.text = '111-222-333'
    self.link.text = 'app.aidar.ai/register/626-623-752'
    

  # -----------------------
  # NAVIGATION
  def nav_account_click(self, **event_args):
    self.nav_account.role = 'section_buttons_focused'
    self.nav_user.role = 'section_buttons'
    self.sec_account.visible = True
    self.sec_user.visible = False

  def nav_user_click(self, **event_args):
    self.nav_account.role = 'section_buttons'
    self.nav_user.role = 'section_buttons_focused'
    self.sec_account.visible = False
    self.sec_user.visible = True

  
  # -----------------------
  # 1. ACCOUNT SETTINGS
  # a) Profile Management

  # b) Subscription Status

  # c) Password
  def reset_pw_click(self, **event_args):   
    res = alert(title='Do you want to reset your password?',
      content="Are you sure to reset your password?",
      buttons=[
        ("Cancel", "NO"),
        ("Yes, reset password", "YES")
      ],
      role=["forgot-password-success","remove-focus"]
    )
    if res == 'YES':
      anvil.users.send_password_reset_email('janek-meyn@web.de')  # ATTENTION !!!
      alert(
        "A recovery email has been sent to your email address",
        title="Success",
        large=False,
        buttons=[("OK", True)],
        role=["forgot-password-success","remove-focus"]
      )

  
  # -----------------------
  # 2. USER MANAGEMENT
  # a) User Roles & Permissions

  # b) User Invite  
  def copy_click(self, **event_args):
    navigator.clipboard.writeText(f'https://{self.link.text}')
    Notification("", title="Link copied!", style="success").show()


