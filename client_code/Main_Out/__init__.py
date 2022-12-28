from ._anvil_designer import Main_OutTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

class Main_Out(Main_OutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.label_2.text = anvil.users.get_user()
  
  def link_1_click(self, **event_args):
    anvil.users.login_with_form(allow_cancel=True)

  def button_1_click(self, **event_args):
    anvil.users.signup_with_form(allow_cancel=True)


