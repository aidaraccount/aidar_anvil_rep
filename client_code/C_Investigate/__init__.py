from ._anvil_designer import C_InvestigateTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server
import json
import datetime
import plotly.graph_objects as go


class C_Investigate(C_InvestigateTemplate):
  def __init__(self, temp_artist_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    global cur_model_id
    user = anvil.users.get_user()    
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    
    self.refresh_sug(temp_artist_id)
  
  def refresh_sug(self, temp_artist_id, **event_args):
    print(f'Refresh Sug - Start {datetime.datetime.now()}', flush=True)
    sug = json.loads(anvil.server.call('get_suggestion', cur_model_id, 'Inspect', temp_artist_id)) # Free, Explore, Inspect, Dissect

    if sug["Status"] == 'Empty Model!':
      alert(title='Train you Model..',
            content="Sorry, we cound't find any artists for your model. Make sure your model is fully set up!\n\nTherefore, go to ADD REF. ARTISTS and add some starting artists that you are interested in.")
      self.visible = False

    elif sug["Status"] == 'No Findings!':
      alert(title='No Artists found..',
            content="Sorry, we cound't find any artists for your filters.\n\nPlease check your FILTERS and change them to find additional artists.")
      self.visible = False
    
    elif sug["Status"] == 'Free Limit Reached!':
      alert(title='Free Limit Reached..',
            content="Sorry, the free version is limited in the number of suggested artists - if you're interested to continue, please upgrade to one of our subscription plans.\n\nFor any questions, please contact us at info@aidar.ai\n\nYour AIDAR Team")
      self.visible = False
      
    else:      
      global artist_id
      artist_id = int(sug["ArtistID"])
      global spotify_artist_id
      spotify_artist_id = sug["SpotifyArtistID"]
      
      if sug["ArtistPictureURL"] != 'None':
        self.artist_image.source = sug["ArtistPictureURL"]
      else:
        self.artist_image.source = '_/theme/pics/Favicon_orange.JPG'
      
      if sug["ArtistURL"] != 'None': self.artist_link.url = sug["ArtistURL"]
      
      self.name.text = '   ' + sug["Name"]

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
      
      if sug["MinMusDist"] == 'None': mmd = 'N/A'
      else: mmd = "{:.2f}".format(round(float(sug["MinMusDist"]),2))
      self.min_mus_dis.text = mmd
      if sug["AvgMusDist"] == 'None': amd = 'N/A'
      else: amd = "{:.2f}".format(round(float(sug["AvgMusDist"]),2))
      self.avg_mus_dis.text = amd
      if sug["MaxMusDist"] == 'None': xmd = 'N/A'
      else: xmd = "{:.2f}".format(round(float(sug["MaxMusDist"]),2))
      self.max_mus_dis.text = xmd
      
      if (sug["AvgExplicit"] == 'None'): expl = '-'
      else: expl = "{:.0f}".format(round(float(sug["AvgExplicit"]),0))
      self.avg_explicit.text = str(expl) + '%'
      
      if sug["RelArtists7"] == 'None': self.rel_artists_7.text = '-'
      else: self.rel_artists_7.text = sug["RelArtists7"]
      
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
      # self.plot_1.figure = go.Figure(data=[go.Bar(y=float(sug["AvgDuration"]))])
      print(f'FEATURES - Start {datetime.datetime.now()}', flush=True)
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
      print(f'FEATURES - End {datetime.datetime.now()}', flush=True)
    
  def button_1_click(self, **event_args):
    self.header.scroll_into_view(smooth=True)
    anvil.server.call('add_interest', cur_model_id, artist_id, 1)
    self.refresh_sug(temp_artist_id=None)

  def button_2_click(self, **event_args):
    self.header.scroll_into_view(smooth=True)
    anvil.server.call('add_interest', cur_model_id, artist_id, 2)
    self.refresh_sug(temp_artist_id=None)

  def button_3_click(self, **event_args):
    self.header.scroll_into_view(smooth=True)
    anvil.server.call('add_interest', cur_model_id, artist_id, 3)
    self.refresh_sug(temp_artist_id=None)

  def button_4_click(self, **event_args):
    self.header.scroll_into_view(smooth=True)
    anvil.server.call('add_interest', cur_model_id, artist_id, 4)
    self.refresh_sug(temp_artist_id=None)

  def button_5_click(self, **event_args):
    self.header.scroll_into_view(smooth=True)
    anvil.server.call('add_interest', cur_model_id, artist_id, 5)
    self.refresh_sug(temp_artist_id=None)

  def button_6_click(self, **event_args):
    self.header.scroll_into_view(smooth=True)
    anvil.server.call('add_interest', cur_model_id, artist_id, 6)
    self.refresh_sug(temp_artist_id=None)

  def button_7_click(self, **event_args):
    self.header.scroll_into_view(smooth=True)
    anvil.server.call('add_interest', cur_model_id, artist_id, 7)
    self.refresh_sug(temp_artist_id=None)
