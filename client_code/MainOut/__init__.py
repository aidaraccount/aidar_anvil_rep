from ._anvil_designer import MainOutTemplate
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

from ..C_Login import C_Login


# @routing.route('login', title='Login')
@routing.main_router
class MainOut(MainOutTemplate):
  def __init__(self, **properties):
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    global user
    user = None
    
    # Any code you write here will run before the form opens.
    open_form('C_Login')
    # self.content_panel.add_component(C_Login())
    