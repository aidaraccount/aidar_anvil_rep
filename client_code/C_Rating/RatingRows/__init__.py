from ._anvil_designer import RatingRowsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

#from ..C_Investigate import C_Investigate

class RatingRows(RatingRowsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def check_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.check_link.url = 'www.google.com'
    self.content_panel.clear()
    self.content_panel.add_component(C_Investigate())

