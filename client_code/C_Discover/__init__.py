from ._anvil_designer import C_DiscoverTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
from collections import defaultdict
import itertools
from ..C_CustomAlertForm import C_CustomAlertForm  # Import the custom form
from ..C_ProgressMessage import C_ProgressMessage
from anvil import js
import anvil.js
import anvil.js.window
from anvil.js.window import document, updateGauge, playSpotify, autoPlaySpotify

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var, save_var
import time


class C_Discover(C_DiscoverTemplate):
  def __init__(self, url_artist_id, **properties):
    # print(f"{datetime.now()}: Discover - __init__ - 1", flush=True)

    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.html = "@theme:C_Discover.html"
    self.add_event_handler("show", self.form_show)

    global user
    user = anvil.users.get_user()
    print(f"Discover user: {user}")
    print(f"Discover user_id: {load_var('user_id')}")

    self.url_artist_id = url_artist_id
    
    # Any code you write here will run before the form opens.
    if user is None or user == "None":
      if load_var("user_id") is None:
        open_form("Main_Out")
        # open_form('Main_Out_New')
      else:
        self.user_id = load_var("user_id")
        self.refresh_sug()

    elif (
      user["expiration_date"] is not None
      and (datetime.today().date() - user["expiration_date"]).days > 0
    ):
      routing.set_url_hash("no_subs", load_from_cache=False)
      get_open_form().SearchBar.visible = False

    else:
      self.user_id = user["user_id"]
      self.refresh_sug()
      self.column_panel_header.scroll_into_view(smooth=True)

  
  # -------------------------------------------
  # SUGGESTIONS
  def refresh_sug(self, **event_args):
    self.column_panel_header.scroll_into_view(smooth=True)

    # begin = datetime.now()
    # print(f"{datetime.now()}: Discover - __init__ - 2", flush=True)
    # print(f"{datetime.now()}: Discover - __init__ - 3", flush=True)
    # print(f"TotalTime Discover: {datetime.now() - begin}", flush=True)

    self.spacer_bottom_margin.height = 80
    self.Artist_Name_Details.clear()
    self.Artist_Name_Details_Sidebar.clear()
    self.flow_panel_genre_tile.clear()
    self.flow_panel_social_media_tile.clear()
    # self.spotify_player_spot.clear()
    # self.column_panel_1.clear()

    # model_id
    model_id = load_var("model_id")
    if model_id is None:
      save_var("model_id", anvil.server.call("get_model_id", self.user_id))
    print(f"Discover model_id: {model_id}")
    self.model_id = model_id

    # watchlist_id
    watchlist_id = load_var("watchlist_id")
    if watchlist_id is None:
      save_var("watchlist_id", anvil.server.call("get_watchlist_id", self.user_id))
    print(f"Discover watchlist_id: {watchlist_id}")
    self.watchlist_id = watchlist_id

    # get_suggestion
    # url_artist_id = self.url_dict["artist_id"]
    # url_artist_id = 107650  # ATTENTION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    sug = json.loads(
      anvil.server.call("get_suggestion", "Inspect", self.model_id, self.url_artist_id)
    )  # Free, Explore, Inspect, Dissect
    self.sug = sug
    save_var("lastplayed", self.sug["SpotifyArtistID"])

    # check status
    if sug["Status"] == "Empty Model!":
      alert(
        title="Train you Model..",
        content="Sorry, we cound't find any artists for your model. Make sure your model is fully set up!\n\nTherefore, go to ADD REF. ARTISTS and add some starting artists that you are interested in.",
      )
      self.visible = False

    elif sug["Status"] == "No Findings!":
      result = alert(
        title="No Artists found..",
        content="Sorry, we cound't find any artists for your model. Please check two potential issues:\n\n1. Please check your FILTERS and change them to find additional artists.\n\n2. If you're just setting up your model or are subscribed to the Explore subscription, go to the ADD REF. ARTISTS page and add additional reference artists.",
        buttons=[("Change Filters", "FILTERS"), ("Ok", "OK")],
      )
      self.visible = False
      if result == "FILTERS":
        click_button(
          f"model_profile?model_id={self.model_id}&section=Filter", event_args
        )

    # elif sug["Status"] == 'Free Limit Reached!':
    #   alert(title='Free Limit Reached..',
    #     content="Sorry, the free version is limited in the number of suggested artists - if you're interested in continuing, please upgrade to one of our subscription plans.\n\nFor any questions, please contact us at info@aidar.ai\n\nYour AIDAR Team")
    #   self.visible = False

    else:
      self.nav_releases.role = "section_buttons_focused"
      self.sec_releases.visible = True
      self.sec_success.visible = False
      self.sec_fandom.visible = False
      self.sec_musical.visible = False

      artist_id = int(sug["ArtistID"])
      self.artist_id = artist_id

      if self.watchlist_id is None:
        watchlist_presence = "False"
      else:
        watchlist_presence = anvil.server.call(
          "check_watchlist_presence", self.watchlist_id, artist_id
        )

      # -------------------------------
      # NOTES
      self.get_watchlist_notes(artist_id)
      self.get_watchlist_details(artist_id)

      # -------------------------------
      # ARTIST HEADER
      # picture and its link
      if sug["ArtistPictureURL"] != "None":
        self.artist_image.source = sug["ArtistPictureURL"]
      else:
        self.artist_image.source = "_/theme/pics/Favicon_orange.JPG"

      if sug["ArtistURL"] != "None":
        self.artist_link.url = sug["ArtistURL"]

      # --------
      # watchlist
      # if watchlist_presence == "True":
      #   self.link_watchlist_name.icon = "fa:star"
      #   # self.link_watchlist_name2.icon = "fa:star"
      #   self.parent.parent.parent.parent.link_watchlist_name2.icon = "fa:star"
      # else:
      #   self.link_watchlist_name.icon = "fa:star-o"
      #   # self.link_watchlist_name2.icon = "fa:star-o"        
      #   self.parent.parent.parent.parent.link_watchlist_name2.icon = "fa:star-o"

      # --------
      # name
      artist_name_component = Label(
        text=sug["Name"], role="artist-name-tile", spacing_above=0, spacing_below=0
      )
      self.Artist_Name_Details.add_component(artist_name_component)
      artist_name_component_sidebar = Label(
        text=sug["Name"], role="artist-name-tile", spacing_above=0, spacing_below=0
      )
      self.Artist_Name_Details_Sidebar.add_component(artist_name_component_sidebar)

      # --------
      # genres
      if sug["Genres"] == "None":
        pass
      else:
        genres_string = sug["Genres"]
        # Clean up the string and convert to list
        genres_string_cleaned = genres_string.strip("[]").replace("'", "")
        genres_list = [genre.strip() for genre in genres_string_cleaned.split(",")]
        # Add Genres to FlowPanel
        for genre in genres_list:
          genre_label = Label(text=genre)
          genre_label.role = "genre-box"
          self.flow_panel_genre_tile.add_component(genre_label)

      # --------
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
        "TikTok": "fab:tiktok",
      }

      if sug["Platforms"] == "None":
        self.social_media_link.visible = False
      else:
        social_media_list = json.loads(sug["Platforms"])
        for i in range(0, len(social_media_list)):
          found = False

          if social_media_list[i]["platform"] in platform_dict:
            found = True
            social_media_link = Link(
              icon=platform_dict[social_media_list[i]["platform"]]
            )
            social_media_link.role = "music-icons-tile"

          if found is True:
            # social_media_link.role = 'genre-box'
            social_media_link.url = social_media_list[i]["platform_url"]
            self.flow_panel_social_media_tile.add_component(social_media_link)

      # --------
      # origin
      if sug["Countries"] == "None":
        pass
      else:
        country = json.loads(sug["Countries"])
        country_flag = Image(
          source="https://flagcdn.com/w40/" + country["CountryCode"].lower() + ".png",
          spacing_below=0,
          spacing_above=0,
        )
        country_flag.role = "country-flag-icon"
        country_flag.tooltip = country["CountryName"]
        self.Artist_Name_Details.add_component(country_flag)

      # --------
      # birt date
      if sug["BirthDate"] == "None":
        self.birthday.visible = False
      else:
        self.birthday.visible = True
        self.birthday.text = sug["BirthDate"]

      # --------
      # gender
      if sug["Gender"] == "None":
        self.gender.visible = False
      else:
        self.gender.visible = True
        self.gender.text = sug["Gender"]

      # --------
      # line condition
      if sug["BirthDate"] != "None" and sug["Gender"] != "None":
        self.gender_birthday_line.visible = True
      else:
        self.gender_birthday_line.visible = False

      # --------
      # KPI_tile_1: prediction_size
      if sug["prediction_size"] == "None":
        self.KPI_tile_1.text = "-"
      else:
        self.KPI_tile_1.text = (
          "{:.0f}".format(round(float(sug["prediction_size"]) / 7 * 100, 0)) + "%"
        )

      # KPI_tile_2: prediction_rel
      if sug["prediction_rel"] == "None":
        self.KPI_tile_2.text = "-"
      else:
        self.KPI_tile_2.text = (
          "{:.0f}".format(round(float(sug["prediction_rel"]) / 7 * 100, 0)) + "%"
        )

      # KPI_tile_3: prediction_musical // ATTENTION !!! musical not active yet
      if sug["prediction_rel"] == "None":
        self.KPI_tile_3.text = "-"
      else:
        self.KPI_tile_3.text = (
          "{:.0f}".format(round(float(sug["prediction_rel"]) / 7 * 100, 0)) + "%"
        )

      # KPI_tile_4: prediction_growth
      if sug["prediction_growth"] == "None":
        self.KPI_tile_4.text = "-"
      else:
        self.KPI_tile_4.text = (
          "{:.0f}".format(round(float(sug["prediction_growth"]) / 7 * 100, 0)) + "%"
        )

      # --------
      # prediction
      if (str(sug["Prediction"]) == "nan") or (str(sug["Prediction"]) == "None"):
        self.column_panel_1.visible = False
        self.linear_panel_2.visible = True
        self.no_prediction.visible = True
        self.pred = None
      else:
        if float(sug["Prediction"]) > 7:
          self.pred = "100%"
        elif float(sug["Prediction"]) < 0:
          self.pred = "0%"
        else:
          self.pred = "{:.2f}".format(round(float(sug["Prediction"]) / 7 * 100, 0))
        self.linear_panel_2.visible = False
        self.no_prediction.visible = False
      self.custom_HTML_prediction()
      # self.spotify_HTML_player()

      # --------
      # biography
      biography = sug["Biography"]
      if biography != "None":
        if len(biography) >= 200:
          self.bio_text.content = f"{biography[0:200]}..."
          self.bio.visible = True
        else:
          self.bio_text.content = biography
          self.bio.visible = False
      else:
        self.bio.visible = False

      # --------
      # KPI_1: fcg.ev_sp_fol_30, fcg.ev_sp_li_30, fcg.ev_tt_fol_30
      if sug["ArtistFollower_lat"] == "None":
        self.KPI_1.content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255); padding-left: 10px;">-</span>"""
      else:
        self.KPI_1.content = f"""<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255); padding-left: 10px;">{get_open_form().shorten_number(sug["ArtistFollower_lat"])}</span>"""

        if sug["ev_sp_fol_30"] != "None":
          val = int("{:.0f}".format(round(float(sug["ev_sp_fol_30"]) * 100, 0)))
          if val >= 3:
            ev = f"""+{val}%"""
            "{:.0f}".format(round(float(sug["ev_sp_fol_30"]) * 100, 0))
            col = "green"
          elif val < 0:
            ev = f"""{val}%"""
            col = "red"
          else:
            ev = f"""+{val}%"""
            col = "grey"

          self.KPI_1.content = (
            self.KPI_1.content
            + f"""<span style="font-size: 16px; color: {col};">  {ev}</span>"""
          )

      # -------------------------------
      # I. RELEASES
      # a) stats
      if sug["NoTracks"] == "None":
        self.no_tracks.text = "-"
      else:
        self.no_tracks.text = f'{int(sug["NoTracks"]):,}'

      if sug["FirstReleaseDate"] == "None":
        self.first_release_date.text = "-"
      else:
        self.first_release_date.text = sug["FirstReleaseDate"]

      if sug["LastReleaseDate"] == "None":
        self.last_release_date.text = "-"
      else:
        self.last_release_date.text = sug["LastReleaseDate"]

      if sug["LatestLabel"] == "None":
        ll = "N/A"
      else:
        ll = sug["LatestLabel"]
      self.latest_label.text = ll

      if sug["MajorCoop"] == "1":
        mc = "yes"
      elif sug["MajorCoop"] == "0":
        mc = "no"
      else:
        mc = "-"
      self.major_coop.text = mc

      if sug["SubMajorCoop"] == "1":
        smc = "yes"
      elif sug["SubMajorCoop"] == "0":
        smc = "no"
      else:
        smc = "-"
      self.sub_major_coop.text = smc

      co_artists = json.loads(anvil.server.call("get_co_artists", artist_id))
      if co_artists == []:
        self.co_artists_avg.text = "0"
      else:
        self.co_artists_avg.text = "{:.2f}".format(
          round(co_artists[0]["avg_co_artists_per_track"], 2)
        )

      # --------
      # b) release tables
      if self.data_grid_releases.visible is True:
        self.data_grid_releases_data.items = json.loads(
          anvil.server.call("get_dev_releases", artist_id)
        )

      # --------
      # c) release cycle
      if self.data_grid_cycle.visible is True:
        self.data_grid_cycle_data.items = anvil.server.call(
          "get_release_cycle", artist_id
        )

      # --------
      # d) release timing
      data = json.loads(anvil.server.call("get_dev_releases", artist_id))
      self.create_release_timing_scatter_chart(data=data)

      # --------
      # e) labels freq
      # Set items for the dropdown
      self.sort_dropdown.items = [
        # ("Sort", "Sort"), # Placeholder option
        ("A-Z", "alpha"),
        ("Z-A", "reverse_alpha"),
        ("Highest First", "high_num"),
        ("Lowest First", "low_num"),
      ]
      self.sort_dropdown.selected_value = "high_num"
      self.sort_dropdown.role = "sort-dropdown"
      self.drop_down_wl.role = "sort-dropdown-footer"
      self.drop_down_model.role = "sort-dropdown-footer"
      self.sort_dropdown_countries.role = "sort-dropdown"

      # Add event handler for the dropdown
      self.sort_dropdown.set_event_handler("change", self.sort_data)

      # Load the data when the form is initialized
      labels_freq = json.loads(anvil.server.call("get_labels_freq", artist_id))
      if labels_freq != []:
        labels = [x["LabelName"] for x in labels_freq]
        cooperations = [x["NoLabels"] for x in labels_freq]
        self.bar_data = {"labels": labels, "cooperations": cooperations}

        self.Most_Frequent_Labels_Graph.visible = True
        self.No_Most_Frequent_Labels_Graph.visible = False

        self.apply_default_sorting()

      else:
        self.Most_Frequent_Labels_Graph.visible = False
        self.No_Most_Frequent_Labels_Graph.visible = True

      # --------
      # f) co-artists by frequency
      if self.data_grid_co_artists_freq.visible is True:
        self.data_grid_co_artists_freq_data.items = co_artists

      # --------
      # g) co-artists by popularity
      if self.data_grid_co_artists_pop.visible is True:
        self.data_grid_co_artists_pop_data.items = sorted(
          co_artists,
          key=lambda x: float(x["ArtistPopularity_lat"])
          if x["ArtistPopularity_lat"] not in [None, ""]
          else 0.0,
          reverse=True,
        )

      # --------
      # h) related artists table
      if self.data_grid_related_artists.visible is True:
        self.data_grid_related_artists_data.items = json.loads(
          anvil.server.call("get_dev_related_artists", artist_id, int(self.model_id))
        )

      # -------------------------------
      # II. SUCCESS
      # Load data
      dev_successes = json.loads(anvil.server.call("get_dev_successes", artist_id))
      dates = [x["Date"] for x in dev_successes]
      artist_popularity = [x["ArtistPopularity"] for x in dev_successes]
      artist_followers = [x["ArtistFollower"] for x in dev_successes]
      self.scatter_data = {
        "dates": dates,
        "artist_popularity": artist_popularity,
        "artist_followers": artist_followers,
      }

      # --------
      # a) Popularity
      if sug["ArtistPopularity_lat"] == "None":
        self.sp_pop_lat.text = "-"
      else:
        self.sp_pop_lat.text = sug["ArtistPopularity_lat"]
        self.create_artist_popularity_scatter_chart()

      # --------
      # b) Followers
      if sug["ArtistFollower_lat"] == "None":
        self.sp_fol_lat.text = "-"
      else:
        self.sp_fol_lat.text = f'{int(sug["ArtistFollower_lat"]):,}'
        self.create_artist_followers_scatter_chart()

      # --------
      # II. SUCCESS - c) Stats
      ev_dict = {
        "dev1": (
          "dev1_t0",
          'sug["ArtistPopularity_lat"]',
          "dev1_t7",
          'int(sug["ArtistPopularity_lat"]) / (float(sug["ev_sp_pop_7"])+1)',
          'sug["ev_sp_pop_7"]',
          "dev1_t30",
          'int(sug["ArtistPopularity_lat"]) / (float(sug["ev_sp_pop_30"])+1)',
          'sug["ev_sp_pop_30"]',
        ),
        "dev2": (
          "dev2_t0",
          'sug["ArtistFollower_lat"]',
          "dev2_t7",
          'int(sug["ArtistFollower_lat"]) / (float(sug["ev_sp_fol_7"])+1)',
          'sug["ev_sp_fol_7"]',
          "dev2_t30",
          'int(sug["ArtistFollower_lat"]) / (float(sug["ev_sp_fol_30"])+1)',
          'sug["ev_sp_fol_30"]',
        ),
        "dev3": (
          "dev3_t0",
          'sug["SpotifyMtlListeners_lat"]',
          "dev3_t7",
          'int(sug["SpotifyMtlListeners_lat"]) / (float(sug["ev_sp_li_7"])+1)',
          'sug["ev_sp_li_7"]',
          "dev3_t30",
          'int(sug["SpotifyMtlListeners_lat"]) / (float(sug["ev_sp_li_30"])+1)',
          'sug["ev_sp_li_30"]',
        ),
      }

      for dev in ["dev1", "dev2", "dev3"]:
        cont = False
        if dev == "dev1" and sug["ArtistPopularity_lat"] != "None":
          cont = True
        elif dev == "dev2" and sug["ArtistFollower_lat"] != "None":
          cont = True
        elif dev == "dev3" and sug["SpotifyMtlListeners_lat"] != "None":
          cont = True
        elif dev == "dev4" and sug["TikTokFollower_lat"] != "None":
          cont = True

        lab_0, val_0, lab_7, val_7, ev_7, lab_30, val_30, ev_30 = ev_dict[dev]

        if cont is False:
          getattr(
            self, lab_0
          ).content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">-</span>"""
          getattr(
            self, lab_7
          ).content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">-</span>"""
          getattr(
            self, lab_30
          ).content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">-</span>"""
        else:
          val_0 = eval(val_0, {"sug": sug})
          ev_7 = eval(ev_7, {"sug": sug})
          ev_30 = eval(ev_30, {"sug": sug})

          # t0:
          getattr(
            self, lab_0
          ).content = f"""<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">{get_open_form().shorten_number(val_0)}</span>"""

          # t7
          if ev_7 != "None":
            val_7 = eval(val_7, {"sug": sug})
            getattr(
              self, lab_7
            ).content = f"""<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">{get_open_form().shorten_number(val_7)}</span>"""
            val = int("{:.0f}".format(round(float(ev_7) * 100, 0)))
            if val >= 3:
              ev = f"""+{val}%"""
              "{:.0f}".format(round(float(ev_7) * 100, 0))
              col = "green"
            elif val < 0:
              ev = f"""{val}%"""
              col = "red"
            else:
              ev = f"""+{val}%"""
              col = "grey"
            getattr(self, lab_7).content = (
              getattr(self, lab_7).content
              + f"""<span style="font-size: 16px; color: {col};">  {ev}</span>"""
            )
          else:
            getattr(
              self, lab_7
            ).content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">-</span>"""

          # t30
          if ev_30 != "None":
            val_30 = eval(val_30, {"sug": sug})
            getattr(
              self, lab_30
            ).content = f"""<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">{get_open_form().shorten_number(val_30)}</span>"""
            val = int("{:.0f}".format(round(float(ev_30) * 100, 0)))
            if val >= 3:
              ev = f"""+{val}%"""
              "{:.0f}".format(round(float(ev_30) * 100, 0))
              col = "green"
            elif val < 0:
              ev = f"""{val}%"""
              col = "red"
            else:
              ev = f"""+{val}%"""
              col = "grey"
            getattr(self, lab_30).content = (
              getattr(self, lab_30).content
              + f"""<span style="font-size: 16px; color: {col};">  {ev}</span>"""
            )
          else:
            getattr(
              self, lab_30
            ).content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">-</span>"""

      # -------------------------------
      # III. FANDOM
      # a) mtl. listeners
      # Load data for the Scatter plot (Spotify Monthly Listeners)
      monthly_listeners_data = json.loads(
        anvil.server.call("get_mtl_listeners", artist_id)
      )

      if monthly_listeners_data != []:
        sp_mtl_lis_lat = monthly_listeners_data[-1]["MtlListeners"]

        # KPI_2
        self.KPI_2.content = f"""<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255); padding-left: 10px;">{get_open_form().shorten_number(sp_mtl_lis_lat)}</span>"""
        if sug["ev_sp_li_30"] != "None":
          val = int("{:.0f}".format(round(float(sug["ev_sp_li_30"]) * 100, 0)))
          if val >= 3:
            ev = f"""+{val}%"""
            "{:.0f}".format(round(float(sug["ev_sp_li_30"]) * 100, 0))
            col = "green"
          elif val < 0:
            ev = f"""{val}%"""
            col = "red"
          else:
            ev = f"""+{val}%"""
            col = "grey"
          self.KPI_2.content = (
            self.KPI_2.content
            + f"""<span style="font-size: 16px; color: {col};">  {ev}</span>"""
          )

        # other
        self.sp_mtl_listeners.text = f"{int(sp_mtl_lis_lat):,}"

        dates = [x["Date"] for x in monthly_listeners_data]
        monthly_listeners = [x["MtlListeners"] for x in monthly_listeners_data]
        self.listeners_data = {"dates": dates, "monthly_listeners": monthly_listeners}

        self.Spotify_Monthly_Listeners_Graph.visible = True
        self.No_Spotify_Monthly_Listeners_Graph.visible = False

        self.create_artist_monthly_listeners_scatter_chart()

      else:
        self.KPI_2.content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255); padding-left: 10px;">-</span>"""
        self.sp_mtl_listeners.text = "-"
        self.Spotify_Monthly_Listeners_Graph.visible = False
        self.No_Spotify_Monthly_Listeners_Graph.visible = True

      # --------
      # b) mtl. listeners country
      # Load data for the Scatter plot (Spotify Monthly Listeners by Country)
      monthly_listeners_country_data = json.loads(
        anvil.server.call("get_mtl_listeners_country", artist_id)
      )

      if monthly_listeners_country_data != []:
        self.audience_country.text = monthly_listeners_country_data[0]["CountryName"]

        country_codes = [x["CountryCode"] for x in monthly_listeners_country_data]
        country_name = [x["CountryName"] for x in monthly_listeners_country_data]
        monthly_listeners = [x["MtlListeners"] for x in monthly_listeners_country_data]
        self.listeners_country_data = {
          "country_codes": country_codes,
          "monthly_listeners": monthly_listeners,
          "country_name": country_name,
        }
        self.Spotify_Monthly_Listeners_by_Country_Graph.visible = True
        self.flow_panel_countries.visible = True
        self.No_Spotify_Monthly_Listeners_by_Country_Graph.visible = False

        self.create_monthly_listeners_by_country_bar_chart()

      else:
        self.audience_country.text = "-"
        self.Spotify_Monthly_Listeners_by_Country_Graph.visible = False
        self.flow_panel_countries.visible = False
        self.No_Spotify_Monthly_Listeners_by_Country_Graph.visible = True

      # --------
      # c) mtl. listeners city
      monthly_listeners_city_data = json.loads(
        anvil.server.call("get_mtl_listeners_city", artist_id)
      )

      if monthly_listeners_city_data != []:
        self.audience_city.text = monthly_listeners_city_data[0]["CityWithCountryCode"]

        city_w_country_code = [
          x["CityWithCountryCode"] for x in monthly_listeners_city_data
        ]
        monthly_listeners = [x["MtlListeners"] for x in monthly_listeners_city_data]
        country_name_city = [x["CountryName"] for x in monthly_listeners_city_data]
        self.listeners_city_data = {
          "city_w_country_code": city_w_country_code,
          "monthly_listeners": monthly_listeners,
          "country_name_city": country_name_city,
        }
        self.Spotify_Monthly_Listeners_by_City_Graph.visible = True
        self.No_Spotify_Monthly_Listeners_by_City_Graph.visible = False
        self.create_monthly_listeners_by_city_bar_chart()

      else:
        self.Spotify_Monthly_Listeners_by_City_Graph.visible = False
        self.No_Spotify_Monthly_Listeners_by_City_Graph.visible = True

      # --------
      # d) Social Media followers
      audience_follower = json.loads(
        anvil.server.call("get_audience_follower2", artist_id)
      )

      if audience_follower != []:
        # Initialize a dictionary to hold data for each platform
        self.no_social_media.visible = False
        platform_data = defaultdict(lambda: {"dates": [], "followers": []})

        # Populate the dictionary with data
        for entry in audience_follower:
          platform = entry["Platform"]
          platform_data[platform]["dates"].append(entry["Date"])
          platform_data[platform]["followers"].append(entry["ArtistFollower"])

        if platform_data["tiktok"]["dates"] != []:
          tiktok_fol_lat = platform_data["tiktok"]["followers"][-1]

          # KPI_3
          self.KPI_3.content = f"""<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255); padding-left: 10px;">{get_open_form().shorten_number(tiktok_fol_lat)}</span>"""
          if sug["ev_tt_fol_30"] != "None":
            val = int("{:.0f}".format(round(float(sug["ev_tt_fol_30"]) * 100, 0)))
            if val >= 3:
              ev = f"""+{val}%"""
              "{:.0f}".format(round(float(sug["ev_tt_fol_30"]) * 100, 0))
              col = "green"
            elif val < 0:
              ev = f"""{val}%"""
              col = "red"
            else:
              ev = f"""+{val}%"""
              col = "grey"
            self.KPI_3.content = (
              self.KPI_3.content
              + f"""<span style="font-size: 16px; color: {col};">  {ev}</span>"""
            )

          # other
          self.tiktok_follower.text = f"{int(tiktok_fol_lat):,}"
        else:
          self.KPI_3.content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255); padding-left: 10px;">-</span>"""

        if platform_data["soundcloud"]["dates"] != []:
          soundcloud_fol_lat = platform_data["soundcloud"]["followers"][-1]
          self.soundcloud_follower.text = f"{int(soundcloud_fol_lat):,}"

        def create_social_media_followers_chart(data, platform, color):
          # Format the text for the bar annotations
          formatted_text = [
            f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.1f}K" if x >= 1e3 else str(x)
            for x in data["followers"]
          ]

          fig = go.Figure(
            data=(
              go.Scatter(
                x=data["dates"],
                y=data["followers"],
                mode="lines",
                name=platform.capitalize(),
                line=dict(color=color),
                text=formatted_text,
                hoverinfo="none",
                hovertext=data["dates"],
                hovertemplate="Platform: "
                + platform
                + "<br>Followers: %{text}<br>Date: %{x}<extra></extra>",
              )
            )
          )

          fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=50),
            xaxis=dict(
              showgrid=False  # Remove x-axis gridlines
            ),
            yaxis=dict(
              shogrid=True,
              gridcolor="rgb(175,175,175)",  # Color of the gridlines
              gridwidth=0.1,  # Thickness of the gridlines
              griddash="dash",  # Dash style of the gridlines
            ),
            hoverlabel=dict(
              bgcolor="rgba(250, 250, 250, 0.1)",  # Background color of the hover label
            ),
          )
          return fig

        # INSTAGRAM
        if platform_data["instagram"]["dates"]:
          self.instagram_chart.figure = create_social_media_followers_chart(
            platform_data["instagram"], "Instagram", "rgb(253, 101, 45)"
          )
          self.no_instagram.visible = False
        else:
          # self.instagram_chart.figure = None  # Handle the case when there's no data
          self.instagram_chart.visible = False
          self.no_instagram.visible = True

        # TIKTOK
        if platform_data["tiktok"]["dates"]:
          self.tiktok_chart.figure = create_social_media_followers_chart(
            platform_data["tiktok"], "TikTok", "rgb(0, 153, 204)"
          )
          self.no_tiktok.visible = False
        else:
          # self.tiktok_chart.figure = None  # Handle the case when there's no data
          self.tiktok_chart.visible = False
          self.no_tiktok.visible = True
          self.tiktok_follower.text = "-"

        # YOUTUBE
        if platform_data["youtube"]["dates"]:
          self.youtube_chart.figure = create_social_media_followers_chart(
            platform_data["youtube"], "YouTube", "rgb(255, 0, 0)"
          )
          self.no_youtube.visible = False
        else:
          # self.youtube_chart.figure = None  # Handle the case when there's no data
          self.youtube_chart.visible = False
          self.no_youtube.visible = True

        # SOUNDCLOUD
        if platform_data["soundcloud"]["dates"]:
          self.soundcloud_chart.figure = create_social_media_followers_chart(
            platform_data["soundcloud"], "SoundCloud", "rgb(205, 60, 0)"
          )
          self.no_soundcloud.visible = False
        else:
          # self.soundcloud_chart.figure = None  # Handle the case when there's no data
          self.soundcloud_chart.visible = False
          self.no_soundcloud.visible = True
          self.soundcloud_follower.text = "-"

      else:
        self.KPI_3.content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255); padding-left: 10px;">-</span>"""
        self.tiktok_follower.text = "-"
        self.soundcloud_follower.text = "-"
        self.no_social_media.visible = True

      # # -------------------------------
      # # IV. MUSICAL
      # a) musical features
      if sug["AvgDuration"] == "None":
        f1 = "-"
      else:
        f1 = "{:.0f}".format(round(float(sug["AvgDuration"]), 0))
      self.feature_1.text = f1 + " sec"
      if sug["AvgDanceability"] == "None":
        f2 = "-"
      else:
        f2 = "{:.0f}".format(round(float(sug["AvgDanceability"]) * 100, 0))
      self.feature_2.text = f2 + "%"
      if sug["AvgEnergy"] == "None":
        f3 = "-"
      else:
        f3 = "{:.0f}".format(round(float(sug["AvgEnergy"]) * 100, 0))
      self.feature_3.text = f3 + "%"

      tonleiter = [
        "C",
        "C#/Db",
        "D",
        "D#/Eb",
        "E",
        "F",
        "F#/Gb",
        "G",
        "G#/Ab",
        "A",
        "A#/Bb",
        "B",
      ]
      if sug["AvgKey"] == "None":
        f4 = "--"
      else:
        f4 = tonleiter[int(round(float(sug["AvgKey"]), 0))]
      self.feature_4.text = f4

      if sug["AvgLoudness"] == "None":
        f5 = "-"
      else:
        f5 = "{:.2f}".format(round(float(sug["AvgLoudness"]), 2))
      self.feature_5.text = f5 + " dB"
      if sug["AvgMode"] == "None":
        f6 = "-"
      else:
        f6 = "{:.0f}".format(round(float(sug["AvgMode"]) * 100, 0))
      self.feature_6.text = f6 + "% Major"
      if sug["AvgSpeechiness"] == "None":
        f7 = "-"
      else:
        f7 = "{:.0f}".format(round(float(sug["AvgSpeechiness"]) * 100, 0))
      self.feature_7.text = f7 + "%"
      if sug["AvgAcousticness"] == "None":
        f8 = "-"
      else:
        f8 = "{:.0f}".format(round(float(sug["AvgAcousticness"]) * 100, 0))
      self.feature_8.text = f8 + "%"
      if sug["AvgInstrumentalness"] == "None":
        f9 = "-"
      else:
        f9 = "{:.0f}".format(round(float(sug["AvgInstrumentalness"]) * 100, 0))
      self.feature_9.text = f9 + "%"
      if sug["AvgLiveness"] == "None":
        f10 = "-"
      else:
        f10 = "{:.0f}".format(round(float(sug["AvgLiveness"]) * 100, 0))
      self.feature_10.text = f10 + "%"
      if sug["AvgValence"] == "None":
        f11 = "-"
      else:
        f11 = "{:.0f}".format(round(float(sug["AvgValence"]) * 100, 0))
      self.feature_11.text = f11 + "%"
      if sug["AvgTempo"] == "None":
        f12 = "-"
      else:
        f12 = "{:.0f}".format(round(float(sug["AvgTempo"]), 0))
      self.feature_12.text = f12 + " bpm"

      # -------------------------------
      # FOOTER:
      # a) Spotify Web-Player
      # if load_var("autoPlayStatus") is not None:
      #   self.autoplay_button.icon = load_var("autoPlayStatus")
      #   if load_var("autoPlayStatus") == "fa:toggle-on":
      #     self.spotify_artist_button.icon = "fa:pause-circle"
      # --------
      # b) Filter Button visibility
      activefilters = anvil.server.call("check_filter_presence", self.model_id)
      if activefilters == "False":
        self.button_remove_filters.visible = False
      else:
        self.button_remove_filters.visible = True

      # --------
      # c) Watchlist Drop-Down
      if self.user_id is None:
        self.drop_down_wl.visible = False
      else:
        self.drop_down_wl.visible = True
        wl_data = json.loads(anvil.server.call("get_watchlist_ids", self.user_id))
        wl_name_last_used = [
          item["watchlist_name"] for item in wl_data if item["is_last_used"]
        ][0]
        self.drop_down_wl.selected_value = wl_name_last_used
        watchlist_names = [item["watchlist_name"] for item in wl_data]
        self.drop_down_wl.items = watchlist_names

      # --------
      # d) Models Drop-Down
      if self.user_id is None:
        self.drop_down_model.visible = False
      else:
        self.drop_down_model.visible = True
        model_data = json.loads(anvil.server.call("get_model_ids", self.user_id))
        model_name_last_used = [
          item["model_name"] for item in model_data if item["is_last_used"]
        ][0]
        self.drop_down_model.selected_value = model_name_last_used
        model_names = [item["model_name"] for item in model_data]
        self.drop_down_model.items = model_names

      # -------------------------------
      # MILESTONE ALERT
      total_ratings = sug["total_ratings"]
      if total_ratings == "10":
        self.show_milestone_alert(10)
      elif total_ratings == "25":
        self.show_milestone_alert(25)
      elif total_ratings == "50":
        self.show_milestone_alert(50)

    self.column_panel_header.scroll_into_view(smooth=True)

  # ----------------------------------------------
  def form_show(self, **event_args):
    # embed_iframe_element = document.getElementById("embed-iframe")
    # if embed_iframe_element:
    #   self.call_js("createOrUpdateSpotifyPlayer", anvil.js.get_dom_node(self), "artist", self.sug["SpotifyArtistID"])
    #   # self.call_js('playSpotify_2')
    # else:
    #   print("Embed iframe element not found. Will not initialize Spotify player.")
    pass

  def spotify_HTML_player(self):
    # c_web_player_html = """
    #   <div id="embed-iframe"></div>
    #   """
    # html_webplayer_panel = HtmlPanel(html=c_web_player_html)
    # self.spotify_player_spot.add_component(html_webplayer_panel)
    pass

  def custom_HTML_prediction(self):
    if self.pred:
      custom_html = f"""
      <li class="note-display" data-note="{self.pred}">
        <div class="circle">
          <svg width="140" height="140" class="circle__svg">
            <defs>
              <linearGradient id="grad1" x1="100%" y1="100%" x2="0%" y2="0%">
                <stop offset="0%" style="stop-color:#812675;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#E95F30;stop-opacity:1" />
              </linearGradient>
            </defs>
            <circle cx="70" cy="70" r="65" class="circle__progress circle__progress--path"></circle>
            <circle cx="70" cy="70" r="65" class="circle__progress circle__progress--fill" stroke="url(#grad1)"></circle>
          </svg>

          <div class="percent">
            <span class="percent__int">0.</span>
            <!-- <span class="percent__dec">00</span> -->
            <span class="label" style="font-size: 13px;">Fit Likelihood</span>
          </div>
        </div>

      </li>
      """
      html_panel = HtmlPanel(html=custom_html)
      self.column_panel_1.add_component(html_panel)
    else:
      print("NO SELF PRED?")

  def truncate_label(self, label):
    return label if len(label) <= 10 else label[:10] + "..."

  def create_bar_chart(self, labels=None, cooperations=None):
    if labels is None:
      labels = self.bar_data["labels"]
    if cooperations is None:
      cooperations = self.bar_data["cooperations"]

    truncated_labels = [self.truncate_label(label) for label in labels]

    # Creating the Bar Chart
    fig = go.Figure(
      data=(
        go.Bar(
          x=labels,
          y=cooperations,
          hoverinfo="none",
          hovertext=labels,
          hovertemplate="Label: %{hovertext}<br>Cooperations: %{y} <extra></extra>",
        )
      )
    )

    fig.update_layout(
      template="plotly_dark",
      plot_bgcolor="rgba(0,0,0,0)",
      paper_bgcolor="rgba(0,0,0,0)",
      xaxis=dict(
        tickvals=list(range(len(labels))),
        ticktext=truncated_labels,  # Display truncated labels on the x-axis
      ),
      yaxis=dict(
        gridcolor="rgb(175, 175,175)",  # Color of the gridlines
        gridwidth=0.7,  # Thickness of the gridlines
        griddash="dash",  # Dash style of the gridlines
        range=[0, max(cooperations) * 1.1],  # Adjust y-axis range to add extra space
        zerolinecolor="rgb(240,240,240)",  # Set the color of the zero line
      ),
      margin=dict(
        t=50  # Increase top margin to accommodate the labels
      ),
      hoverlabel=dict(bgcolor="rgba(237,139,82, 0.4)"),
    )
    # This is to style the bars
    for trace in fig.data:
      trace.update(
        # marker_color='rgb(240,229,252)',
        marker_color="rgb(237,139,82)",
        marker_line_color="rgb(237,139,82)",
        marker_line_width=0.5,
        opacity=0.9,
      )
    self.Most_Frequent_Labels_Graph.figure = fig

  def create_release_timing_scatter_chart(self, data):
    dates_str = [x["AlbumReleaseDate"] for x in data]
    tracks = [x["Title"] for x in data]
    labels = [x["LabelName"] for x in data]
    release = [0] * len(data)

    dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates_str]
    if len(dates) > 0:
      min_date = min(dates)
      # Substracting 50 days from the min date of the list of dates for visual purposes.
      date_before_min = min_date - timedelta(days=50)
      # Get today's date
      today = datetime.today().strftime("%Y-%m-%d")
      date_before_min = date_before_min.strftime("%Y-%m-%d")

      # Creating the Scatter Chart
      fig = go.Figure(
        data=(
          go.Scatter(
            x=dates,
            y=release,
            textposition="outside",
            hoverinfo="none",
            hovertext=[
              f"Date: {date.strftime('%Y-%m-%d')}<br>Track: {track}<br>Label: {label}"
              for date, track, label in zip(dates, tracks, labels)
            ],
            hovertemplate="%{hovertext}<extra></extra>",
            marker=dict(
              color="rgb(237,139,82)",  # Color of the markers
              size=15,  # Size of the markers
              line=dict(
                color="rgb(237,139,82)",  # Color of the marker borders
                width=2,  # Width of the marker borders
              ),
            ),
            mode="markers+text",  # Display both markers and text
          )
        )
      )
      fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50),
        xaxis=dict(
          showgrid=False,
          range=[date_before_min, today],  # Set x-axis range to end at today's date
        ),
        yaxis=dict(
          range=[0.02, -0.01],  # Limit the y-axis
          showticklabels=False,  # Hide the tick labels
          showline=False,  # Hide the axis line
          zeroline=True,  # Ensure the zero line is visible
          zerolinecolor="rgb(175,175,175)",  # Set the color of the zero line
          zerolinewidth=2,  # Optionally set the width of the zero line
          showgrid=False,  # Disable the grid lines
        ),
        hoverlabel=dict(bgcolor="rgba(237,139,82, 0.4)"),
      )
      for trace in fig.data:
        trace.update(
          marker_color="rgb(219,106,37)",
          marker_line_color="rgb(219,106,37)",
          marker_line_width=1,
          opacity=0.8,
        )

      self.Release_Timing_Graph.figure = fig

  def sort_dropdown_countries_change(self, **event_args):
    save_var("sort_dropdown_countries", self.sort_dropdown_countries.selected_value)
    self.create_monthly_listeners_by_country_bar_chart()
    self.create_monthly_listeners_by_city_bar_chart()

  def create_monthly_listeners_by_country_bar_chart(
    self,
    country_page=1,
    items_per_page=15,
    country_codes=None,
    monthly_listeners=None,
    country_name=None,
  ):
    if load_var("sort_dropdown_countries") is None:
      self.sort_dropdown_countries.selected_value = "All countries"
    else:
      self.sort_dropdown_countries.selected_value = load_var("sort_dropdown_countries")
    selected_country_name = self.sort_dropdown_countries.selected_value

    country_codes = self.listeners_country_data["country_codes"]
    monthly_listeners = self.listeners_country_data["monthly_listeners"]
    country_name = self.listeners_country_data["country_name"]

    # Calculate the range for the current page
    start_index = (country_page - 1) * items_per_page
    end_index = start_index + items_per_page

    # Slice the data for the current page
    country_code_page = country_codes[start_index:end_index]
    monthly_listeners_page = monthly_listeners[start_index:end_index]
    country_name_page = country_name[start_index:end_index]

    # Highlight the selected country
    bar_colors = [
      "rgba(237,139,82,1)"
      if name == selected_country_name or selected_country_name == "All countries"
      else "rgba(125,125,125,0.6)"
      for name in country_name_page
    ]

    # Format the text for the bar annotations
    formatted_text = [
      f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.1f}K" if x >= 1e3 else str(x)
      for x in monthly_listeners
    ]

    # Creating the Bar Chart
    fig = go.Figure(
      data=(
        go.Bar(
          x=country_code_page,
          y=monthly_listeners_page,
          text=formatted_text,
          textposition="none",
          hoverinfo="none",
          hovertext=country_name_page,
          hovertemplate="Country: %{hovertext}<br>Monthly Listeners: %{text} <extra></extra>",
        )
      )
    )

    fig.update_layout(
      template="plotly_dark",
      plot_bgcolor="rgba(0,0,0,0)",
      paper_bgcolor="rgba(0,0,0,0)",
      xaxis=dict(
        tickvals=list(range(len(country_codes))),
      ),
      yaxis=dict(
        gridcolor="rgb(175,175,175)",  # Color of the gridlines
        gridwidth=0.1,  # Thickness of the gridlines
        griddash="dash",  # Dash style of the gridlines
        range=[
          0,
          max(monthly_listeners) * 1.1,
        ],  # Adjust y-axis range to add extra space
        tickformat="~s",  # Format numbers with SI unit prefixes
        zerolinecolor="rgb(240,240,240)",  # Set the color of the zero line
      ),
      margin=dict(
        t=0,  # Top margin
        b=20,  # Bottom margin
      ),
      hoverlabel=dict(bgcolor="rgba(237,139,82, 0.4)"),
    )
    # This is to style the bars
    for trace in fig.data:
      trace.update(marker=dict(color=bar_colors), marker_line_width=0.1, opacity=0.9)
    self.Spotify_Monthly_Listeners_by_Country_Graph.figure = fig
    self.current_page = country_page
    self.total_pages = (len(country_codes) + items_per_page - 1) // items_per_page
    self.prev_button_country.visible = True
    self.next_button_country.visible = True
    if self.current_page == 1:
      self.prev_button_country.enabled = False
    else:
      self.prev_button_country.enabled = True
    if self.current_page == self.total_pages:
      self.next_button_country.enabled = False
    else:
      self.next_button_country.enabled = True

  def next_page_country(self, **event_args):
    if self.current_page < self.total_pages:
      self.create_monthly_listeners_by_country_bar_chart(
        country_page=self.current_page + 1
      )

  def previous_page_country(self, **event_args):
    if self.current_page > 1:
      self.create_monthly_listeners_by_country_bar_chart(
        country_page=self.current_page - 1
      )

  def create_monthly_listeners_by_city_bar_chart(
    self, page=1, items_per_page=15, city_w_country_code=None, monthly_listeners=None
  ):
    selected_country_name = self.sort_dropdown_countries.selected_value

    city_w_country_code = self.listeners_city_data["city_w_country_code"]
    monthly_listeners = self.listeners_city_data["monthly_listeners"]
    country_name = self.listeners_city_data["country_name_city"]

    # Calculate the range for the current page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    # Slice the data for the current page
    city_w_country_code_page = city_w_country_code[start_index:end_index]
    monthly_listeners_page = monthly_listeners[start_index:end_index]
    country_name_page = country_name[start_index:end_index]

    bar_colors = [
      "rgba(237,139,82,1)"
      if code == selected_country_name or selected_country_name == "All countries"
      else "rgba(125,125,125,0.6)"
      for code in country_name_page
    ]
    # Format the text for the bar annotations
    formatted_text = [
      f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.1f}K" if x >= 1e3 else str(x)
      for x in monthly_listeners
    ]

    # Creating the Bar Chart
    fig = go.Figure(
      data=(
        go.Bar(
          x=city_w_country_code_page,
          y=monthly_listeners_page,
          text=formatted_text,
          textposition="none",
          hoverinfo="none",
          hovertext=city_w_country_code_page,
          hovertemplate="City: %{hovertext}<br>Monthly Listeners: %{text} <extra></extra>",
        )
      )
    )

    fig.update_layout(
      template="plotly_dark",
      plot_bgcolor="rgba(0,0,0,0)",
      paper_bgcolor="rgba(0,0,0,0)",
      xaxis=dict(
        tickvals=list(range(len(city_w_country_code))),
      ),
      yaxis=dict(
        gridcolor="rgb(175,175,175)",  # Color of the gridlines
        gridwidth=1,  # Thickness of the gridlines
        griddash="dash",  # Dash style of the gridlines
        range=[
          0,
          max(monthly_listeners) * 1.2,
        ],  # Adjust y-axis range to add extra space
        tickformat="~s",  # Format numbers with SI unit prefixes
        zerolinecolor="rgb(240,240,240)",  # Set the color of the zero line
      ),
      margin=dict(
        t=0,  # Top margin
        b=20,  # Bottom margin
      ),
      hoverlabel=dict(bgcolor="rgba(237,139,82, 0.4)"),
    )
    # This is to style the bars
    for trace in fig.data:
      trace.update(marker=dict(color=bar_colors), marker_line_width=0.1, opacity=0.9)
    self.Spotify_Monthly_Listeners_by_City_Graph.figure = fig
    self.current_page = page
    self.total_pages = (len(city_w_country_code) + items_per_page - 1) // items_per_page
    self.prev_button_city.visible = True
    self.next_button_city.visible = True
    if self.current_page == 1:
      self.prev_button_city.enabled = False
    else:
      self.prev_button_city.enabled = True
    if self.current_page == self.total_pages:
      self.next_button_city.enabled = False
    else:
      self.next_button_city.enabled = True

  def next_page_city(self, **event_args):
    if self.current_page < self.total_pages:
      self.create_monthly_listeners_by_city_bar_chart(page=self.current_page + 1)

  def previous_page_city(self, **event_args):
    if self.current_page > 1:
      self.create_monthly_listeners_by_city_bar_chart(page=self.current_page - 1)

  def create_artist_popularity_scatter_chart(self, dates=None, artist_popularity=None):
    scatter_data_pop = {
      "dates": [
        date
        for date, followers in zip(
          self.scatter_data["dates"], self.scatter_data["artist_popularity"]
        )
        if followers is not None
      ],
      "artist_popularity": [
        popularity
        for popularity in self.scatter_data["artist_popularity"]
        if popularity is not None
      ],
    }

    if dates is None:
      dates = scatter_data_pop["dates"]
    if artist_popularity is None:
      artist_popularity = scatter_data_pop["artist_popularity"]

    # Creating the Scatter Chart
    fig = go.Figure(
      data=(
        go.Scatter(
          x=dates,
          y=artist_popularity,
          text=artist_popularity,
          textposition="outside",
          hoverinfo="none",
          hovertext=dates,
          hovertemplate="Date: %{hovertext}<br>Artist Spotify Popularity: %{y} <extra></extra>",
        )
      )
    )
    fig.update_layout(
      template="plotly_dark",
      plot_bgcolor="rgba(0,0,0,0)",
      paper_bgcolor="rgba(0,0,0,0)",
      margin=dict(t=50),
      xaxis=dict(showgrid=False),
      yaxis=dict(
        shogrid=True,
        gridcolor="rgb(175,175,175)",  # Color of the gridlines
        gridwidth=0.1,  # Thickness of the gridlines
        griddash="dash",  # Dash style of the gridlines
      ),
      hoverlabel=dict(bgcolor="rgba(237,139,82, 0.4)"),
    )
    for trace in fig.data:
      trace.update(
        marker_color="rgb(237,139,82)",
        # marker_color='rgb(240,229,252)',
        marker_line_color="rgb(237,139,82)",
        marker_line_width=1,
        opacity=0.9,
      )

    self.Spotify_Popularity_Graph.figure = fig

  def create_artist_followers_scatter_chart(self, dates=None, artist_followers=None):
    scatter_data_fol = {
      "dates": [
        date
        for date, followers in zip(
          self.scatter_data["dates"], self.scatter_data["artist_followers"]
        )
        if followers is not None
      ],
      "artist_followers": [
        followers
        for followers in self.scatter_data["artist_followers"]
        if followers is not None
      ],
    }

    if dates is None:
      dates = scatter_data_fol["dates"]
    if artist_followers is None:
      artist_followers = scatter_data_fol["artist_followers"]

    # Format the text for the bar annotations
    formatted_text = [
      f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.1f}K" if x >= 1e3 else str(x)
      for x in artist_followers
    ]

    # Creating the Scatter Chart
    fig = go.Figure(
      data=(
        go.Scatter(
          x=dates,
          y=artist_followers,
          text=formatted_text,
          textposition="outside",
          hoverinfo="none",
          hovertext=dates,
          hovertemplate="Date: %{hovertext}<br>Artist Spotify Followers: %{text} <extra></extra>",
        )
      )
    )
    fig.update_layout(
      template="plotly_dark",
      plot_bgcolor="rgba(0,0,0,0)",
      paper_bgcolor="rgba(0,0,0,0)",
      margin=dict(t=50),
      xaxis=dict(showgrid=False),
      yaxis=dict(
        shogrid=True,
        gridcolor="rgba(175,175,175,1)",  # Color of the gridlines
        gridwidth=0.1,  # Thickness of the gridlines
        griddash="dash",  # Dash style of the gridlines
        tickformat="~s",  # Format numbers with SI unit prefixes
      ),
      hoverlabel=dict(bgcolor="rgba(237,139,82, 0.4)"),
    )
    for trace in fig.data:
      trace.update(
        marker_color="rgb(237,139,82)",
        # marker_color='rgb(237,139,82)',
        marker_line_color="rgb(237,139,82)",
        marker_line_width=1,
        opacity=0.9,
      )

    self.Spotify_Followers_Graph.figure = fig

  def create_artist_monthly_listeners_scatter_chart(
    self, dates=None, monthly_listeners=None
  ):
    if dates is None:
      dates = self.listeners_data["dates"]
    if monthly_listeners is None:
      monthly_listeners = self.listeners_data["monthly_listeners"]

    # Format the text for the bar annotations
    formatted_text = [
      f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.1f}K" if x >= 1e3 else str(x)
      for x in monthly_listeners
    ]

    # Creating the Scatter Chart
    fig = go.Figure(
      data=(
        go.Scatter(
          x=dates,
          y=monthly_listeners,
          mode="lines",
          text=formatted_text,
          textposition="outside",
          hoverinfo="none",
          hovertext=dates,
          hovertemplate="Date: %{hovertext}<br>Artist Spotify Monthly Listeners: %{text} <extra></extra>",
        )
      )
    )
    fig.update_layout(
      template="plotly_dark",
      plot_bgcolor="rgba(0,0,0,0)",
      paper_bgcolor="rgba(0,0,0,0)",
      margin=dict(t=50),
      xaxis=dict(showgrid=False),
      yaxis=dict(
        shogrid=True,
        gridcolor="rgb(175,175,175)",  # Color of the gridlines
        gridwidth=0.1,  # Thickness of the gridlines
        griddash="dash",  # Dash style of the gridlines
        tickformat="~s",  # Format numbers with SI unit prefixes
      ),
      hoverlabel=dict(bgcolor="rgba(237,139,82, 0.4)"),
    )
    for trace in fig.data:
      trace.update(
        marker_color="rgb(237,139,82)",
        # marker_color='rgb(240,229,252)',
        marker_line_color="rgb(237,139,82)",
        marker_line_width=1,
        opacity=0.9,
      )

    self.Spotify_Monthly_Listeners_Graph.figure = fig

  def create_social_media_followers_chart_all_platforms(self, platform_data):
    traces = []
    # Define colors for each platform
    platform_colors = {
      "instagram": "rgb(253, 101, 45)",
      "tiktok": "rgb(0, 153, 204)",
      "youtube": "rgb(255, 0, 0)",
      "soundcloud": "rgb(205, 60, 0)",
    }

    for (
      platform,
      data,
    ) in platform_data.items():  # Use platform_data instead of self.platform_data
      if data["dates"]:
        trace = go.Scatter(
          x=data["dates"],
          y=data["followers"],
          mode="lines+markers",
          name=platform.capitalize(),
          line=dict(
            color=platform_colors.get(platform, "black")
          ),  # Default to black if no color specified
          text=data["followers"],
          textposition="outside",
          hoverinfo="none",
          hovertext=data["dates"],
          # hovertemplate=f'{platform.capitalize()} Followers: %{text}<br>Date: %{hovertext} <extra></extra>'
        )
        traces.append(trace)

    fig = go.Figure(data=traces)

    fig.update_layout(
      template="plotly_dark",
      plot_bgcolor="rgba(0,0,0,0)",
      paper_bgcolor="rgba(0,0,0,0)",
      xaxis=dict(
        showgrid=False  # Remove x-axis gridlines
      ),
      yaxis=dict(
        showgrid=True,  # Ensure y-axis gridlines are visible
        gridcolor="rgba(250,250,250,1)",  # Color of the gridlines
        gridwidth=2,  # Emphasized thickness of the gridlines
      ),
      margin=dict(
        l=5,  # Left margin
        r=5,  # Right margin
        t=0,  # Top margin
        b=5,  # Bottom margin
      ),
    )

    self.Social_Media_Followers_Graph.figure = fig

  def apply_default_sorting(self):
    """Apply the default sorting based on the dropdown selection"""
    labels = self.bar_data["labels"]
    cooperations = self.bar_data["cooperations"]
    sorted_indices = sorted(
      range(len(cooperations)), key=lambda i: cooperations[i], reverse=True
    )
    sorted_labels = [labels[i] for i in sorted_indices]
    sorted_cooperations = [cooperations[i] for i in sorted_indices]
    self.create_bar_chart(labels=sorted_labels, cooperations=sorted_cooperations)

  def sort_data(self, **event_args):
    sort_option = self.sort_dropdown.selected_value
    labels = self.bar_data["labels"]
    cooperations = self.bar_data["cooperations"]

    if sort_option == "alpha":
      # Sort alphabetically
      sorted_indices = sorted(range(len(labels)), key=lambda i: labels[i])
    elif sort_option == "reverse_alpha":
      # Sort reverse alphabetically
      sorted_indices = sorted(range(len(labels)), key=lambda i: labels[i], reverse=True)
    elif sort_option == "high_num":
      # Sort by highest number of cooperations
      sorted_indices = sorted(
        range(len(cooperations)), key=lambda i: cooperations[i], reverse=True
      )
    elif sort_option == "low_num":
      # Sort by lowest number of cooperations
      sorted_indices = sorted(range(len(cooperations)), key=lambda i: cooperations[i])
    else:
      # If "Sort" is selected, do not sort
      return

    sorted_labels = [labels[i] for i in sorted_indices]
    sorted_cooperations = [cooperations[i] for i in sorted_indices]

    # Update the bar chart with sorted data
    self.create_bar_chart(labels=sorted_labels, cooperations=sorted_cooperations)

  # ----------------------------------------------
  # ----------------------------------------------

  # -------------------------------
  # INFO CLICK
  def info_click(self, **event_args):
    if self.info.icon == "fa:angle-down":
      self.info.icon = "fa:angle-up"
      self.info.icon_align = "left_edge"
      self.info.text = "This is your artist dashboard - showing everything you need to know about the artist recommended just for you by our AI. Rate the artist, and our algorithm will continue to learn what you like and appreciate in artists - be it their music style, their origin or label status. If you want to narrow it down manually, use the filters!"
    else:
      self.info.icon = "fa:angle-down"
      self.info.icon_align = "left"
      self.info.text = "Info"

  # -------------------------------
  # BIO CLICK
  def bio_click(self, **event_args):
    if self.sug["Countries"] == "None":
      source = None
      countryname = None
    else:
      country = json.loads(self.sug["Countries"])
      countryname = country["CountryName"]
      source = "https://flagcdn.com/w40/" + country["CountryCode"].lower() + ".png"
    country_flag = Image(source=source, spacing_below=0, spacing_above=0)
    custom_alert_form = C_CustomAlertForm(
      text=self.sug["Biography"],
      pickurl=self.sug["ArtistPictureURL"],
      artist_name=self.sug["Name"],
      countryflag=country_flag,
      countryname=countryname,
    )
    alert(content=custom_alert_form, large=True, buttons=[])

  # -------------------------------
  # WATCHLIST
  def link_watchlist_name_click(self, **event_args):    
    name = self.Artist_Name_Details.get_components()
    name = name[0].text
    if self.link_watchlist_name.icon == "fa:star":
      self.link_watchlist_name.icon = "fa:star-o"
      # self.link_watchlist_name2.icon = "fa:star-o"
      self.parent.parent.parent.parent.link_watchlist_name2.icon = "fa:star-o"
      self.update_watchlist_lead(self.artist_id, False, None, False)
      Notification("", title=f"{name} removed from the watchlist!", style="success").show()
    else:
      self.link_watchlist_name.icon = "fa:star"
      # self.link_watchlist_name2.icon = "fa:star"
      self.parent.parent.parent.parent.link_watchlist_name2.icon = "fa:star"
      self.update_watchlist_lead(self.artist_id, True, "Action required", True)
      Notification("", title=f"{name} added to the watchlist!", style="success").show()

  def update_watchlist_lead(self, artist_id, watchlist, status, notification, **event_args):
    anvil.server.call(
      "update_watchlist_lead",
      user["user_id"],
      self.watchlist_id,
      artist_id,
      watchlist,
      status,
      notification,
    )
    
    self.parent.parent.parent.parent.parent.parent.update_no_notifications()

  # -------------------------------
  # SECTION NAVIGATION
  def nav_releases_click(self, **event_args):
    self.nav_releases.role = "section_buttons_focused"
    self.nav_success.role = "section_buttons"
    self.nav_fandom.role = "section_buttons"
    self.nav_musical.role = "section_buttons"
    self.sec_releases.visible = True
    self.sec_success.visible = False
    self.sec_fandom.visible = False
    self.sec_musical.visible = False

  def nav_success_click(self, **event_args):
    self.nav_releases.role = "section_buttons"
    self.nav_success.role = "section_buttons_focused"
    self.nav_fandom.role = "section_buttons"
    self.nav_musical.role = "section_buttons"
    self.sec_releases.visible = False
    self.sec_success.visible = True
    self.sec_fandom.visible = False
    self.sec_musical.visible = False

  def nav_fandom_click(self, **event_args):
    self.nav_releases.role = "section_buttons"
    self.nav_success.role = "section_buttons"
    self.nav_fandom.role = "section_buttons_focused"
    self.nav_musical.role = "section_buttons"
    self.sec_releases.visible = False
    self.sec_success.visible = False
    self.sec_fandom.visible = True
    self.sec_musical.visible = False

  def nav_musical_click(self, **event_args):
    self.nav_releases.role = "section_buttons"
    self.nav_success.role = "section_buttons"
    self.nav_fandom.role = "section_buttons"
    self.nav_musical.role = "section_buttons_focused"
    self.sec_releases.visible = False
    self.sec_success.visible = False
    self.sec_fandom.visible = False
    self.sec_musical.visible = True

  # -------------------------------
  # RATING BUTTONS
  def set_rating_highlight(self, **event_args):
    self.parent.parent.parent.parent.set_rating_highlight(None if self.sug["Interest"] == "None" else int(self.sug["Interest"]))
  
  def button_1_click(self, **event_args):
    anvil.server.call(
      "add_interest", user["user_id"], self.model_id, self.artist_id, 1, False, ""
    )
    # self.column_panel_header.scroll_into_view(smooth=True)
    # next_artist_id = anvil.server.call("get_next_artist_id", self.model_id)
    # routing.set_url_hash(f"artists?artist_id={next_artist_id}", load_from_cache=False)
    Notification("", title="Artist rated with 1!", style="success").show()

  def button_2_click(self, **event_args):
    anvil.server.call(
      "add_interest", user["user_id"], self.model_id, self.artist_id, 2, False, ""
    )
    # self.column_panel_header.scroll_into_view(smooth=True)
    # next_artist_id = anvil.server.call("get_next_artist_id", self.model_id)
    # routing.set_url_hash(f"artists?artist_id={next_artist_id}", load_from_cache=False)
    Notification("", title="Artist rated with 2!", style="success").show()

  def button_3_click(self, **event_args):
    anvil.server.call(
      "add_interest", user["user_id"], self.model_id, self.artist_id, 3, False, ""
    )
    # self.column_panel_header.scroll_into_view(smooth=True)
    # next_artist_id = anvil.server.call("get_next_artist_id", self.model_id)
    # routing.set_url_hash(f"artists?artist_id={next_artist_id}", load_from_cache=False)
    Notification("", title="Artist rated with 3!", style="success").show()

  def button_4_click(self, **event_args):
    anvil.server.call(
      "add_interest", user["user_id"], self.model_id, self.artist_id, 4, False, ""
    )
    # self.column_panel_header.scroll_into_view(smooth=True)
    # next_artist_id = anvil.server.call("get_next_artist_id", self.model_id)
    # routing.set_url_hash(f"artists?artist_id={next_artist_id}", load_from_cache=False)
    Notification("", title="Artist rated with 4!", style="success").show()

  def button_5_click(self, **event_args):
    anvil.server.call(
      "add_interest", user["user_id"], self.model_id, self.artist_id, 5, False, ""
    )
    # self.column_panel_header.scroll_into_view(smooth=True)
    # next_artist_id = anvil.server.call("get_next_artist_id", self.model_id)
    # routing.set_url_hash(f"artists?artist_id={next_artist_id}", load_from_cache=False)
    Notification("", title="Artist rated with 5!", style="success").show()

  def button_6_click(self, **event_args):
    anvil.server.call(
      "add_interest", user["user_id"], self.model_id, self.artist_id, 6, False, ""
    )
    # self.column_panel_header.scroll_into_view(smooth=True)
    # next_artist_id = anvil.server.call("get_next_artist_id", self.model_id)
    # routing.set_url_hash(f"artists?artist_id={next_artist_id}", load_from_cache=False)
    Notification("", title="Artist rated with 6!", style="success").show()

  def button_7_click(self, **event_args):
    anvil.server.call(
      "add_interest", user["user_id"], self.model_id, self.artist_id, 7, False, ""
    )
    # self.column_panel_header.scroll_into_view(smooth=True)
    # next_artist_id = anvil.server.call("get_next_artist_id", self.model_id)
    # routing.set_url_hash(f"artists?artist_id={next_artist_id}", load_from_cache=False)
    Notification("", title="Artist rated with 7!", style="success").show()

  # -------------------------------
  # DESCRIPTION LINKS
  def info_prediction_click(self, **event_args):
    alert(
      title="Prediction",
      content="Prediction of interest for you personally. Is based on your individually trained Machine Learning Model. Ranges from 1 to 7.",
    )

  def info_popularity_click(self, **event_args):
    alert(
      title="Popularity",
      content="Level of popularity on Spotify. Ranges from 0 to 100.",
    )

  def info_follower_click(self, **event_args):
    alert(title="Follower", content="Number of followers on Spotify")

  def info_no_tracks_click(self, **event_args):
    alert(
      title="No. Tracks",
      content="Number of tracks from the presented Artist in our database. Not all tracks of this Artist have to be in the database.",
    )

  def info_min_distance_click(self, **event_args):
    alert(
      title="Min. musical Distance",
      content="If you subscribed to the Inspect or Dissect subscription, the minimal musical distance is the smallest Euclidean Distance between one of the artist's songs and your personal reference tracks.\n\nIf you have not yet added your reference tracks or are subscribed to the Explore subscription, this value is empty.",
    )

  def info_avg_distance_click(self, **event_args):
    alert(
      title="Avg. musical Distance",
      content="If you subscribed to the Inspect or Dissect subscription, the average musical distance is the average Euclidean Distance between the artist's songs and your personal reference tracks.\n\nIf you have not yet added your reference tracks or are subscribed to the Explore subscription, this value is empty.",
    )

  def info_max_distance_click(self, **event_args):
    alert(
      title="Max. musical Distance",
      content="If you subscribed to the Inspect or Dissect subscription, the maximal musical distance is the largest Euclidean Distance between one of the artist's songs and your personal reference tracks.\n\nIf you have not yet added your reference tracks or are subscribed to the Explore subscription, this value is empty.",
    )

  def info_duration_click(self, **event_args):
    alert(
      title="Avg. Duration",
      content="The average duration of all songs of an artist in seconds.",
    )

  def info_danceability_click(self, **event_args):
    alert(
      title="Avg. Danceability",
      content="Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity.\n\nWe average this value across all songs and its value ranges from 0 (least danceable) to 100% (most danceable).",
    )

  def info_energy_click(self, **event_args):
    alert(
      title="Avg. Energy",
      content="Energy is a measure from 0 to 100% and represents a perceptual measure of intensity and activity on average across all songs.",
    )

  def info_key_click(self, **event_args):
    alert(
      title="Avg. Key",
      content="The estimated overall average key of all songs of an artist",
    )

  def info_loudness_click(self, **event_args):
    alert(
      title="Avg. relative Loudness",
      content="The overall average loudness of all tracks in decibels (dB).\n\nFor each track the loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks.",
    )

  def info_mode_click(self, **event_args):
    alert(
      title="Mode",
      content="Mode indicates the portion of tracks in major (modality) of an artist. Ranges from 0 to 100%.",
    )

  def info_speechiness_click(self, **event_args):
    alert(
      title="Avg. Speechiness",
      content="Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g., talk show, audiobook, poetry), the closer to 100% the attribute value. It is averaged across all songs of that artist.",
    )

  def info_acousticness_click(self, **event_args):
    alert(
      title="Avg. Acousticness",
      content="A confidence measure from 0 to 100% of whether an artist's tracks are acoustic. 100% represents high confidence the tracks are acoustic.",
    )

  def info_instrumentalness_click(self, **event_args):
    alert(
      title="Avg. Instrumentalness",
      content="Measures whether the tracks of an artist contain no vocals.\n\n“Ooh” and “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly “vocal”. The closer the instrumentalness value is to 100%, the greater likelihood the tracks contain no vocal content.",
    )

  def info_liveness_click(self, **event_args):
    alert(
      title="Avg. Liveness",
      content="Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the tracks of that artist were performed live.",
    )

  def info_valence_click(self, **event_args):
    alert(
      title="Avg. Valence",
      content="A measure from 0 to 100% describing the musical positiveness conveyed by an artist's tracks. Tracks with high valence sound more positive (e.g., happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g., sad, depressed, angry).",
    )

  def info_tempo_click(self, **event_args):
    alert(
      title="Avg. Tempo",
      content="The overall average estimated tempo of all track of an artist in beats per minute (BPM).",
    )

  def info_first_release_click(self, **event_args):
    alert(
      title="First Release",
      content="Date of the first release of an artist on Spotify.\n\nOur database is not complete yet - there might be missing tracks that are not present in our database.",
    )

  def info_last_release_click(self, **event_args):
    alert(
      title="Latest Release",
      content="Date of the latest release of an artist on Spotify.\n\nOur database is not complete yet - there might be missing tracks that are not present in our database.",
    )

  def info_latest_label_click(self, **event_args):
    alert(
      title="Latest Label", content="Name of the latest label this artist worked with."
    )

  def info_major_click(self, **event_args):
    alert(
      title="Major Coop",
      content="Indicates whether this artist ever worked with a major label or not.",
    )

  def info_sub_major_click(self, **event_args):
    alert(
      title="Sub-Major Coop",
      content="Indicates whether this artist ever worked with a sub-major label or not.",
    )

  def info_no_co_artists_click(self, **event_args):
    alert(
      title="Avg. No. of Co-Artists per Track",
      content="Total number of Co-Artists per Track divided by total number of Tracks.",
    )

  def info_sp_pop_lat(self, **event_args):
    alert(
      title="Spotify Popularity",
      content="Current value of Spotify Popularity - measured between 0 and 100.",
    )

  def info_sp_fol_lat(self, **event_args):
    alert(title="Spotify Follower", content="Current number of Spotify Follower.")

  def info_sp_mtl_listeners(self, **event_args):
    alert(
      title="Spotify Monthly Listeners",
      content="Latest number of monthly listeners on Spotify.",
    )

  def info_audience_country(self, **event_args):
    alert(
      title="Biggest Audience Country",
      content="Country with most listeners on Spotify.",
    )

  def info_audience_city(self, **event_args):
    alert(title="Biggest Audience City", content="City with most listeners on Spotify.")

  def info_tiktok_fol(self, **event_args):
    alert(title="TikTok Followers lat.", content="Latest number of TikTok Follower.")

  def info_soundcloud_fol(self, **event_args):
    alert(
      title="Soundcloud Follower lat.", content="Latest number of Soundcloud Follower."
    )

  def button_set_filters_click(self, **event_args):
    click_button(f"model_profile?model_id={self.model_id}&section=Filter", event_args)

  def button_remove_filters_click(self, **event_args):
    anvil.server.call("change_filters", self.model_id, filters_json=None)
    self.column_panel_header.scroll_into_view(smooth=True)
    next_artist_id = anvil.server.call("get_next_artist_id", self.model_id)
    routing.set_url_hash(f"artists?artist_id={next_artist_id}", load_from_cache=False)

  def drop_down_model_change(self, **event_args):
    model_data = json.loads(anvil.server.call("get_model_ids", user["user_id"]))
    model_id_new = [
      item["model_id"]
      for item in model_data
      if item["model_name"] == self.drop_down_model.selected_value
    ][0]
    self.model_id = model_id_new
    save_var("model_id", model_id_new)
    anvil.server.call("update_model_usage", user["user_id"], model_id_new)
    self.column_panel_header.scroll_into_view(smooth=True)
    get_open_form().refresh_models_underline()
    routing.set_url_hash(f"artists?artist_id={self.artist_id}", load_from_cache=False)

  def drop_down_wl_change(self, **event_args):
    wl_data = json.loads(anvil.server.call("get_watchlist_ids", user["user_id"]))
    wl_id_new = [
      item["watchlist_id"]
      for item in wl_data
      if item["watchlist_name"] == self.drop_down_wl.selected_value
    ][0]
    self.watchlist_id = wl_id_new
    save_var("watchlist_id", wl_id_new)
    anvil.server.call("update_watchlist_usage", user["user_id"], wl_id_new)
    self.column_panel_header.scroll_into_view(smooth=True)
    get_open_form().refresh_watchlists_underline()
    routing.set_url_hash(f"artists?artist_id={self.artist_id}", load_from_cache=False)

  # -----------------------------------------------------------------------------------------
  #  Start of the Sidebar Watchilish Functions
  # -----------------------------------------------------------------------------------------
  def get_watchlist_notes(self, artist_id, **event_args):
    self.repeating_panel_1.items = json.loads(
      anvil.server.call("get_watchlist_notes", user["user_id"], artist_id)
    )

  def button_note_click(self, **event_args):
    anvil.server.call(
      "add_note",
      user["user_id"],
      self.artist_id,
      "",
      "",
      self.comments_area_section.text,
    )
    self.get_watchlist_notes(self.artist_id)
    self.update_details_on_sidebar()

  def get_watchlist_details(self, artist_id, **event_args):
    details = json.loads(
      anvil.server.call("get_watchlist_details", self.watchlist_id, artist_id)
    )

    if details[0]["Description"] is None:
      self.label_description_2.text = "-"
      self.text_area_description.text = None
    else:
      self.label_description_2.text = details[0]["Description"]
      self.text_area_description.text = details[0]["Description"]

    if details[0]["ContactName"] is None:
      self.label_contact.text = "-"
      self.Text_Box_for_Artist_Name.text = None
    else:
      self.label_contact.text = details[0]["ContactName"]
      self.Text_Box_for_Artist_Name.text = details[0]["ContactName"]
    if details[0]["Mail"] is None:
      self.label_mail.text = "-"
      self.Text_Box_for_Artist_Email.text = None
    else:
      self.label_mail.text = details[0]["Mail"]
      self.Text_Box_for_Artist_Email.text = details[0]["Mail"]
    if details[0]["Phone"] is None:
      self.label_phone.text = "-"
      self.Text_Box_for_Artist_Phone.text = None
    else:
      self.label_phone.text = details[0]["Phone"]
      self.Text_Box_for_Artist_Phone.text = details[0]["Phone"]

    # tags
    if details[0]["Status"] is None:
      self.status_dropdown.selected_value = "Action required"
    else:
      self.status_dropdown.selected_value = details[0]["Status"]
    if details[0]["Priority"] is None:
      self.priority_dropdown.selected_value = "mid"
    else:
      self.priority_dropdown.selected_value = details[0]["Priority"]
    if details[0]["Reminder"] is None:
      self.date_picker_1.date = ""
    else:
      self.date_picker_1.date = details[0]["Reminder"]

  def update_details_on_sidebar(self, **event_args):
    """This method is called when an item is selected"""
    details = json.loads(
      anvil.server.call("get_watchlist_details", self.watchlist_id, self.artist_id)
    )
    anvil.server.call(
      "update_watchlist_details",
      user["user_id"],
      self.watchlist_id,
      self.artist_id,
      True,
      self.status_dropdown.selected_value,
      self.priority_dropdown.selected_value,
      self.date_picker_1.date,
      details[0]["Notification"],
      self.Text_Box_for_Artist_Name.text,
      self.Text_Box_for_Artist_Email.text,
      self.Text_Box_for_Artist_Phone.text,
      self.text_area_description.text,
    )

    if self.link_watchlist_name.icon == "fa:star-o":
      self.link_watchlist_name.icon = "fa:star"
      # self.link_watchlist_name2.icon = "fa:star"
      self.parent.parent.parent.parent.link_watchlist_name2.icon = "fa:star"
      name = self.Artist_Name_Details.get_components()
      name = name[0].text
      Notification("", title=f"{name} added to the watchlist!", style="success").show()

    self.get_watchlist_details(self.artist_id)

  def contacts_button_click(self, **event_args):
    details = json.loads(
      anvil.server.call("get_watchlist_details", self.watchlist_id, self.artist_id)
    )

    if self.contacts_button.icon == "fa:edit":
      self.contacts_button.icon = "fa:save"

      self.Text_Box_for_Artist_Name.visible = True
      self.Text_Box_for_Artist_Email.visible = True
      self.Text_Box_for_Artist_Phone.visible = True

      self.label_contact.visible = False
      self.label_mail.visible = False
      self.label_phone.visible = False

      self.Text_Box_for_Artist_Name.text = details[0]["ContactName"]
      self.Text_Box_for_Artist_Email.text = details[0]["Mail"]
      self.Text_Box_for_Artist_Phone.text = details[0]["Phone"]

    else:
      self.contacts_button.icon = "fa:edit"

      self.Text_Box_for_Artist_Name.visible = False
      self.Text_Box_for_Artist_Email.visible = False
      self.Text_Box_for_Artist_Phone.visible = False

      self.label_contact.visible = True
      self.label_mail.visible = True
      self.label_phone.visible = True

      # save text boxes
      self.update_details_on_sidebar()

  def description_button_click(self, **event_args):
    if self.description_button.icon == "fa:edit":
      self.description_button.icon = "fa:save"

      self.text_area_description.visible = True
      self.label_description_2.visible = False

    else:
      self.description_button.icon = "fa:edit"

      self.text_area_description.visible = False
      self.label_description_2.visible = True

      # save text boxes
      self.update_details_on_sidebar()

  def button_track_test_click(self, track_id=None, **event_args):
    anvil.js.call_js("playSpotify")

  def spotify_artist_button_click(self, **event_args):
    # if self.spotify_artist_button.icon == "fa:play-circle":
    #   self.spotify_artist_button.icon = "fa:pause-circle"

    #   if load_var("lastplayed") != self.sug["SpotifyArtistID"]:
    #     self.spotify_player_spot.clear()
    #     self.spotify_HTML_player()
    #     self.call_js(
    #       "createOrUpdateSpotifyPlayer", anvil.js.get_dom_node(self), "artist", self.sug["SpotifyArtistID"]
    #     )
    #
    # else:
    #   self.spotify_artist_button.icon = "fa:play-circle"

    # anvil.js.call_js("playSpotify")
    # save_var("lastplayed", self.sug["SpotifyArtistID"])

    # self.reset_track_play_buttons()
    pass

  # def reset_track_play_buttons(self, **event_args):
  #   components = self.data_grid_releases_data.get_components()
  #   for component in components:
  #     component.button_play_track.icon = "fa:play-circle"

  def autoplay_button_click(self, **event_args):
    if self.autoplay_button.icon == "fa:toggle-on":
      self.autoplay_button.icon = "fa:toggle-off"
    else:
      self.autoplay_button.icon = "fa:toggle-on"

    save_var("autoPlayStatus", self.autoplay_button.icon)

  def show_milestone_alert(self, milestone):
    # Show a congratulatory alert when a user reaches a milestone.
    alert(
      content=C_ProgressMessage(self.model_id, milestone),
      buttons=[],
      role=["progress-message", "remove-focus"],
    )

  def set_watchlist_icons(self):
    if self.watchlist_id is None:
      watchlist_presence = "False"
    else:
      watchlist_presence = anvil.server.call("check_watchlist_presence", self.watchlist_id, self.url_artist_id)
    
    if watchlist_presence == "True":
      self.link_watchlist_name.icon = "fa:star"
      self.parent.parent.parent.parent.link_watchlist_name2.icon = "fa:star"
    else:
      self.link_watchlist_name.icon = "fa:star-o"     
      self.parent.parent.parent.parent.link_watchlist_name2.icon = "fa:star-o"
