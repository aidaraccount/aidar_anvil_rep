from ._anvil_designer import RepeatingPanel_TracksTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RepeatingPanel_Tracks(RepeatingPanel_TracksTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    # set album picture    
    if self.item["album_picture_url"] is not None:
      self.album_img.source = self.item["album_picture_url"]
    else:
      self.album_img.source = '_/theme/pics/Favicon_orange.JPG'