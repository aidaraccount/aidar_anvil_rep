from ._anvil_designer import CustomAlertFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class CustomAlertForm(CustomAlertFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.label_1.text = text  # Assuming you have a Label component named label_1
    # Optionally apply a custom class for additional styling
    self.role = 'custom-alert'
