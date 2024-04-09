from ._anvil_designer import C_DiscoverTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class C_Discover(C_DiscoverTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    self.feature_1.value.text = 'Value 1'
    self.feature_1.header.text = 'Header 1'
    self.feature_1.width = 200

    self.feature_2.value.text = 'Value 2'
    self.feature_2.header.text = 'Header 2'
    self.feature_2.width = 400
    
    self.feature_3.value.text = 'Value 3'
    self.feature_3.header.text = 'Header 3'
    self.feature_3.width = 400
    self.feature_3.visible = False
    
    self.feature_4.value.text = 'Value 4'
    self.feature_4.header.text = 'Header 4'
    self.feature_4.width = 400
    
    self.feature_double_1.value.text = 'Value Double 4'
    self.feature_double_1.header.text = 'Header Double 4'
    self.feature_double_1.width = 200

    # Section 2: Spotify Web-Player
    spotify_artist_id = '4WqdAyk9kdsB6B5JVdhRIB'
    self.c_web_player.html = '<iframe style="border-radius:12px" src="https://open.spotify.com/embed/artist/' + spotify_artist_id + '?utm_source=generator&theme=0" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
    
    
    