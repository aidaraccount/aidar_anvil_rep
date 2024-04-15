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
  def __init__(self, temp_artist_id = 2, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    sug = {"Status": "Success!", "ModelID": "2", "ArtistID": "560919", "SpotifyArtistID": "6heMlLFM6RDDHRz99uKMqS", "Name": "RetroVision", "ArtistURL": "https://open.spotify.com/artist/6heMlLFM6RDDHRz99uKMqS", "ArtistPictureURL": "https://i.scdn.co/image/ab6761610000e5eb1428ee0feb9dae32ac83669e", "NoTracks": "113", "ArtistPopularity_lat": "46", "ArtistFollower_lat": "93339", "FirstReleaseDate": "2014-11-18", "LastReleaseDate": "2024-03-08", "MajorCoop": "1", "SubMajorCoop": "1", "LatestLabel": "Warner Music Central Europe", "AvgExplicit": "0.0354", "MinMusDist": "0.8885102232353875", "AvgMusDist": "0.9062671665657496", "MaxMusDist": "0.9240241098961117", "AvgDuration": "187.52287610619476", "AvgDanceability": "0.678221238938053", "AvgEnergy": "0.857221238938053", "AvgKey": "4.8938", "AvgLoudness": "-4.713938053097346", "AvgMode": "0.4867", "AvgSpeechiness": "0.09923097345132743", "AvgAcousticness": "0.0627684778761062", "AvgInstrumentalness": "0.2995615364601769", "AvgLiveness": "0.3070929203539824", "AvgValence": "0.457787610619469", "AvgTempo": "126.82925663716814", "Genres": "pop, house, edm, electro", "Countries": "Sweden", "RelArtists": "6", "Prediction": "93"}
    biography = 'DNA are a producer duo from Johannesburg, South Africa - comprising of Devon Horowitz and Alon Alkalay. \n\nComing together from different musical backgrounds, Dev brings an attention to musical and rythmic-detail, having been classically trained in jazz drumming and rock guitar, whilst Lon brings his deep knowledge of electronic music production and finesse for intricate sound design and emotional compositions to the duo - they would describe their sound as a culmination of uplifting and emotive progressions, driven by strong basslines and soaring melodics. \n\nDNA achieved a Top 10 position on <a href="spotify:artist:3BtOWcNsCesRzrZLII9zdz" data-name="Beatport">Beatport</a>&#39;s&#39; Hype Chart as well as a Top 100 position on <a href="spotify:artist:3BtOWcNsCesRzrZLII9zdz" data-name="Beatport">Beatport</a>&#39;s&#39; Melodic House Chart with their prior Ton Töpferei. \n\nThe duo are feeling ambitious for 2021, with some amazing new music in the works.'
    watchlist_presence = 'True'
    self.section_header.text = 'MAIN FEATURES'
    
    self.spacer_bottom_margin.height = 80

    # --------------------------------------
    # HEADER:
    # Image
    if sug["ArtistPictureURL"] != 'None':
      self.artist_image.source = sug["ArtistPictureURL"]
    else:
      self.artist_image.source = '_/theme/pics/Favicon_orange.JPG'

    # Image Link
    if sug["ArtistURL"] != 'None': self.artist_link.url = sug["ArtistURL"]

    # Name
    self.name.text = sug["Name"]
    if watchlist_presence == 'True':
      self.link_watchlist_name.icon = 'fa:star'
    else:
      self.link_watchlist_name.icon = 'fa:star-o'

    # Origin
    if sug["Countries"] == 'None': self.countries.text = '-'
    else: self.countries.text = sug["Countries"]
      
    # Genres
    if sug["Genres"] == 'None': self.genres.text = '-'
    else: self.genres.text = sug["Genres"]

    # Popularity
    if sug["ArtistPopularity_lat"] == 'None': self.artist_popularity_lat.text = '-'
    else: self.artist_popularity_lat.text = sug["ArtistPopularity_lat"]

    # Follower
    if sug["ArtistFollower_lat"] == 'None': self.artist_follower_lat.text = '-'
    else: self.artist_follower_lat.text = f'{int(sug["ArtistFollower_lat"]):,}'
    
    # Prediction
    if (sug["Prediction"] == 'None'): pred = 'N/A'
    elif (int(sug["Prediction"]) > 100): pred = 100
    elif (int(sug["Prediction"]) < 0): pred = 0
    else: pred = "{:.0f}".format(round(float(sug["Prediction"]),0))
    self.prediction.text = str(pred) + '%'

    # Bio
    self.bio.text = biography[1:70] + '...'

    
    
    # --------------------------------------
    # FOOTER:
    # Spotify Web-Player
    self.c_web_player.html = '<iframe style="border-radius:12px" src="https://open.spotify.com/embed/artist/' + sug["SpotifyArtistID"] + '?utm_source=generator&theme=0&autoplay=true" width="100%" height="80" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'

  
  def info_click(self, **event_args):
    if self.info.icon == 'fa:angle-down':
      self.info.icon = 'fa:angle-up'
      self.info.icon_align = 'left_edge'
      self.info.text = 'This is your artist dashboard - showing everything you need to know about the artist recommended just for you by our AI. Rate the artist, and our algorithm will continue to learn what you like and appreciate in artists - be it their music style, their origin or label status. If you want to narrow it down manually, use the filters!'
    else:
      self.info.icon = 'fa:angle-down'
      self.info.icon_align = 'left'
      self.info.text = 'Info'

  def link_watchlist_name_click(self, **event_args):
    if self.link_watchlist_name.icon == 'fa:star':
      self.link_watchlist_name.icon = 'fa:star-o'
    else:
      self.link_watchlist_name.icon = 'fa:star'

  def bio_click(self, **event_args):
    biography = 'DNA are a producer duo from Johannesburg, South Africa - comprising of Devon Horowitz and Alon Alkalay. \n\nComing together from different musical backgrounds, Dev brings an attention to musical and rythmic-detail, having been classically trained in jazz drumming and rock guitar, whilst Lon brings his deep knowledge of electronic music production and finesse for intricate sound design and emotional compositions to the duo - they would describe their sound as a culmination of uplifting and emotive progressions, driven by strong basslines and soaring melodics. \n\nDNA achieved a Top 10 position on <a href="spotify:artist:3BtOWcNsCesRzrZLII9zdz" data-name="Beatport">Beatport</a>&#39;s&#39; Hype Chart as well as a Top 100 position on <a href="spotify:artist:3BtOWcNsCesRzrZLII9zdz" data-name="Beatport">Beatport</a>&#39;s&#39; Melodic House Chart with their prior Ton Töpferei. \n\nThe duo are feeling ambitious for 2021, with some amazing new music in the works.'
    if self.bio.icon == 'fa:angle-down':
      self.bio.icon = 'fa:angle-up'
      self.bio.icon_align = 'left_edge'
      self.bio.text = biography
    else:
      self.bio.icon = 'fa:angle-down'
      self.bio.icon_align = 'left'
      self.bio.text = biography[1:90] + '...'

  def nav_link_1_click(self, **event_args):
    self.section_header.text = 'MAIN FEATURES'
    self.section_1.visible = True
    self.section_2.visible = False
  
  def nav_link_2_click(self, **event_args):
    self.section_header.text = 'RELEASE FEATURES'
    self.section_1.visible = False
    self.section_2.visible = True
