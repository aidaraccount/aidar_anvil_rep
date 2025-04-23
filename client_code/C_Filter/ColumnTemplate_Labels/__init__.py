from ._anvil_designer import ColumnTemplate_LabelsTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ColumnTemplate_Labels(ColumnTemplate_LabelsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    
  def button_remove_label_filter_click(self, **event_args):
    self.parent.items = [entry for entry in self.parent.items if entry['label_name'] != self.item['label_name']]
