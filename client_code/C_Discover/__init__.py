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
from collections import defaultdict
import itertools
from ..CustomAlertForm import CustomAlertForm  # Import the custom form



class C_Discover(C_DiscoverTemplate):
  def __init__(self, model_id, temp_artist_id, **properties):
    print(f"{datetime.now()}: C_Discover - __init__ - 1", flush=True)    
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.
    begin = datetime.now()
    
    global user
    user = anvil.users.get_user()
    self.model_id=model_id
    
    print(f"{datetime.now()}: C_Discover - __init__ - 2", flush=True)
    self.refresh_sug(temp_artist_id)
    print(f"{datetime.now()}: C_Discover - __init__ - 3", flush=True)
    
    print(f"TotalTime C_Discover: {datetime.now() - begin}", flush=True)

  
  # --------------------------------------------
  # SUGGESTIONS
  def refresh_sug(self, temp_artist_id, **event_args):    
    global temp_artist_id_global
    temp_artist_id_global = temp_artist_id
    self.spacer_bottom_margin.height = 80
    sug = json.loads(anvil.server.call('get_suggestion', 'Inspect', self.model_id, temp_artist_id)) # Free, Explore, Inspect, Dissect
    
    self.Artist_Name_Details.clear()
    self.flow_panel_genre_tile.clear()
    self.flow_panel_social_media_tile.clear()
    
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
        open_form('Main_In', model_id=self.model_id, temp_artist_id = None, target = 'C_Filter', value=None)
    
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
      global biography
      biography = sug["Biography"]
      self.biography = biography
      
      self.sec_releases.visible = True
      self.sec_success.visible = False
      self.sec_fandom.visible = False
      self.sec_musical.visible = False
   
      watchlist_presence = anvil.server.call('check_watchlist_presence', self.model_id, artist_id)

      # Filter Button visibility
      activefilters = anvil.server.call('check_filter_presence', self.model_id)
      if activefilters == 'False':
        self.button_remove_filters.visible = False
      else:
        self.button_remove_filters.visible = True

      
      # -------------------------------
      # ARTIST HEADER
      # picture and its link
      if sug["ArtistPictureURL"] != 'None':
        self.artist_image.source = sug["ArtistPictureURL"]
      else:
        self.artist_image.source = '_/theme/pics/Favicon_orange.JPG'
      
      if sug["ArtistURL"] != 'None': self.artist_link.url = sug["ArtistURL"]

      # watchlist
      if watchlist_presence == 'True':
        self.link_watchlist_name.icon = 'fa:star'
        self.link_watchlist_name2.icon = 'fa:star'
      else:
        self.link_watchlist_name.icon = 'fa:star-o'
        self.link_watchlist_name2.icon = 'fa:star-o'

      # name
      artist_name_component = Label(text=sug["Name"], role="artist-name-tile", spacing_above=0, spacing_below=0)
      self.Artist_Name_Details.add_component(artist_name_component)

      # genres
      if sug["Genres"] == 'None':
        pass
      else:
        genres_string = sug["Genres"]
        # Clean up the string and convert to list
        genres_string_cleaned = genres_string.strip("[]").replace("'", "")
        genres_list = [genre.strip() for genre in genres_string_cleaned.split(',')]  
        # Add Genres to FlowPanel
        for genre in genres_list:
          genre_label = Label(text=genre)
          genre_label.role = 'genre-box'
          self.flow_panel_genre_tile.add_component(genre_label)

      # Social media
      platform_dict = {
        "Spotify": "fa:spotify",
        "Amazon": "fa:amazon",
        "Soundcloud": "fa:soundcloud",
        "Apple Music": "fa:apple",
        "Facebook": "fa:facebook",
        "Instagram": "fa:instagram",
        "Twitter": "fab:x-twitter",
        "YouTube": "fa:youtube",
        "Deezer": "fab:deezer",
        "TikTok": "fab:tiktok"
       }
      
      if sug["Platforms"] == 'None':
        self.social_media_link.visible = False
      else:
        social_media_list = json.loads(sug["Platforms"])
        for i in range(0, len(social_media_list)):
          found = False

          if social_media_list[i]["platform"] in platform_dict:  
            found = True
            social_media_link = Link(icon=platform_dict[social_media_list[i]["platform"]])
            social_media_link.role = "music-icons-tile"
            

          if found is True:
            # social_media_link.role = 'genre-box'
            social_media_link.url = social_media_list[i]["platform_url"]
            self.flow_panel_social_media_tile.add_component(social_media_link)
      
      # origin
          
      if sug["Countries"] == 'None':
        pass
      else:
        country = json.loads(sug["Countries"])
        # self.countries.text = country["CountryName"]
        # self.Artist_Country.text = country["CountryCode"]
        # flag_url = flag_url_template https://flagcdn.com/w80/ua.png
        country_flag = Image(source="https://flagcdn.com/w40/" + country["CountryCode"].lower() + ".png", spacing_below=0, spacing_above=0)
        country_flag.role = 'country-flag-icon'
        country_flag.tooltip = country["CountryName"]
        self.Artist_Name_Details.add_component(country_flag)
      
      # birt date
      if sug["BirthDate"] == 'None': 
        self.birthday.visible = False
      else:
        self.birthday.visible = True
        self.birthday.text = sug["BirthDate"]

      # gender
      if sug["Gender"] == 'None':
        self.gender.visible = False
      else:
        self.gender.visible = True
        self.gender.text = sug["Gender"]

      # line condition
      if sug["BirthDate"] != 'None' and sug["Gender"] != 'None':
        self.gender_birthday_line.visible = True
      else:
        self.gender_birthday_line.visible = False
      
      # popularity
      if sug["ArtistPopularity_lat"] == 'None':
        self.KPI_tile_1.text = '-'
      else:
        self.KPI_tile_1.text = sug["ArtistPopularity_lat"]

      # follower
      if sug["ArtistFollower_lat"] == 'None':
        self.KPI_tile_2.text = '-'
      else:
        self.KPI_tile_2.text = f'{int(sug["ArtistFollower_lat"]):,}'

      # prediction
      if (sug["Prediction"] == 'None'): pred = 'N/A'
      elif (float(sug["Prediction"]) > 7): pred = 7.0
      elif (float(sug["Prediction"]) < 0): pred = 0.0
      else: pred = "{:.1f}".format(round(float(sug["Prediction"]),1))
      self.prediction.text = pred

      # biography
      if biography != 'None':
        if len(biography) >= 200:
          self.bio_text.content = biography[0:200] + '...'
          # self.bio_text_2.content = biography[0:310] + '...'
        else:
          self.bio_text.content = biography
          # self.bio_text_2.content = biography
      else:
        self.bio.visible = False     

      
      # -------------------------------
      # I. RELEASES
      # a) stats
      if sug["NoTracks"] == 'None': self.no_tracks.text = '-'
      else: self.no_tracks.text = f'{int(sug["NoTracks"]):,}'
      
      if sug["FirstReleaseDate"] == 'None': self.first_release_date.text = '-'
      else: self.first_release_date.text = sug["FirstReleaseDate"]
      
      if sug["LastReleaseDate"] == 'None': self.last_release_date.text = '-'
      else: self.last_release_date.text = sug["LastReleaseDate"]

      if sug["LatestLabel"] == 'None': ll = 'N/A'
      else: ll = sug["LatestLabel"]
      self.latest_label.text = ll
        
      if sug["MajorCoop"] == '1': mc = 'yes'
      elif sug["MajorCoop"] == '0': mc = 'no'
      else: mc = '-'
      self.major_coop.text = mc
      
      if sug["SubMajorCoop"] == '1': smc = 'yes'
      elif sug["SubMajorCoop"] == '0': smc = 'no'
      else: smc = '-'
      self.sub_major_coop.text = smc

      co_artists = json.loads(anvil.server.call('get_co_artists', int(cur_artist_id)))
      if co_artists == []:
        self.co_artists_avg.text = '-'
      else:
        self.co_artists_avg.text = "{:.2f}".format(round(co_artists[0]["avg_co_artists_per_track"],2))      
      
      # b) release tables
      if self.data_grid_releases.visible is True:
        self.data_grid_releases_data.items = json.loads(anvil.server.call('get_dev_releases', int(cur_artist_id)))

      # c) labels freq
      labels_freq = json.loads(anvil.server.call('get_labels_freq', int(cur_artist_id)))
      if labels_freq != []:
        self.plot_labels_freq.visible = True
        self.no_labels_freq.visible = False
        
        self.plot_labels_freq.data = [
          go.Bar(
            x = [x['LabelName'] for x in labels_freq],
            y = [x['NoLabels'] for x in labels_freq],
            marker = dict(color = 'rgb(253, 101, 45)')
          )
        ]
        self.plot_labels_freq.layout = {
          'template': 'plotly_dark',
          'title': {
            'text' : 'Most frequent Label cooperations',
            'x': 0.5,
            'xanchor': 'center'
            },
          'yaxis': {
            'title': 'No. Labels',
            'range': [0, 1.1*max([x['NoLabels'] for x in labels_freq])]
          },
          'paper_bgcolor': 'rgb(40, 40, 40)',
          'plot_bgcolor': 'rgb(40, 40, 40)'
        }
      else:
        self.plot_labels_freq.visible = False
        self.no_labels_freq.visible = True

      # d) co-artists by frequency
      if self.data_grid_co_artists_freq.visible is True:
        self.data_grid_co_artists_freq_data.items = co_artists
      
      # e) co-artists by popularity
      if self.data_grid_co_artists_pop.visible is True:
        self.data_grid_co_artists_pop_data.items = sorted(co_artists, key=lambda x: float(x['ArtistPopularity_lat']), reverse=True)
      
      # f) related artists table
      # d) related artists table
      if self.data_grid_related_artists.visible is True:
        self.data_grid_related_artists_data.items = json.loads(anvil.server.call('get_dev_related_artists', int(cur_artist_id), int(self.model_id)))

      
      # -------------------------------
      # II. SUCCESS
      dev_successes = json.loads(anvil.server.call('get_dev_successes', int(cur_artist_id)))

      # a) stats
      if sug["ArtistPopularity_lat"] == 'None': self.sp_pop_lat.text = '-'
      else: self.sp_pop_lat.text = sug["ArtistPopularity_lat"]
      
      if sug["ArtistFollower_lat"] == 'None': self.sp_fol_lat.text = '-'
      else: self.sp_fol_lat.text = f'{int(sug["ArtistFollower_lat"]):,}'
      
      # a) Popularity
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

      
      # -------------------------------
      # III. FANDOM
      # a) mtl. listeners
      mtl_listeners = json.loads(anvil.server.call('get_mtl_listeners', int(cur_artist_id)))
      if mtl_listeners != []:
        self.plot_mtl_listeners.visible = True
        self.no_mtl_listeners.visible = False
        
        self.plot_mtl_listeners.data = [
          go.Scatter(
            x = [x['Date'] for x in mtl_listeners],
            y = [x['MtlListeners'] for x in mtl_listeners],
            marker = dict(color = 'rgb(253, 101, 45)')
          )
        ]
        self.plot_mtl_listeners.layout = {
          'template': 'plotly_dark',
          'title': {
            'text' : 'Spotify mtl. Listeners over time',
            'x': 0.5,
            'xanchor': 'center'
            },
          'yaxis': {
            'title': 'Mtl. Listeners',
            'range': [0, 1.1*max([x['MtlListeners'] for x in mtl_listeners])]
          },
          'paper_bgcolor': 'rgb(40, 40, 40)',
          'plot_bgcolor': 'rgb(40, 40, 40)'
        }
      else:
        self.plot_mtl_listeners.visible = False
        self.no_mtl_listeners.visible = True

      # b) mtl. listeners country
      mtl_listeners_ctr = json.loads(anvil.server.call('get_mtl_listeners_country', int(cur_artist_id)))
      if mtl_listeners_ctr != []:
        self.plot_mtl_listeners_country.visible = True
        self.no_mtl_listeners_country.visible = False
        
        self.plot_mtl_listeners_country.data = [
          go.Bar(
            x = [x['CountryCode'] for x in mtl_listeners_ctr],
            y = [x['MtlListeners'] for x in mtl_listeners_ctr],
            marker = dict(color = 'rgb(253, 101, 45)')
          )
        ]
        self.plot_mtl_listeners_country.layout = {
          'template': 'plotly_dark',
          'title': {
            'text' : 'Spotify mtl. Listeners per Country',
            'x': 0.5,
            'xanchor': 'center'
            },
          'yaxis': {
            'title': 'Mtl. Listeners',
            'range': [0, 1.1*max([x['MtlListeners'] for x in mtl_listeners_ctr])]
          },
          'paper_bgcolor': 'rgb(40, 40, 40)',
          'plot_bgcolor': 'rgb(40, 40, 40)'
        }
      else:
        self.plot_mtl_listeners_country.visible = False
        self.no_mtl_listeners_country.visible = True

      # c) mtl. listeners city
      mtl_listeners_cty = json.loads(anvil.server.call('get_mtl_listeners_city', int(cur_artist_id)))
      if mtl_listeners_cty != []:
        self.plot_mtl_listeners_city.visible = True
        self.no_mtl_listeners_city.visible = False
        
        self.plot_mtl_listeners_city.data = [
          go.Bar(
            x = [x['CityWithCountryCode'] for x in mtl_listeners_cty],
            y = [x['MtlListeners'] for x in mtl_listeners_cty],
            marker = dict(color = 'rgb(253, 101, 45)')
          )
        ]
        self.plot_mtl_listeners_city.layout = {
          'template': 'plotly_dark',
          'title': {
            'text' : 'Spotify mtl. Listeners per City',
            'x': 0.5,
            'xanchor': 'center'
            },
          'yaxis': {
            'title': 'Mtl. Listeners',
            'range': [0, 1.1*max([x['MtlListeners'] for x in mtl_listeners_cty])]
          },
          'paper_bgcolor': 'rgb(40, 40, 40)',
          'plot_bgcolor': 'rgb(40, 40, 40)'
        }
      else:
        self.plot_mtl_listeners_city.visible = False
        self.no_mtl_listeners_city.visible = True

      # d) audience follower
      audience_follower = json.loads(anvil.server.call('get_audience_follower2', int(cur_artist_id)))
      if audience_follower != []:
        # Initialize a dictionary to hold data for each platform
        platform_data = defaultdict(lambda: {'dates': [], 'followers': []})
        
        # Populate the dictionary with data
        for entry in audience_follower:
            platform = entry['Platform']
            platform_data[platform]['dates'].append(entry['Date'])
            platform_data[platform]['followers'].append(entry['ArtistFollower'])
        
        # Create traces for each platform
        traces = []
        colors = {
            'instagram': 'rgb(253, 101, 45)',
            'tiktok': 'rgb(0, 153, 204)',
            'youtube': 'rgb(255, 0, 0)',
            'soundcloud': 'rgb(205, 60, 0)'
        }
        
        for platform, values in platform_data.items():
            trace = go.Scatter(
                x=values['dates'],
                y=values['followers'],
                mode='lines',
                name=platform,
                marker=dict(color=colors.get(platform, 'rgb(0, 0, 0)'))  # Default color if not in colors dict
            )
            traces.append(trace)
        
        # Define the layout for the line chart
        self.plot_audience_follower.data = traces
        self.plot_audience_follower.layout = {
            'template': 'plotly_dark',
            'title': {
                'text': 'Social Media Followers over time',
                'x': 0.5,
                'xanchor': 'center'
            },
            'yaxis': {
                'title': 'Followers',
                'range': [0, 1.1 * max(itertools.chain(*[v['followers'] for v in platform_data.values()]))]
            },
            'paper_bgcolor': 'rgb(40, 40, 40)',
            'plot_bgcolor': 'rgb(40, 40, 40)'
        }
        
      else:
        self.plot_audience_follower.visible = False
        self.no_audience_follower.visible = True
      
      
      # -------------------------------
      # IV. MUSICAL
      # a) musical distance
      if sug["MinMusDist"] == 'None': mmd = 'N/A'
      else: mmd = "{:.2f}".format(round(float(sug["MinMusDist"]),2))
      self.min_mus_dis.text = mmd
      if sug["AvgMusDist"] == 'None': amd = 'N/A'
      else: amd = "{:.2f}".format(round(float(sug["AvgMusDist"]),2))
      self.avg_mus_dis.text = amd
      if sug["MaxMusDist"] == 'None': xmd = 'N/A'
      else: xmd = "{:.2f}".format(round(float(sug["MaxMusDist"]),2))
      self.max_mus_dis.text = xmd
      
      # b) musical features
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
      
      
      # -------------------------------
      # FOOTER:
      # Spotify Web-Player
      self.c_web_player.html = '<iframe style="border-radius:12px" src="https://open.spotify.com/embed/artist/' + sug["SpotifyArtistID"] + '?utm_source=generator&theme=0&autoplay=true" width="100%" height="80" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'

  
  # -------------------------------
  # INFO CLICK  
  def info_click(self, **event_args):
    if self.info.icon == 'fa:angle-down':
      self.info.icon = 'fa:angle-up'
      self.info.icon_align = 'left_edge'
      self.info.text = 'This is your artist dashboard - showing everything you need to know about the artist recommended just for you by our AI. Rate the artist, and our algorithm will continue to learn what you like and appreciate in artists - be it their music style, their origin or label status. If you want to narrow it down manually, use the filters!'
    else:
      self.info.icon = 'fa:angle-down'
      self.info.icon_align = 'left'
      self.info.text = 'Info'

  # -------------------------------
  # BIO CLICK
  def bio_click(self, **event_args):
    sug = json.loads(anvil.server.call('get_suggestion', 'Inspect', self.model_id, temp_artist_id_global)) # Free, Explore, Inspect, Dissect
    if sug["Countries"] == "None":
      source = None
      countryname = None
    else:
      country = json.loads(sug["Countries"])
      countryname = country["CountryName"]
      source = "https://flagcdn.com/w40/" + country["CountryCode"].lower() + ".png"
    country_flag = Image(source=source, spacing_below=0, spacing_above=0)
    custom_alert_form = CustomAlertForm(
      text=self.biography, 
      pickurl=sug["ArtistPictureURL"], 
      artist_name=sug["Name"], 
      countryflag=country_flag, 
      countryname=countryname
    )
    alert(content=custom_alert_form, large=True, buttons=[])

  
  # def text_box_search_pressed_enter(self, **event_args):
  #   search_text = self.text_box_search.text
  #   popup_table = alert(
  #     content=C_RelatedPopupTable(self.model_id, search_text),
  #     large=True,
  #     buttons=[]
  #   )

  
  # -------------------------------
  # WATCHLIST  
  def link_watchlist_name_click(self, **event_args):
    name = self.Artist_Name_Details.get_components()
    name = name[0].text
    if self.link_watchlist_name.icon == 'fa:star':
      self.link_watchlist_name.icon = 'fa:star-o'
      self.link_watchlist_name2.icon = 'fa:star-o'
      self.update_watchlist_lead(artist_id, False, None, False)
      Notification("",
        title=f"{name} removed from the watchlist!",
        style="success").show()
    else:
      self.link_watchlist_name.icon = 'fa:star'
      self.link_watchlist_name2.icon = 'fa:star'
      self.update_watchlist_lead(artist_id, True, 'Action required', True)
      Notification("",
        title=f"{name} added to the watchlist!",
        style="success").show()

  def update_watchlist_lead(self, artist_id, watchlist, status, notification, **event_args):
    anvil.server.call('update_watchlist_lead', self.model_id, artist_id, watchlist, status, notification)
    self.parent.parent.update_no_notifications()
  
  # -------------------------------
  # SECTION NAVIGATION
  def nav_releases_click(self, **event_args):
    self.nav_releases.role = 'table_content_small_orange_underlined'
    self.nav_success.role = 'table_content_small'
    self.nav_fandom.role = 'table_content_small'
    self.nav_musical.role = 'table_content_small'
    self.sec_releases.visible = True
    self.sec_success.visible = False
    self.sec_fandom.visible = False
    self.sec_musical.visible = False
  
  def nav_success_click(self, **event_args):
    self.nav_releases.role = 'table_content_small'
    self.nav_success.role = 'table_content_small_orange_underlined'
    self.nav_fandom.role = 'table_content_small'
    self.nav_musical.role = 'table_content_small'
    self.sec_releases.visible = False
    self.sec_success.visible = True
    self.sec_fandom.visible = False
    self.sec_musical.visible = False

  def nav_fandom_click(self, **event_args):
    self.nav_releases.role = 'table_content_small'
    self.nav_success.role = 'table_content_small'
    self.nav_fandom.role = 'table_content_small_orange_underlined'
    self.nav_musical.role = 'table_content_small'
    self.sec_releases.visible = False
    self.sec_success.visible = False
    self.sec_fandom.visible = True
    self.sec_musical.visible = False
    
  def nav_musical_click(self, **event_args):
    self.nav_releases.role = 'table_content_small'
    self.nav_success.role = 'table_content_small'
    self.nav_fandom.role = 'table_content_small'
    self.nav_musical.role = 'table_content_small_orange_underlined'
    self.sec_releases.visible = False
    self.sec_success.visible = False
    self.sec_fandom.visible = False
    self.sec_musical.visible = True

  # -------------------------------
  # RATING BUTTONS
  def button_1_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], self.model_id, artist_id, 1, False, '')
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_2_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], self.model_id, artist_id, 2, False, '')
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_3_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], self.model_id, artist_id, 3, False, '')
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_4_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], self.model_id, artist_id, 4, False, '')
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_5_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], self.model_id, artist_id, 5, False, '')
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_6_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], self.model_id, artist_id, 6, False, '')
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)

  def button_7_click(self, **event_args):
    anvil.server.call('add_interest', user["user_id"], self.model_id, artist_id, 7, False, '')
    self.header.scroll_into_view(smooth=True)
    self.refresh_sug(temp_artist_id=None)
  
  # -------------------------------
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

  def button_set_filters_click(self, **event_args):
    open_form('Main_In', model_id=self.model_id, temp_artist_id=None, target='C_Filter', value=None)

  def button_remove_filters_click(self, **event_args):
    anvil.server.call('change_filters', self.model_id, filters_json = None)
    open_form('Main_In', model_id=self.model_id, temp_artist_id=None, target='C_Discover', value=None)



  

  
