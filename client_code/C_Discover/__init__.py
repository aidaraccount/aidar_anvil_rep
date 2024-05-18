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
    global user
    global cur_model_id
    user = anvil.users.get_user()
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    
    sug = {"Status": "Success!", "ModelID": "2", "ArtistID": "560919", "SpotifyArtistID": "6heMlLFM6RDDHRz99uKMqS", "Name": "RetroVision", "ArtistURL": "https://open.spotify.com/artist/6heMlLFM6RDDHRz99uKMqS", "ArtistPictureURL": "https://i.scdn.co/image/ab6761610000e5eb1428ee0feb9dae32ac83669e", "NoTracks": "113", "ArtistPopularity_lat": "46", "ArtistFollower_lat": "93339", "FirstReleaseDate": "2014-11-18", "LastReleaseDate": "2024-03-08", "MajorCoop": "1", "SubMajorCoop": "1", "LatestLabel": "Warner Music Central Europe", "AvgExplicit": "0.0354", "MinMusDist": "0.8885102232353875", "AvgMusDist": "0.9062671665657496", "MaxMusDist": "0.9240241098961117", "AvgDuration": "187.52287610619476", "AvgDanceability": "0.678221238938053", "AvgEnergy": "0.857221238938053", "AvgKey": "4.8938", "AvgLoudness": "-4.713938053097346", "AvgMode": "0.4867", "AvgSpeechiness": "0.09923097345132743", "AvgAcousticness": "0.0627684778761062", "AvgInstrumentalness": "0.2995615364601769", "AvgLiveness": "0.3070929203539824", "AvgValence": "0.457787610619469", "AvgTempo": "126.82925663716814", "Genres": "pop, house, edm, electro", "Countries": "Sweden", "RelArtists": "6", "Prediction": "93"}
    biography = 'DNA are a producer duo from Johannesburg, South Africa - comprising of Devon Horowitz and Alon Alkalay. \n\nComing together from different musical backgrounds, Dev brings an attention to musical and rythmic-detail, having been classically trained in jazz drumming and rock guitar, whilst Lon brings his deep knowledge of electronic music production and finesse for intricate sound design and emotional compositions to the duo - they would describe their sound as a culmination of uplifting and emotive progressions, driven by strong basslines and soaring melodics. \n\nDNA achieved a Top 10 position on <a href="spotify:artist:3BtOWcNsCesRzrZLII9zdz" data-name="Beatport">Beatport</a>&#39;s&#39; Hype Chart as well as a Top 100 position on <a href="spotify:artist:3BtOWcNsCesRzrZLII9zdz" data-name="Beatport">Beatport</a>&#39;s&#39; Melodic House Chart with their prior Ton Töpferei. \n\nThe duo are feeling ambitious for 2021, with some amazing new music in the works.'
    watchlist_presence = 'True'
        
    self.spacer_bottom_margin.height = 80

    if sug["Status"] == 'Empty Model!':
      alert(title='Train you Model..',
            content="Sorry, we cound't find any artists for your model. Make sure your model is fully set up!\n\nTherefore, go to ADD REF. ARTISTS and add some starting artists that you are interested in.")
      self.visible = False

    elif sug["Status"] == 'No Findings!':
      result = alert(title='No Artists found..',
                content="Sorry, we cound't find any artists for your model. Please check two potential issues:\n\n1. Please check your FILTERS and change them to find additional artists.\n\n2. If you're just setting up your model or are subscribed to the Explore subscription, go to the ADD REF. ARTISTS page and add additional reference artists.",
                buttons=[
                  ("Change Filters", "FILTERS"),
                  ("Ok", "OK")
                ])
      self.visible = False
      if result == "FILTERS":
        open_form('Main_In', temp_artist_id = None, target = 'C_Filter', value=None)
    
    elif sug["Status"] == 'Free Limit Reached!':
      alert(title='Free Limit Reached..',
            content="Sorry, the free version is limited in the number of suggested artists - if you're interested in continuing, please upgrade to one of our subscription plans.\n\nFor any questions, please contact us at info@aidar.ai\n\nYour AIDAR Team")
      self.visible = False
      
    else:      
      global cur_artist_id
      cur_artist_id = sug["ArtistID"]
      global artist_id
      artist_id = int(sug["ArtistID"])
      global spotify_artist_id
      spotify_artist_id = sug["SpotifyArtistID"]
  
      self.sec_releases.visible = True
      self.sec_success.visible = False
      self.sec_fandom.visible = False
      self.sec_musical.visible = False
    
      # self.check_watchlist_presence(cur_model_id, artist_id)
      
      if sug["ArtistPictureURL"] != 'None':
        self.artist_image.source = sug["ArtistPictureURL"]
      else:
        self.artist_image.source = '_/theme/pics/Favicon_orange.JPG'
      
      if sug["ArtistURL"] != 'None': self.artist_link.url = sug["ArtistURL"]
      
      self.name.text = '   ' + sug["Name"]
      if watchlist_presence == 'True':
        self.link_watchlist_name.icon = 'fa:star'
      else:
        self.link_watchlist_name.icon = 'fa:star-o'

      self.bio.text = biography[1:70] + '...'
      
      if sug["ArtistPopularity_lat"] == 'None': self.artist_popularity_lat.text = '-'
      else: self.artist_popularity_lat.text = sug["ArtistPopularity_lat"]
      
      if sug["ArtistFollower_lat"] == 'None': self.artist_follower_lat.text = '-'
      else: self.artist_follower_lat.text = f'{int(sug["ArtistFollower_lat"]):,}'

      if sug["NoTracks"] == 'None': self.no_tracks.text = '-'
      else: self.no_tracks.text = f'{int(sug["NoTracks"]):,}'
      
      if sug["FirstReleaseDate"] == 'None': self.first_release_date.text = '-'
      else: self.first_release_date.text = sug["FirstReleaseDate"]
      if sug["LastReleaseDate"] == 'None': self.last_release_date.text = '-'
      else: self.last_release_date.text = sug["LastReleaseDate"]
        
      if sug["MajorCoop"] == '1': mc = 'yes'
      elif sug["MajorCoop"] == '0': mc = 'no'
      else: mc = '-'
      self.major_coop.text = mc
      
      if sug["SubMajorCoop"] == '1': smc = 'yes'
      elif sug["SubMajorCoop"] == '0': smc = 'no'
      else: smc = '-'
      self.sub_major_coop.text = smc

      if sug["LatestLabel"] == 'None': ll = 'N/A'
      else: ll = sug["LatestLabel"]
      self.latest_label.text = ll
      
      if sug["MinMusDist"] == 'None': mmd = 'N/A'
      else: mmd = "{:.2f}".format(round(float(sug["MinMusDist"]),2))
      self.min_mus_dis.text = mmd
      if sug["AvgMusDist"] == 'None': amd = 'N/A'
      else: amd = "{:.2f}".format(round(float(sug["AvgMusDist"]),2))
      self.avg_mus_dis.text = amd
      if sug["MaxMusDist"] == 'None': xmd = 'N/A'
      else: xmd = "{:.2f}".format(round(float(sug["MaxMusDist"]),2))
      self.max_mus_dis.text = xmd
      
      if (sug["Prediction"] == 'None'): pred = 'N/A'
      elif (float(sug["Prediction"]) > 7): pred = 7.0
      elif (float(sug["Prediction"]) < 0): pred = 0.0
      else: pred = "{:.1f}".format(round(float(sug["Prediction"]),1))
      self.prediction.text = pred

      if sug["Genres"] == 'None': self.genres.text = '-'
      else: self.genres.text = sug["Genres"]

      if sug["Countries"] == 'None': self.countries.text = '-'
      else: self.countries.text = sug["Countries"]
      
      self.c_web_player.html = '<iframe style="border-radius:12px" src="https://open.spotify.com/embed/artist/' + spotify_artist_id + '?utm_source=generator&theme=0" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
      
      # Musical Features
      if sug["AvgDuration"] == 'None': f1 = '-'
      else: f1 = "{:.0f}".format(round(float(sug["AvgDuration"]),0))
      self.feature_1.text = f1 + ' sec'
      if sug["AvgDanceability"] == 'None': f2 = '-'
      else: f2 = "{:.0f}".format(round(float(sug["AvgDanceability"])*100,0))
      self.feature_2.text = f2 + '%'
      if sug["AvgEnergy"] == 'None': f3 = '-'
      else: f3 = "{:.0f}".format(round(float(sug["AvgEnergy"])*100,0))
      self.feature_3.text = f3 + '%'
  
      tonleiter = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
      if sug["AvgKey"] == 'None': f4 = '--'
      else: f4 = tonleiter[int(round(float(sug["AvgKey"]),0))]
      self.feature_4.text = f4
      
      if sug["AvgLoudness"] == 'None': f5 = '-'
      else: f5 = "{:.2f}".format(round(float(sug["AvgLoudness"]),2))
      self.feature_5.text = f5 + ' dB'
      if sug["AvgMode"] == 'None': f6 = '-'
      else: f6 = "{:.0f}".format(round(float(sug["AvgMode"])*100,0))
      self.feature_6.text = f6 + '% Major'
      if sug["AvgSpeechiness"] == 'None': f7 = '-'
      else: f7 = "{:.0f}".format(round(float(sug["AvgSpeechiness"])*100,0))
      self.feature_7.text = f7 + '%'    
      if sug["AvgAcousticness"] == 'None': f8 = '-'
      else: f8 = "{:.0f}".format(round(float(sug["AvgAcousticness"])*100,0))
      self.feature_8.text = f8 + '%'
      if sug["AvgInstrumentalness"] == 'None': f9 = '-'
      else: f9 = "{:.0f}".format(round(float(sug["AvgInstrumentalness"])*100,0))
      self.feature_9.text = f9 + '%'
      if sug["AvgLiveness"] == 'None': f10 = '-'
      else: f10 = "{:.0f}".format(round(float(sug["AvgLiveness"])*100,0))
      self.feature_10.text = f10 + '%'
      if sug["AvgValence"] == 'None': f11 = '-'
      else: f11 = "{:.0f}".format(round(float(sug["AvgValence"])*100,0))
      self.feature_11.text = f11 + '%'
      if sug["AvgTempo"] == 'None': f12 = '-'
      else: f12 = "{:.0f}".format(round(float(sug["AvgTempo"]),0))
      self.feature_12.text = f12 + ' bpm'

      # refresh visible plots/tables
      # a) Popularity
      dev_successes = json.loads(anvil.server.call('get_dev_successes', int(cur_artist_id)))
      self.plot_popularity.data = [
        go.Scatter(
          x = [x['Date'] for x in dev_successes],
          y = [x['ArtistPopularity'] for x in dev_successes],
          marker = dict(color = 'rgb(253, 101, 45)')
        )
      ]
      self.plot_popularity.layout = {
        'template': 'plotly_dark',
        'title': {
          'text' : 'Spotify Popularity over time',
          'x': 0.5,
          'xanchor': 'center'
          },
        'yaxis': {
          'title': 'Popularity',
          'range': [0, min(1.1*max([x['ArtistPopularity'] for x in dev_successes]), 100)]
        },
        'paper_bgcolor': 'rgb(40, 40, 40)',
        'plot_bgcolor': 'rgb(40, 40, 40)'
      }
      # b) Followers
      dev_successes = json.loads(anvil.server.call('get_dev_successes', int(cur_artist_id)))
      self.plot_followers.data = [
        go.Scatter(
          x = [x['Date'] for x in dev_successes],
          y = [x['ArtistFollower'] for x in dev_successes],
          marker = dict(color = 'rgb(253, 101, 45)')
        )
      ]
      self.plot_followers.layout = {
        'template': 'plotly_dark',
        'title': {
          'text' : 'Spotify Followers over time',
          'x': 0.5,
          'xanchor': 'center'
          },
        'yaxis': {
          'title': 'No. Followers',
          'range': [0, 1.1*max([x['ArtistFollower'] for x in dev_successes])]
        },
        'paper_bgcolor': 'rgb(40, 40, 40)',
        'plot_bgcolor': 'rgb(40, 40, 40)'
      }
      # c) related artists table
      if self.data_grid_related_artists.visible == True:
        self.data_grid_related_artists_data.items = json.loads(anvil.server.call('get_dev_related_artists', int(cur_artist_id), int(cur_model_id)))
      # d) release tables
      if self.data_grid_releases.visible == True:
        self.data_grid_releases_data.items = json.loads(anvil.server.call('get_dev_releases', int(cur_artist_id)))

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
      self.bio.text = biography[1:70] + '...'

  def nav_releases_click(self, **event_args):
    self.sec_releases.visible = True
    self.sec_success.visible = False
    self.sec_fandom.visible = False
    self.sec_musical.visible = False
  
  def nav_success_click(self, **event_args):
    self.sec_releases.visible = False
    self.sec_success.visible = True
    self.sec_fandom.visible = False
    self.sec_musical.visible = False

  def nav_fandom_click(self, **event_args):
    self.sec_releases.visible = False
    self.sec_success.visible = False
    self.sec_fandom.visible = True
    self.sec_musical.visible = False
    
  def nav_musical_click(self, **event_args):
    self.sec_releases.visible = False
    self.sec_success.visible = False
    self.sec_fandom.visible = False
    self.sec_musical.visible = True