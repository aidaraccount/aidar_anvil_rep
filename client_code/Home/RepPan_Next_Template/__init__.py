from ._anvil_designer import RepPan_Next_TemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RepPan_Next_Template(RepPan_Next_TemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.radio_button.selected = True
    self.radio_button.group_name
    
    self.artist_pic.source = self.item['artist_picture_url']
    self.artist_pic.height = 40

    self.link_artist.text = self.item['name']
    self.link_artist.role = ['header-7', 'txt_orange']

    self.label_status.text = self.item['status']
    self.label_status.role = ['header-7']
    
    self.label_priority.text = self.item['priority']
    self.label_priority.role = ['header-7']

    self.button_wl.text = None
    self.button_wl.icon = 'fa:address-card-o'
    
    