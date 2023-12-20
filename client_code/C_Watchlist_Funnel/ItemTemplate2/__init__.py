from ._anvil_designer import ItemTemplate2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ItemTemplate2(ItemTemplate2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.link_1.add_component(Image(
                                source=self.item["ArtistPictureURL"],
                                height=175,
                                #width=100,
                                display_mode='zoom_to_fill'
    ))
    #self.link_1.add_component(XYPanel(height=175)) #.add_component(Label(text='Test Test'))
    
    