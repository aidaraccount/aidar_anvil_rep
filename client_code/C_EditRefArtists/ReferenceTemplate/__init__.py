from ._anvil_designer import ReferenceTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ReferenceTemplate(ReferenceTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    if self.label_name_3.text == None:
      self.button_3.visible = False
      self.image_3.visible = False
      self.label_name_3.visible = False
    
    if self.label_name_2.text == None:
      self.button_2.visible = False
      self.image_2.visible = False
      self.label_name_2.visible = False