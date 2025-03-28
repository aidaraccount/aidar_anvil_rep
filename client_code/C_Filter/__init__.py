from ._anvil_designer import C_FilterTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import datetime

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var, save_var

from ..Discover import Discover


class C_Filter(C_FilterTemplate):
  def __init__(self, model_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    #print(f"{datetime.datetime.now()}: C_Filter - __init__ - 1", flush=True)
    global user
    user = anvil.users.get_user()
    self.model_id=model_id
    #print(f"{datetime.datetime.now()}: C_Filter - __init__ - 2", flush=True)

    # ------------------------------------------------- !!! ATTENTION !!!
    # SCORPIO EXTENSION - has_top5_de
    if user['email'] == 'janek-meyn@web.de' or user['email'].endswith('@fkpscorpio.com'):
      self.de_header.visible = True
      self.de_content.visible = True
    else:      
      self.de_header.visible = False
      self.de_content.visible = False
    # ------------------------------------------------- !!! ATTENTION !!!
    
    self.load_filters()
    #print(f"{datetime.datetime.now()}: C_Filter - __init__ - 3", flush=True)

  
  def load_filters(self, **event_args):
    # General Filters
    my_dict = {"artist_popularity_lat >=": "artist_popularity_lat_min",
               "artist_popularity_lat <=": "artist_popularity_lat_max",
               "artist_follower_lat >=": "artist_follower_lat_min",
               "artist_follower_lat <=": "artist_follower_lat_max",
               "major_coop =": "drop_down_major",
               "sub_major_coop =": "drop_down_submajor",
               "(CURRENT_DATE - first_release_date) / 365 <=": "years_since_first_release",
               "CURRENT_DATE - last_release_date <=": "days_since_last_release",
               "avg_duration >=": "avg_duration_min",
               "avg_duration <=": "avg_duration_max",
               "avg_danceability >=": "avg_danceability_min",
               "avg_danceability <=": "avg_danceability_max",
               "avg_energy >=": "avg_energy_min",
               "avg_energy <=": "avg_energy_max",
               "avg_key >=": "avg_key_min",
               "avg_key <=": "avg_key_max",
               "avg_loudness >=": "avg_loudness_min",
               "avg_loudness <=": "avg_loudness_max",
               "avg_mode >=": "avg_mode_min",
               "avg_mode <=": "avg_mode_max",
               "avg_speechiness >=": "avg_speechiness_min",
               "avg_speechiness <=": "avg_speechiness_max",
               "avg_acousticness >=": "avg_acousticness_min",
               "avg_acousticness <=": "avg_acousticness_max",
               "avg_instrumentalness >=": "avg_instrumentalness_min",
               "avg_instrumentalness <=": "avg_instrumentalness_max",
               "avg_liveness >=": "avg_liveness_min",
               "avg_liveness <=": "avg_liveness_max",
               "avg_valence >=": "avg_valence_min",
               "avg_valence <=": "avg_valence_max",
               "avg_tempo >=": "avg_tempo_min",
               "avg_tempo <=": "avg_tempo_max",
               "gender =": "drop_down_gender",
               "has_top5_de =": "drop_down_has_top5_de"}
    
    fil = json.loads(anvil.server.call('get_filters', self.model_id))
    
    for filter in fil:
      if filter["Type"] in ('general', 'gender', 'has_top5_de', 'date'):
        element = getattr(self, my_dict[f'{filter["Column"]} {filter["Operator"]}'], None)
        if filter["Column"] in ("artist_popularity_lat", "artist_follower_lat", "avg_duration", "avg_loudness", "avg_tempo", "CURRENT_DATE - last_release_date"):
          element.text = "{:.0f}".format(round(float(filter["Value"]), 0))
        elif filter["Column"] in ("avg_danceability", "avg_energy", "avg_mode", "avg_speechiness", "avg_acousticness", "avg_instrumentalness", "avg_liveness", "avg_valence"):
          element.text = "{:.0f}".format(round(float(filter["Value"])*100, 0))
        elif filter["Column"] in ("avg_key"):
          tonleiter = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
          element.selected_value = tonleiter[int("{:.0f}".format(round(float(filter["Value"]), 0)))]
        elif filter["Column"] in ("major_coop", "sub_major_coop"):
          if filter["Value"] == '1': element.selected_value = 'Yes'
          if filter["Value"] == '0': element.selected_value = 'No'
        elif filter["Column"] in ("gender"):
          if filter["Value"] == 'female': element.selected_value = 'Female'
          if filter["Value"] == 'male': element.selected_value = 'Male'
          if filter["Value"] == 'mixed': element.selected_value = 'Mixed'
          if filter["Value"] == 'other': element.selected_value = 'Other'
        elif filter["Column"] in ("has_top5_de"):
          if filter["Value"] == 'True': element.selected_value = 'True'
          if filter["Value"] == 'False': element.selected_value = 'False'
        elif filter["Column"] in ("(CURRENT_DATE - first_release_date) / 365"):
          element.text = "{:.1f}".format(float(filter["Value"]) + 1)

    # Genre Filters
    filter_genre = [item for item in fil if item['Type'] == 'genre']
    if len(filter_genre) > 0:
      self.repeating_panel_genre.items = filter_genre
      self.label_no_genre_filters.visible = False

    # Origin Filters
    filter_origin = [item for item in fil if item['Type'] == 'origin']
    if len(filter_origin) > 0:
      self.repeating_panel_origin.items = filter_origin
      self.label_no_origin_filters.visible = False

  
  def apply_filters_click(self, **event_args):
    
    filters_json = '['
    
    # 1. General
    if self.artist_popularity_lat_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"artist_popularity_lat","Operator":">=","Value":"{self.artist_popularity_lat_min.text}"}},'
    if self.artist_popularity_lat_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"artist_popularity_lat","Operator":"<=","Value":"{self.artist_popularity_lat_max.text}"}},'
    if self.artist_follower_lat_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"artist_follower_lat","Operator":">=","Value":"{self.artist_follower_lat_min.text}"}},'
    if self.artist_follower_lat_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"artist_follower_lat","Operator":"<=","Value":"{self.artist_follower_lat_max.text}"}},'

    if self.drop_down_major.selected_value == 'Yes': filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"major_coop","Operator":"=","Value":"1"}},'
    if self.drop_down_major.selected_value == 'No': filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"major_coop","Operator":"=","Value":"0"}},'
    if self.drop_down_submajor.selected_value == 'Yes': filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"sub_major_coop","Operator":"=","Value":"1"}},'
    if self.drop_down_submajor.selected_value == 'No': filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"sub_major_coop","Operator":"=","Value":"0"}},'

    if self.years_since_first_release.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"date","Column":"(CURRENT_DATE - first_release_date) / 365","Operator":"<=","Value":"{self.years_since_first_release.text - 1}"}},'
    if self.days_since_last_release.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"date","Column":"CURRENT_DATE - last_release_date","Operator":"<=","Value":"{self.days_since_last_release.text}"}},'

    # 2. Musical Features
    if self.avg_duration_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_duration","Operator":">=","Value":"{self.avg_duration_min.text}"}},'
    if self.avg_duration_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_duration","Operator":"<=","Value":"{self.avg_duration_max.text}"}},'
    
    if self.avg_danceability_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_danceability","Operator":">=","Value":"{int(self.avg_danceability_min.text)/100}"}},'
    if self.avg_danceability_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_danceability","Operator":"<=","Value":"{int(self.avg_danceability_max.text)/100}"}},'
    
    if self.avg_energy_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_energy","Operator":">=","Value":"{int(self.avg_energy_min.text)/100}"}},'
    if self.avg_energy_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_energy","Operator":"<=","Value":"{int(self.avg_energy_max.text)/100}"}},'

    tonleiter = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
    if self.avg_key_min.selected_value != '': filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_key","Operator":">=","Value":"{tonleiter.index(self.avg_key_min.selected_value)}"}},'
    if self.avg_key_max.selected_value != '': filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_key","Operator":"<=","Value":"{tonleiter.index(self.avg_key_max.selected_value)}"}},'
    
    if self.avg_loudness_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_loudness","Operator":">=","Value":"{self.avg_loudness_min.text}"}},'
    if self.avg_loudness_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_loudness","Operator":"<=","Value":"{self.avg_loudness_max.text}"}},'
    
    if self.avg_mode_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_mode","Operator":">=","Value":"{int(self.avg_mode_min.text)/100}"}},'
    if self.avg_mode_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_mode","Operator":"<=","Value":"{int(self.avg_mode_max.text)/100}"}},'
    
    if self.avg_speechiness_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_speechiness","Operator":">=","Value":"{int(self.avg_speechiness_min.text)/100}"}},'
    if self.avg_speechiness_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_speechiness","Operator":"<=","Value":"{int(self.avg_speechiness_max.text)/100}"}},'
    
    if self.avg_acousticness_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_acousticness","Operator":">=","Value":"{int(self.avg_acousticness_min.text)/100}"}},'
    if self.avg_acousticness_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_acousticness","Operator":"<=","Value":"{int(self.avg_acousticness_max.text)/100}"}},'
    
    if self.avg_instrumentalness_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_instrumentalness","Operator":">=","Value":"{int(self.avg_instrumentalness_min.text)/100}"}},'
    if self.avg_instrumentalness_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_instrumentalness","Operator":"<=","Value":"{int(self.avg_instrumentalness_max.text)/100}"}},'
    
    if self.avg_liveness_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_liveness","Operator":">=","Value":"{int(self.avg_liveness_min.text)/100}"}},'
    if self.avg_liveness_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_liveness","Operator":"<=","Value":"{int(self.avg_liveness_max.text)/100}"}},'

    if self.avg_valence_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_valence","Operator":">=","Value":"{int(self.avg_valence_min.text)/100}"}},'
    if self.avg_valence_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_valence","Operator":"<=","Value":"{int(self.avg_valence_max.text)/100}"}},'
    
    if self.avg_tempo_min.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_tempo","Operator":">=","Value":"{self.avg_tempo_min.text}"}},'
    if self.avg_tempo_max.text is not None: filters_json += f'{{"ModelID":"{self.model_id}","Type":"general","Column":"avg_tempo","Operator":"<=","Value":"{self.avg_tempo_max.text}"}},'

    # 3. Genres
    genre_data = self.repeating_panel_genre.items
    if genre_data is not None:
      for element in genre_data:
        filters_json += f'{{"ModelID":"{self.model_id}","Type":"genre","Column":"{element["Column"].lower()}","Operator":"is","Value":"{element["Value"]}"}},'
    
    # 4. Origins
    origin_data = self.repeating_panel_origin.items
    if origin_data is not None:
      for element in origin_data:
        if element["Value"] == 'True' or element["Value"] is True:
          operator = 'is'
        else:
          operator = 'is not'
        filters_json += f'{{"ModelID":"{self.model_id}","Type":"origin","Column":"country_code","Operator":"{operator}","Value":"{element["Column"][:2]}"}},'
    
    # 5. Gender
    if self.drop_down_gender.selected_value == 'Female': filters_json += f'{{"ModelID":"{self.model_id}","Type":"gender","Column":"gender","Operator":"=","Value":"female"}},'
    if self.drop_down_gender.selected_value == 'Male': filters_json += f'{{"ModelID":"{self.model_id}","Type":"gender","Column":"gender","Operator":"=","Value":"male"}},'
    if self.drop_down_gender.selected_value == 'Mixed': filters_json += f'{{"ModelID":"{self.model_id}","Type":"gender","Column":"gender","Operator":"=","Value":"mixed"}},'
    if self.drop_down_gender.selected_value == 'Other': filters_json += f'{{"ModelID":"{self.model_id}","Type":"gender","Column":"gender","Operator":"=","Value":"other"}},'

    # 6. German Audience
    if self.drop_down_has_top5_de.selected_value == 'True': filters_json += f'{{"ModelID":"{self.model_id}","Type":"has_top5_de","Column":"has_top5_de","Operator":"=","Value":"True"}},'
    if self.drop_down_has_top5_de.selected_value == 'False': filters_json += f'{{"ModelID":"{self.model_id}","Type":"has_top5_de","Column":"has_top5_de","Operator":"=","Value":"False"}},'
    
    # correct and close the json string
    if filters_json[-1] == ",": filters_json = filters_json[:-1]
    filters_json += "]"

    # check for filter presence
    if filters_json == '[]': filters_json = None
    
    # change filters
    anvil.server.call('change_filters',
                      self.model_id,
                      filters_json
                     )
    
    temp_artist_id = anvil.server.call('get_next_artist_id', load_var('model_id'))
    if temp_artist_id is None:
      alert(title='No Artists found..',
        content="Sorry, we cound't find any artists for your selection. Please change your FILTERS to find additional artists.",
        buttons=[
          ("Ok", "OK")
        ]
      )
    else:
      Notification("", title="Filter changes saved!", style="success").show()

  
  def clear_filters_button_click(self, **event_args):    
    anvil.server.call('change_filters',
                      self.model_id,
                      filters_json = None
                     )
    click_button(f'model_profile?model_id={load_var("model_id")}&section=Filter', event_args)
    Notification("", title="All filter are reset!", style="success").show()


  def button_add_genre_click(self, **event_args):
    new_entry = {"ModelID":self.model_id, "Type":"genre", 'Column':self.drop_down_add_genre.selected_value, "Operator":"is", 'Value':self.drop_down_add_value.selected_value}
    genre_data = self.repeating_panel_genre.items
    if genre_data is None:
      genre_data = [new_entry]
    else:
      genre_data.append(new_entry)    
    self.repeating_panel_genre.items = genre_data
    self.label_no_genre_filters.visible = False

  def button_add_origin_click(self, **event_args):
    new_entry = {"ModelID":self.model_id, "Type":"origin", 'Column':self.drop_down_add_origin.selected_value, "Operator":"is", 'Value':self.drop_down_add_value2.selected_value}
    origin_data = self.repeating_panel_origin.items
    if origin_data is None:
      origin_data = [new_entry]
    else:
      origin_data.append(new_entry)    
    self.repeating_panel_origin.items = origin_data
    self.label_no_origin_filters.visible = False
