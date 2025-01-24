from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random
import string

from anvil_extras import routing
from ..nav import click_link, click_button, save_var


@routing.route("settings", title="Settings")
class Settings(SettingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    self.nav_account_click()
    
  
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
