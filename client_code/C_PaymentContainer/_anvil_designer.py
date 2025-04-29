import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js

class C_PaymentContainerTemplate(anvil.Component):
  """
  A template for a custom Component that manages the payment and subscription flow
  """
  def __init__(self, **properties):
    # Initialize self
    # Set Form properties and Data Bindings
    self.init_components(**properties)
    
  def init_components(self, **properties):
    # Set properties
    for prop_name, prop_value in properties.items():
      setattr(self, prop_name, prop_value)
