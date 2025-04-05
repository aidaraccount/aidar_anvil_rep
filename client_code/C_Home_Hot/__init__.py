from ._anvil_designer import C_Home_HotTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import anvil.js
from anvil import get_open_form
from ..nav import click_button, save_var
import time
from anvil.js.window import location


class C_Home_Hot(C_Home_HotTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    # 1. Register JavaScript callbacks for direct call (not promises)
    anvil.js.call_js(
      "eval",
      """
      
      """,
    )

    # Register the Python functions
    # ...
    
    # 2. Create NextUp table
    self.create_nextup_table()

  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass

  def create_hot_tables(self):
    """
    Creates the Hot tables with artist data
    """
    