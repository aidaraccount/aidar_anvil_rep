from ._anvil_designer import RelArtistRowTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RelArtistRowTemplate(RelArtistRowTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def related_artist_pic_link_click(self, **event_args):
    open_form('Main_In', temp_artist_id = int(self.related_artist_pic_link.url), value=None)

  def related_artist_name_link_click(self, **event_args):
    open_form('Main_In', temp_artist_id = int(self.related_artist_name_link.url), value=None)