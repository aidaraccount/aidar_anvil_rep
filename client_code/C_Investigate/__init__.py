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
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    global cur_model_id
    user = anvil.users.get_user()    
    cur_model_id = anvil.server.call('GetModelID',  user["user_id"])

    self.refresh_sug()

  
  def refresh_sug(self, **event_args):
    print(f'Refresh Sug - Start {datetime.datetime.now()}', flush=True)
    sug = json.loads(anvil.server.call('GetSug', cur_model_id))
    global artist_id
    artist_id = int(sug["ArtistID"])
    global spotify_artist_id
    spotify_artist_id = sug["SpotifyArtistID"]
    
    if sug["ArtistPictureURL"] != 'None':
      self.artist_image.source = sug["ArtistPictureURL"]
    else:
      self.artist_image.source = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAoAAAAEkCAYAAAC/qIBGAAAgAElEQVR4Xu2dCZwcRb3Hq3pmN+ceM7szE0JA4KEooKDggXgggiKgcoZbOQQUBLJHwqHAgoBA9gi3D7kEFAREEBDkVlFBQX34AJ8gEo5kZ2Z39sq1OzNd71ebBBJIdmemq2Z6Zn7tJ2bZVP3rX9+q7v51Hf+SghcJkAAJkAAJkAAJkEBVEZBVVVtWlgRIgARIgARIgARIQFAAshOQAAmQAAmQAAmQQJURoACssgZndUmABEiABEiABEiAApB9gARIgARIgARIgASqjAAFYJU1OKtLAiRAAiRAAiRAAhSA7AMkQAIkQAIkQAIkUGUEKACrrMFZXRIgARIgARIgARKgAGQfIAESIAESIAESIIEqI0ABWGUNzuqSAAmQAAmQAAmQAAUg+wAJkAAJkAAJkAAJVBkBCsAqa3BWlwRIgARIgARIgAQoANkHSIAESIAESIAESKDKCFAAVlmDs7okQAIkQAIkQAIkQAHIPkACJEACJEACJEACVUaAArDKGpzVJQESIAESIAESIAEKQPYBEiABEiABEiABEqgyAhSAVdbgrC4JkAAJkAAJkAAJUACyD5AACZAACZAACZBAlRGgAKyyBmd1SYAESIAESIAESIACkH2ABEiABEiABEiABKqMAAVglTU4q0sCJEACJEACJEACFIDsAyRAAiRAAiRAAiRQZQQoAKuswVldEiABEiABEiABEqAAZB8gARIgARIgARIggSojQAFYZQ3O6pIACZAACZAACZAABSD7AAmQAAmQAAmQAAlUGQEKwCprcFaXBEiABEiABEiABCgA2QdIgARIgARIgARIoMoIUABWWYOzuiRAAiRAAiRAAiRAAcg+QAIkQAIkQAIkQAJVRoACsMoanNUlARIgARIgARIgAQpA9gESIAESIAESIAESqDICFIBV1uCsLgmQAAmQAAmQAAlQALIPkAAJkAAJkAAJkECVEaAArLIGZ3VJgARIgARIgARIgAKQfYAESIAESIAESIAEqowABWCVNTirSwIkQAIkQAIkQAIUgOwDJEACJEACJEACJFBlBCgAq6zBWV0SIAESIAESIAESoABkHyABEiABEiABEiCBKiNAAVhlDc7qkgAJkAAJkAAJkAAFIPsACZAACZAACZAACVQZAQrAKmtwVpcESIAESIAESIAEKADZB0iABEiABEiABEigyghQAFZZg7O6JEACJEACJEACJEAByD5AAiRAAiRAAiRAAlVGgAKwyhqc1SUBEiABEiABEiABCkD2ARIgARIgARIgARKoMgIUgFXW4KwuCZAACZAACZAACVAAsg+QAAmQAAmQAAmQQJURoACssgZndUmABEiABEiABEiAApB9gARIgARIgARIgASqjAAFYJU1OKtLAiRAAiRAAiRAAhSA7AMkQAIkQAIkQAIkUGUEKACrrMFZXRIgARIgARIgARKgAGQfIAESIAESIAESIIEqI0ABWGUNzuqSAAmQAAmQAAmQAAUg+wAJkAAJkAAJkAAJVBkBCsAqa3BWlwRIgARIgARIgAQoANkHSIAESIAESIAESKDKCFAAVlmDs7okQAIkQAIkQAIkQAHIPkACJEACJEACJEACVUaAArDKGpzVJQESIAESIAESIAEKQPYBEiABEiABEiABEqgyAhSAVdbgrC4JkAAJkAAJkAAJUACyD5AACZAACZAACZBAlRGgAKyyBmd1SYAESIAESIAESIACkH2ABEiABEiABEiABKqMAAVglTU4q0sCJEACJEACJEACFIDsAyRAAiRAAiRAAiRQZQQoAKuswVldEiABEiABEiABEqAAZB8gARIgARIgARIggSojQAFYZQ3O6pIACZAACZAACZAABSD7AAmQAAmQAAmQAAlUGQEKwCprcFaXBEiABEiABEiABCgA2QdIgARIgARIgARIoMoIUABWWYOzuiRAAiRAAiRAAiRAAcg+QAIkQAIkQAIkQAJVRoACsMoanNUlARIgARIgARIgAQpA9gESIAESIAESIAESqDICFIBV1OCp00MN7pgzs5RVbmqYlZQdL4yV0gevZY+0x6Kj2UyNVzv55H/8zf7euXeKbD55mLZ6CKiWOdP6xcpwKWtcO3XqqvofvtVfSh+8lp04KTLTmeI2eLXjh/zTaqRa68eKjTg0fUwo/W867fjfynGVCrjKdVxXLXPdrOOOjk7NbDI7lLnzhReyfAb5oWXN+UABaI6l7y0NtEW78URoKa2j6rPhruRTpfXBW+mptujzsPBhb1byy51x1CbRhcne/HIxdbUQ6G+NHCKlvL209ZX3hbviXyutD95KH2iPnKqUvMyblZLlVgIPeCmFelv5Cfxm/Hdq/Hd44Y//0+p/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'
    self.artist_link.url = sug["ArtistURL"]
    
    self.name.text = '   ' + sug["Name"]
    self.artist_popularity_lat.text = sug["ArtistPopularity_lat"]
    self.artist_follower_lat.text = sug["ArtistFollower_lat"]
    self.no_tracks.text = sug["NoTracks"]
    self.first_release_date.text = sug["FirstReleaseDate"]
    self.last_release_date.text = sug["LastReleaseDate"]

    if sug["MajorCoop"] == '1': mc = 'yes'
    elif sug["MajorCoop"] == '0': mc = 'no'
    else: mc = 'nan'
    self.major_coop.text = mc
    
    if sug["SubMajorCoop"] == '1': smc = 'yes'
    elif sug["SubMajorCoop"] == '0': smc = 'no'
    else: smc = 'nan'
    self.sub_major_coop.text = smc
    
    if sug["MinMusDist"] == 'None': mmd = 'nan'
    else: mmd = round(float(sug["MinMusDist"]),2)
    self.min_mus_dis.text = mmd
    if sug["AvgMusDist"] == 'None': amd = 'nan'
    else: amd = round(float(sug["AvgMusDist"]),2)
    self.avg_mus_dis.text = amd
    if sug["MaxMusDist"] == 'None': xmd = 'nan'
    else: xmd = round(float(sug["MaxMusDist"]),2)
    self.max_mus_dis.text = xmd
    
    if (sug["AvgExplicit"] == 'None'):
      expl = 'nan'
    else:
      expl = round(float(sug["AvgExplicit"]), 0)
    self.avg_explicit.text = str(expl) + '%'
    # self.avg_explicit.text = sug["AvgExplicit"] + '%'
    
    self.rel_artists_7.text = sug["RelArtists7"]
    
    if (sug["Prediction"] == 'None'):
      pred = 'nan'
    elif (float(sug["Prediction"]) > 7):
      pred = 7.0
    elif (float(sug["Prediction"]) < 0):
      pred = 0.0
    else:
      pred = round(float(sug["Prediction"]),1)
    self.prediction.text = pred
    
    self.genres.text = sug["Genres"]
    self.countries.text = sug["Countries"]
    
    self.c_web_player.html = '<iframe style="border-radius:12px" src="https://open.spotify.com/embed/artist/' + spotify_artist_id + '?utm_source=generator&theme=0" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'

    # BAR CHART
    # self.plot_1.figure = go.Figure(data=[go.Bar(y=float(sug["AvgDuration"]))])
    print(f'FEATURES - Start {datetime.datetime.now()}', flush=True)
    if sug["AvgDuration"] == 'None': f1 = 'nan'
    else: f1 = "{:.0f}".format(round(float(sug["AvgDuration"]),0))
    self.feature_1.text = f1 + ' sec'
    if sug["AvgDanceability"] == 'None': f2 = 'nan'
    else: f2 = "{:.0f}".format(round(float(sug["AvgDanceability"])*100,0))
    self.feature_2.text = f2 + '%'
    if sug["AvgEnergy"] == 'None': f3 = 'nan'
    else: f3 = "{:.0f}".format(round(float(sug["AvgEnergy"])*100,0))
    self.feature_3.text = f3 + '%'  
    if sug["AvgKey"] == 'None': f4 = 'nan'
    else: f4 = "{:.0f}".format(round(float(sug["AvgKey"]),0))
    self.feature_4.text = f4    
    if sug["AvgLoudness"] == 'None': f5 = 'nan'
    else: f5 = "{:.2f}".format(round(float(sug["AvgLoudness"]),2))
    self.feature_5.text = f5 + ' dB'
    if sug["AvgMode"] == 'None': f6 = 'nan'
    else: f6 = "{:.1f}".format(round(float(sug["AvgMode"]),1))
    self.feature_6.text = f6 + '% Major'
    if sug["AvgSpeechiness"] == 'None': f7 = 'nan'
    else: f7 = "{:.0f}".format(round(float(sug["AvgSpeechiness"])*100,0))
    self.feature_7.text = f7 + '%'    
    if sug["AvgAcousticness"] == 'None': f8 = 'nan'
    else: f8 = "{:.0f}".format(round(float(sug["AvgAcousticness"])*100,0))
    self.feature_8.text = f8 + '%'
    if sug["AvgInstrumentalness"] == 'None': f9 = 'nan'
    else: f9 = "{:.0f}".format(round(float(sug["AvgInstrumentalness"])*100,0))
    self.feature_9.text = f9 + '%'
    if sug["AvgLiveness"] == 'None': f10 = 'nan'
    else: f10 = "{:.0f}".format(round(float(sug["AvgLiveness"])*100,0))
    self.feature_10.text = f10 + '%'
    if sug["AvgValence"] == 'None': f11 = 'nan'
    else: f11 = "{:.0f}".format(round(float(sug["AvgValence"])*100,0))
    self.feature_11.text = f11 + '%'
    if sug["AvgTempo"] == 'None': f12 = 'nan'
    else: f12 = "{:.0f}".format(round(float(sug["AvgTempo"]),0))
    self.feature_12.text = f12 + ' bpm' 
    print(f'FEATURES - End {datetime.datetime.now()}', flush=True)
    
  def button_1_click(self, **event_args):
    anvil.server.call('AddInterest', cur_model_id, artist_id, 1)
    self.refresh_sug()

  def button_2_click(self, **event_args):
    anvil.server.call('AddInterest', cur_model_id, artist_id, 2)
    self.refresh_sug()

  def button_3_click(self, **event_args):
    anvil.server.call('AddInterest', cur_model_id, artist_id, 3)
    self.refresh_sug()

  def button_4_click(self, **event_args):
    anvil.server.call('AddInterest', cur_model_id, artist_id, 4)
    self.refresh_sug()

  def button_5_click(self, **event_args):
    anvil.server.call('AddInterest', cur_model_id, artist_id, 5)
    self.refresh_sug()

  def button_6_click(self, **event_args):
    anvil.server.call('AddInterest', cur_model_id, artist_id, 6)
    self.refresh_sug()

  def button_7_click(self, **event_args):
    anvil.server.call('AddInterest', cur_model_id, artist_id, 7)
    self.refresh_sug()
