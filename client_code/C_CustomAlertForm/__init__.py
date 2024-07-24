from ._anvil_designer import C_CustomAlertFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class C_CustomAlertForm(C_CustomAlertFormTemplate):
  def __init__(self, text, pickurl, artist_name, countryflag, countryname, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.
    # Class for additional styling of the entire window
    self.role = 'custom-alert'
    
    # Artist Biography
    self.Artist_Bio.content = text 
    self.Artist_Bio.role = 'alert-long-text'

    # Artist Image
    self.Artist_Image.source = pickurl

    # Artist Name
    self.Artist_Name.text = artist_name
    self.Artist_Name.role ='artist-name-tile'

    # Artist Country
    if countryflag is None:
      pass
    else:
      self.Artist_Name_Details.add_component(countryflag)
      countryflag.tooltip = countryname
      countryflag.role = 'country-flag-icon'
      self.Artist_Name_Details.role = 'artist-name-details-popup'

    
    

