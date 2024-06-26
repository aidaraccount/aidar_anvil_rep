from ._anvil_designer import CustomAlertFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class CustomAlertForm(CustomAlertFormTemplate):
  def __init__(self, text, pickurl, artist_name, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.
    # Class for additional styling of the entire window
    self.role = 'custom-alert'
    
    # Artist Biography
    self.rich_text_1.content = text # Assuming you have a Label component named label_1
    self.rich_text_1.role = 'alert-long-text'

    # Artist Image
    self.image_1.source = pickurl

    # Artist Name
    self.label_1.text = artist_name
    self.label_1.role ='artist-name-tile'
    

