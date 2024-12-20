from ._anvil_designer import RepeatingPanel_ArtistsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RepeatingPanel_Artists(RepeatingPanel_ArtistsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.repeating_panel_tracks.items = self.item["tracks"]

    # set artist picture
    if self.item["artist_picture_url"] is not None:
      self.artist_img.source = self.item["artist_picture_url"]
    else:
      self.artist_img.source = '_/theme/pics/Favicon_orange.JPG'
