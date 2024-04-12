from ._anvil_designer import C_DiscoverTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server
import json
from datetime import datetime
import plotly.graph_objects as go

class C_Discover(C_DiscoverTemplate):
  def __init__(self, temp_artist_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.spacer_bottom_margin.height = 50
    
    # Section 2: Spotify Web-Player
    spotify_artist_id = '5tHOqv4SnPS6Dv4rZuUOxP'
    self.c_web_player.html = '<iframe style="border-radius:12px" src="https://open.spotify.com/embed/artist/' + spotify_artist_id + '?utm_source=generator&theme=0&autoplay=true" width="100%" height="80" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
    