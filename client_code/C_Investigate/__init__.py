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
    
    self.plot_popularity.visible = False
    self.plot_followers.visible = False
    self.data_grid_releases.visible = False
    self.data_grid_explicit.visible = False
    self.data_grid_related_artists.visible = False
    
    #self.artist_popularity_lat.icon = '_/theme/icons/+2.png'
    #self.artist_follower_lat.icon = '_/theme/icons/-1.png'
    
    self.refresh_sug(temp_artist_id)


  # SUGGESTIONS
  def refresh_sug(self, temp_artist_id, **event_args):
    #print(f'Refresh Sug - Start {datetime.datetime.now()}', flush=True)
    sug = json.loads(anvil.server.call('get_suggestion', 'Inspect', cur_model_id, temp_artist_id)) # Free, Explore, Inspect, Dissect
    
    if sug["Status"] == 'Empty Model!':
      alert(title='Train you Model..',
            content="Sorry, we cound't find any artists for your model. Make sure your model is fully set up!\n\nTherefore, go to ADD REF. ARTISTS and add some starting artists that you are interested in.")
      self.visible = False

    elif sug["Status"] == 'No Findings!':
      alert(title='No Artists found..',
            content="Sorry, we cound't find any artists for your model. Please check two potential issues:\n\n1. Please check your FILTERS and change them to find additional artists.\n\n2. If you're just setting up your model or are subscribed to the Explore subscription, go to the ADD REF. ARTISTS page and add additional reference artists.")
      self.visible = False
    
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

      self.check_watchlist_presence(cur_model_id, artist_id)
      
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
      
      if (sug["AvgExplicit"] == 'None'): expl = '-'
      else: expl = "{:.0f}".format(round(float(sug["AvgExplicit"])*100,0))
      self.avg_explicit.text = str(expl) + '%'

      if sug["RelArtists"] == 'None': self.rel_artists_7.text = '-'
      else: self.rel_artists_7.text = sug["RelArtists"]
        
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
      #print(f'FEATURES - Start {datetime.datetime.now()}', flush=True)
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
      #print(f'FEATURES - End {datetime.datetime.now()}', flush=True)


  # POPULARITY PLOT
  def link_popularity_click(self, **event_args):
    dev_successes = json.loads(anvil.server.call('get_dev_successes', int(cur_artist_id)))
    if self.plot_popularity.visible == False:
      self.plot_popularity.visible = True
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
        'paper_bgcolor': 'rgb(25, 28, 26)',
        'plot_bgcolor': 'rgb(25, 28, 26)'
      }
    else:
      self.plot_popularity.visible = False
  
  def link_popularity_close_click(self, **event_args):
    self.plot_popularity.visible = False

  
  # FOLLOWER PLOT
  def link_follower_click(self, **event_args):
    dev_successes = json.loads(anvil.server.call('get_dev_successes', int(cur_artist_id)))
    if self.plot_followers.visible == False:
      self.plot_followers.visible = True
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
        'paper_bgcolor': 'rgb(25, 28, 26)',
        'plot_bgcolor': 'rgb(25, 28, 26)'
      }
    else:
      self.plot_followers.visible = False
      
  def link_follower_close_click(self, **event_args):
    self.plot_followers.visible = False


  # RELATED ARTISTS TABLE
  def rel_artists_7_click(self, **event_args):
    if self.data_grid_related_artists.visible == False:
      self.data_grid_related_artists_data.items = json.loads(anvil.server.call('get_dev_related_artists', int(cur_artist_id), int(cur_model_id)))
      self.data_grid_related_artists.visible = True
    else:
      self.data_grid_related_artists.visible = False
    
  # EXPLICIT TABLE
  def avg_explicit_click(self, **event_args):
    if self.data_grid_explicit.visible == False:
      self.data_grid_explicit_data.items = json.loads(anvil.server.call('get_dev_explicit', int(cur_artist_id)))
      self.data_grid_explicit.visible = True
    else:
      self.data_grid_explicit.visible = False
    
  # RELEASES TABLE
  def link_releases_click(self, **event_args):
    if self.data_grid_releases.visible == False:
      self.data_grid_releases_data.items = json.loads(anvil.server.call('get_dev_releases', int(cur_artist_id)))
      self.data_grid_releases.visible = True
    else:
      self.data_grid_releases.visible = False
      
  
  # CHECK WATCHLIST
  def check_watchlist_presence(self, cur_model_id, artist_id, **event_args):
    watchlist_presence = anvil.server.call('check_watchlist_presence', cur_model_id, artist_id)
    if watchlist_presence == 'True':
      self.button_watchlist.background = '#fd652d' # orange
      self.button_watchlist.foreground = '#f5f4f1' # white
      self.button_watchlist.icon = 'fa:check'
      self.button_watchlist.icon_align = 'right'
      self.button_watchlist.text = 'already on Watchlist  '
      self.column_panel_note.visible = True
      
  
  # RATING BUTTONS
  def button_1_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], cur_model_id, artist_id, 1, False, self.text_note.text)
    self.text_note.text = ""
    self.text_note.placeholder = "Add a note.."
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_2_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], cur_model_id, artist_id, 2, False, self.text_note.text)
    self.text_note.text = ""
    self.text_note.placeholder = "Add a note.."
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_3_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], cur_model_id, artist_id, 3, False, self.text_note.text)
    self.text_note.text = ""
    self.text_note.placeholder = "Add a note.."
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_4_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], cur_model_id, artist_id, 4, False, self.text_note.text)
    self.text_note.text = ""
    self.text_note.placeholder = "Add a note.."
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_5_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], cur_model_id, artist_id, 5, False, self.text_note.text)
    self.text_note.text = ""
    self.text_note.placeholder = "Add a note.."
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_6_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], cur_model_id, artist_id, 6, False, self.text_note.text)
    self.text_note.text = ""
    self.text_note.placeholder = "Add a note.."
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_7_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], cur_model_id, artist_id, 7, False, self.text_note.text)
    self.text_note.text = ""
    self.text_note.placeholder = "Add a note.."
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  
  # DESCRIPTION LINKS
  def info_prediction_click(self, **event_args):
    alert(title='Prediction',
    content="Prediction of interest for you personally. Is based on your individually trained Machine Learning Model. Ranges from 1 to 7.")
  def info_popularity_click(self, **event_args):
    alert(title='Popularity',
    content="Level of popularity on Spotify. Ranges from 0 to 100.")
  def info_follower_click(self, **event_args):
    alert(title='Follower',
    content="Number of followers on Spotify")
    
  def info_related_click(self, **event_args):
    alert(title='No. similar Artists of Interest',
    content="Number of artists that you rated with 6 or 7 and are very similar to the presented artist.")
  def info_explicit_click(self, **event_args):
    alert(title='Share of explicit Tracks',
    content="Share of explicit Tracks in percentage.")
  def info_no_tracks_click(self, **event_args):
    alert(title='No. Tracks',
    content="Number of tracks from the presented Artist in our database. Not all tracks of this Artist have to be in the database.")

  def info_min_distance_click(self, **event_args):
    alert(title='Min. musical Distance',
    content="If you subscribed to the Inspect or Dissect subscription, the minimal musical distance is the smallest Euclidean Distance between one of the artist's songs and your personal reference tracks.\n\nIf you have not yet added your reference tracks or are subscribed to the Explore subscription, this value is empty.")
  def info_avg_distance_click(self, **event_args):
      alert(title='Avg. musical Distance',
      content="If you subscribed to the Inspect or Dissect subscription, the average musical distance is the average Euclidean Distance between the artist's songs and your personal reference tracks.\n\nIf you have not yet added your reference tracks or are subscribed to the Explore subscription, this value is empty.")
  def info_max_distance_click(self, **event_args):
      alert(title='Max. musical Distance',
      content="If you subscribed to the Inspect or Dissect subscription, the maximal musical distance is the largest Euclidean Distance between one of the artist's songs and your personal reference tracks.\n\nIf you have not yet added your reference tracks or are subscribed to the Explore subscription, this value is empty.")

  def info_duration_click(self, **event_args):
      alert(title='Avg. Duration',
      content="The average duration of all songs of an artist in seconds.")
  def info_danceability_click(self, **event_args):
      alert(title='Avg. Danceability',
      content="Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity.\n\nWe average this value across all songs and its value ranges from 0 (least danceable) to 100% (most danceable).")
  def info_energy_click(self, **event_args):
      alert(title='Avg. Energy',
      content="Energy is a measure from 0 to 100% and represents a perceptual measure of intensity and activity on average across all songs.")
  def info_key_click(self, **event_args):
      alert(title='Avg. Key',
      content="The estimated overall average key of all songs of an artist")
  def info_loudness_click(self, **event_args):
      alert(title='Avg. relative Loudness',
      content="The overall average loudness of all tracks in decibels (dB).\n\nFor each track the loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks.")
  def info_mode_click(self, **event_args):
      alert(title='Mode',
      content="Mode indicates the portion of tracks in major (modality) of an artist. Ranges from 0 to 100%.")
  def info_speechiness_click(self, **event_args):
      alert(title='Avg. Speechiness',
      content="Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g., talk show, audiobook, poetry), the closer to 100% the attribute value. It is averaged across all songs of that artist.")
  def info_acousticness_click(self, **event_args):
      alert(title='Avg. Acousticness',
      content="A confidence measure from 0 to 100% of whether an artist's tracks are acoustic. 100% represents high confidence the tracks are acoustic.")
  def info_instrumentalness_click(self, **event_args):
      alert(title='Avg. Instrumentalness',
      content="Measures whether the tracks of an artist contain no vocals.\n\n“Ooh” and “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly “vocal”. The closer the instrumentalness value is to 100%, the greater likelihood the tracks contain no vocal content.")
  def info_liveness_click(self, **event_args):
      alert(title='Avg. Liveness',
      content="Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the tracks of that artist were performed live.")
  def info_valence_click(self, **event_args):
      alert(title='Avg. Valence',
      content="A measure from 0 to 100% describing the musical positiveness conveyed by an artist's tracks. Tracks with high valence sound more positive (e.g., happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g., sad, depressed, angry).")
  def info_tempo_click(self, **event_args):
      alert(title='Avg. Tempo',
      content="The overall average estimated tempo of all track of an artist in beats per minute (BPM).")

  def info_genre_click(self, **event_args):
      alert(title='Genre',
      content="Represents the genre of an artist.\n\nUnfortunatelly, this information is not present for all artists.")
  def info_origin_click(self, **event_args):
      alert(title='Origin',
      content="Represents the origin of an artist.\n\nUnfortunatelly, this information is not present for all artists.")
  
  def info_first_release_click(self, **event_args):
      alert(title='First Release',
      content="Date of the first release of an artist on Spotify.\n\nOur database is not complete yet - there might be missing tracks that are not present in our database.")
  def info_last_release_click(self, **event_args):
      alert(title='Latest Release',
      content="Date of the latest release of an artist on Spotify.\n\nOur database is not complete yet - there might be missing tracks that are not present in our database.")
  
  def info_latest_label_click(self, **event_args):
      alert(title='Latest Label',
      content="Name of the latest label this artist worked with.")

  def info_major_click(self, **event_args):
      alert(title='Major Coop',
      content="Indicates whether this artist ever worked with a major label or not.")
  def info_sub_major_click(self, **event_args):
      alert(title='Sub-Major Coop',
      content="Indicates whether this artist ever worked with a sub-major label or not.")

  def button_watchlist_click(self, **event_args):
    if self.button_watchlist.background == '':
      self.button_watchlist.background = '#fd652d' # orange
      self.button_watchlist.foreground = '#f5f4f1' # white
      self.button_watchlist.icon = 'fa:check'
      self.button_watchlist.icon_align = 'right'
      self.button_watchlist.text = 'added to Watchlist  '
      self.column_panel_note.visible = True
      self.update_watchlist_notification(cur_model_id, artist_id, True, True)
      Notification("",
        title=f"{self.name.text} added to the watchlist!",
        style="success").show()
    else:
      self.button_watchlist.background = ''
      self.button_watchlist.foreground = ''
      self.button_watchlist.icon = ''
      self.button_watchlist.text = 'add to Watchlist'
      self.column_panel_note.visible = False
      self.update_watchlist_notification(cur_model_id, artist_id, False, False)

  # Change the bools watchlist & notification in the leads table
  def update_watchlist_notification(self, cur_model_id, artist_id, watchlist, notification, **event_args):
    anvil.server.call('update_watchlist_notification',
                      cur_model_id,
                      artist_id,
                      watchlist,
                      notification
                      )
    self.parent.parent.update_no_notifications()

  def add_note(self, **event_args):
    anvil.server.call('add_note', user["user_id"], cur_model_id, artist_id, '', '', self.text_note.text)
    self.text_note.text = ""
    self.text_note.placeholder = "Add another note.."
    Notification("",
      title=f"Note saved!",
      style="success").show()

    