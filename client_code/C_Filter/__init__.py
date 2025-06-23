from ._anvil_designer import C_FilterTemplate
from anvil import *
import stripe.checkout
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

    self.data_grid_label_selection.visible = False
    self.link_close.visible = False
    
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
    # my_dict = {"artist_popularity_lat >=": "artist_popularity_lat_min",
    #            "artist_popularity_lat <=": "artist_popularity_lat_max",
    #            "artist_follower_lat >=": "artist_follower_lat_min",
    #            "artist_follower_lat <=": "artist_follower_lat_max",
    #            "major_coop =": "drop_down_major",
    #            "sub_major_coop =": "drop_down_submajor",
    #            "(CURRENT_DATE - first_release_date) / 365 <=": "years_since_first_release",
    #            "CURRENT_DATE - last_release_date <=": "days_since_last_release",
    #            "avg_duration >=": "avg_duration_min",
    #            "avg_duration <=": "avg_duration_max",
    #            "avg_danceability >=": "avg_danceability_min",
    #            "avg_danceability <=": "avg_danceability_max",
    #            "avg_energy >=": "avg_energy_min",
    #            "avg_energy <=": "avg_energy_max",
    #            "avg_key >=": "avg_key_min",
    #            "avg_key <=": "avg_key_max",
    #            "avg_loudness >=": "avg_loudness_min",
    #            "avg_loudness <=": "avg_loudness_max",
    #            "avg_mode >=": "avg_mode_min",
    #            "avg_mode <=": "avg_mode_max",
    #            "avg_speechiness >=": "avg_speechiness_min",
    #            "avg_speechiness <=": "avg_speechiness_max",
    #            "avg_acousticness >=": "avg_acousticness_min",
    #            "avg_acousticness <=": "avg_acousticness_max",
    #            "avg_instrumentalness >=": "avg_instrumentalness_min",
    #            "avg_instrumentalness <=": "avg_instrumentalness_max",
    #            "avg_liveness >=": "avg_liveness_min",
    #            "avg_liveness <=": "avg_liveness_max",
    #            "avg_valence >=": "avg_valence_min",
    #            "avg_valence <=": "avg_valence_max",
    #            "avg_tempo >=": "avg_tempo_min",
    #            "avg_tempo <=": "avg_tempo_max",
    #            "gender =": "drop_down_gender",
    #            "has_top5_de =": "drop_down_has_top5_de"}
    
    # fil = json.loads(anvil.server.call('get_filters', self.model_id))
    # print(fil)
    
    # for filter in fil:
    #   if filter["column"] in ('general', 'gender', 'has_top5_de', 'date'):
    #     element = getattr(self, my_dict[f'{filter["column"]} {filter["operator"]}'], None)
    #     if filter["column"] in ("artist_popularity_lat", "artist_follower_lat", "avg_duration", "avg_loudness", "avg_tempo", "CURRENT_DATE - last_release_date"):
    #       element.text = "{:.0f}".format(round(float(filter["value"]), 0))
    #     elif filter["column"] in ("avg_danceability", "avg_energy", "avg_mode", "avg_speechiness", "avg_acousticness", "avg_instrumentalness", "avg_liveness", "avg_valence"):
    #       element.text = "{:.0f}".format(round(float(filter["value"])*100, 0))
    #     elif filter["column"] in ("avg_key"):
    #       tonleiter = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
    #       element.selected_value = tonleiter[int("{:.0f}".format(round(float(filter["value"]), 0)))]
    #     elif filter["column"] in ("major_coop", "sub_major_coop"):
    #       if filter["value"] == '1': element.selected_value = 'Yes'
    #       if filter["value"] == '0': element.selected_value = 'No'
    #     elif filter["column"] in ("gender"):
    #       if filter["value"] == 'female': element.selected_value = 'Female'
    #       if filter["value"] == 'male': element.selected_value = 'Male'
    #       if filter["value"] == 'mixed': element.selected_value = 'Mixed'
    #       if filter["value"] == 'other': element.selected_value = 'Other'
    #     elif filter["column"] in ("has_top5_de"):
    #       if filter["value"] == 'True': element.selected_value = 'True'
    #       if filter["value"] == 'False': element.selected_value = 'False'
    #     elif filter["column"] in ("(CURRENT_DATE - first_release_date) / 365"):
    #       element.text = "{:.1f}".format(float(filter["value"]) + 1)

    # # Label Filters
    # filter_label = [item for item in fil if item['column'] == 'label']
    # if len(filter_label) > 0:
    #   # Transform the structure to match what rep_pan_label expects
    #   transformed_label_data = [{'label_name': item['value']} for item in filter_label]
    #   self.rep_pan_label.items = transformed_label_data
    #   self.label_no_label_filters.visible = False
      
    # # Genre Filters
    # filter_genre = [item for item in fil if item['column'] == 'genre_root']
    # if len(filter_genre) > 0:
    #   self.repeating_panel_genre.items = filter_genre
    #   self.label_no_genre_filters.visible = False

    # # Origin Filters
    # filter_origin = [item for item in fil if item['column'] == 'country_code']
    # if len(filter_origin) > 0:
    #   self.repeating_panel_origin.items = filter_origin
    #   self.label_no_origin_filters.visible = False
    pass

  
  def apply_filters_click(self, **event_args):    
    filters_json = '['
    
    # 1. General   
    if self.artist_follower_lat_min.text is not None and self.artist_follower_lat_max.text is not None:
      filters_json += f'{{"column":"artist_follower_lat","operator":"BETWEEN","value":[{self.artist_follower_lat_min.text},{self.artist_follower_lat_max.text}]}},'
    elif self.artist_follower_lat_min.text is not None: filters_json += f'{{"column":"artist_follower_lat","operator":">=","value":[{self.artist_follower_lat_min.text}]}},'
    elif self.artist_follower_lat_max.text is not None: filters_json += f'{{"column":"artist_follower_lat","operator":"<=","value":[{self.artist_follower_lat_max.text}]}},'

    if self.years_since_first_release.text is not None: filters_json += f'{{"column":"days_since_first_release","operator":"<=","value":[{float(self.years_since_first_release.text) * 365}]}},'
    if self.days_since_last_release.text is not None: filters_json += f'{{"column":"days_since_last_release","operator":"<=","value":[{self.days_since_last_release.text}]}},'

    # 2. Label cooperation
    if self.drop_down_major.selected_value == 'Yes': filters_json += f'{{"column":"major_coop","operator":"=","value":[1]}},'
    if self.drop_down_major.selected_value == 'No': filters_json += f'{{"column":"major_coop","operator":"=","value":[0]}},'
    if self.drop_down_submajor.selected_value == 'Yes': filters_json += f'{{"column":"sub_major_coop","operator":"=","value":[1]}},'
    if self.drop_down_submajor.selected_value == 'No': filters_json += f'{{"column":"sub_major_coop","operator":"=","value":[0]}},'

    label_data = self.rep_pan_label.items
    if label_data is not None:
      for element in label_data:
        filters_json += f'{{"column":"latest_label","operator":"NOT IN","value":[{element["label_name"]}]}},'
    
    # 3. Musical Features
    if self.avg_duration_min.text is not None and self.avg_duration_max.text is not None:
      filters_json += f'{{"column":"avg_duration","operator":"BETWEEN","value":[{self.avg_duration_min.text},{self.avg_duration_max.text}]}},'
    elif self.avg_duration_min.text is not None: filters_json += f'{{"column":"avg_duration","operator":">=","value":[{self.avg_duration_min.text}]}},'
    elif self.avg_duration_max.text is not None: filters_json += f'{{"column":"avg_duration","operator":"<=","value":[{self.avg_duration_max.text}]}},'
    
    if self.avg_danceability_min.text is not None and self.avg_danceability_max.text is not None:
      filters_json += f'{{"column":"avg_danceability","operator":"BETWEEN","value":[{int(self.avg_danceability_min.text)/100},{int(self.avg_danceability_max.text)/100}]}},'
    elif self.avg_danceability_min.text is not None: filters_json += f'{{"column":"avg_danceability","operator":">=","value":[{int(self.avg_danceability_min.text)/100}]}},'
    elif self.avg_danceability_max.text is not None: filters_json += f'{{"column":"avg_danceability","operator":"<=","value":[{int(self.avg_danceability_max.text)/100}]}},'
    
    if self.avg_energy_min.text is not None and self.avg_energy_max.text is not None:
      filters_json += f'{{"column":"avg_energy","operator":"BETWEEN","value":[{int(self.avg_energy_min.text)/100},{int(self.avg_energy_max.text)/100}]}},'
    elif self.avg_energy_min.text is not None: filters_json += f'{{"column":"avg_energy","operator":">=","value":[{int(self.avg_energy_min.text)/100}]}},'
    elif self.avg_energy_max.text is not None: filters_json += f'{{"column":"avg_energy","operator":"<=","value":[{int(self.avg_energy_max.text)/100}]}},'

    tonleiter = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
    if self.avg_key_min.selected_value != '' and self.avg_key_max.selected_value != '':
      filters_json += f'{{"column":"avg_key","operator":"BETWEEN","value":[{tonleiter.index(self.avg_key_min.selected_value)},{tonleiter.index(self.avg_key_max.selected_value)}]}},'
    elif self.avg_key_min.selected_value != '': filters_json += f'{{"column":"avg_key","operator":">=","value":[{tonleiter.index(self.avg_key_min.selected_value)}]}},'
    elif self.avg_key_max.selected_value != '': filters_json += f'{{"column":"avg_key","operator":"<=","value":[{tonleiter.index(self.avg_key_max.selected_value)}]}},'
    
    if self.avg_loudness_min.text is not None and self.avg_loudness_max.text is not None:
      filters_json += f'{{"column":"avg_loudness","operator":"BETWEEN","value":[{self.avg_loudness_min.text},{self.avg_loudness_max.text}]}},'
    elif self.avg_loudness_min.text is not None: filters_json += f'{{"column":"avg_loudness","operator":">=","value":[{self.avg_loudness_min.text}]}},'
    elif self.avg_loudness_max.text is not None: filters_json += f'{{"column":"avg_loudness","operator":"<=","value":[{self.avg_loudness_max.text}]}},'
    
    if self.avg_mode_min.text is not None and self.avg_mode_max.text is not None:
      filters_json += f'{{"column":"avg_mode","operator":"BETWEEN","value":[{int(self.avg_mode_min.text)/100},{int(self.avg_mode_max.text)/100}]}},'
    elif self.avg_mode_min.text is not None: filters_json += f'{{"column":"avg_mode","operator":">=","value":[{int(self.avg_mode_min.text)/100}]}},'
    elif self.avg_mode_max.text is not None: filters_json += f'{{"column":"avg_mode","operator":"<=","value":[{int(self.avg_mode_max.text)/100}]}},'
    
    if self.avg_speechiness_min.text is not None and self.avg_speechiness_max.text is not None:
      filters_json += f'{{"column":"avg_speechiness","operator":"BETWEEN","value":[{int(self.avg_speechiness_min.text)/100},{int(self.avg_speechiness_max.text)/100}]}},'
    elif self.avg_speechiness_min.text is not None: filters_json += f'{{"column":"avg_speechiness","operator":">=","value":[{int(self.avg_speechiness_min.text)/100}]}},'
    elif self.avg_speechiness_max.text is not None: filters_json += f'{{"column":"avg_speechiness","operator":"<=","value":[{int(self.avg_speechiness_max.text)/100}]}},'
    
    if self.avg_acousticness_min.text is not None and self.avg_acousticness_max.text is not None:
      filters_json += f'{{"column":"avg_acousticness","operator":"BETWEEN","value":[{int(self.avg_acousticness_min.text)/100},{int(self.avg_acousticness_max.text)/100}]}},'
    elif self.avg_acousticness_min.text is not None: filters_json += f'{{"column":"avg_acousticness","operator":">=","value":[{int(self.avg_acousticness_min.text)/100}]}},'
    elif self.avg_acousticness_max.text is not None: filters_json += f'{{"column":"avg_acousticness","operator":"<=","value":[{int(self.avg_acousticness_max.text)/100}]}},'
    
    if self.avg_instrumentalness_min.text is not None and self.avg_instrumentalness_max.text is not None:
      filters_json += f'{{"column":"avg_instrumentalness","operator":"BETWEEN","value":[{int(self.avg_instrumentalness_min.text)/100},{int(self.avg_instrumentalness_max.text)/100}]}},'
    elif self.avg_instrumentalness_min.text is not None: filters_json += f'{{"column":"avg_instrumentalness","operator":">=","value":[{int(self.avg_instrumentalness_min.text)/100}]}},'
    elif self.avg_instrumentalness_max.text is not None: filters_json += f'{{"column":"avg_instrumentalness","operator":"<=","value":[{int(self.avg_instrumentalness_max.text)/100}]}},'
    
    if self.avg_liveness_min.text is not None and self.avg_liveness_max.text is not None:
      filters_json += f'{{"column":"avg_liveness","operator":"BETWEEN","value":[{int(self.avg_liveness_min.text)/100},{int(self.avg_liveness_max.text)/100}]}},'
    elif self.avg_liveness_min.text is not None: filters_json += f'{{"column":"avg_liveness","operator":">=","value":[{int(self.avg_liveness_min.text)/100}]}},'
    elif self.avg_liveness_max.text is not None: filters_json += f'{{"column":"avg_liveness","operator":"<=","value":[{int(self.avg_liveness_max.text)/100}]}},'

    if self.avg_valence_min.text is not None and self.avg_valence_max.text is not None:
      filters_json += f'{{"column":"avg_valence","operator":"BETWEEN","value":[{int(self.avg_valence_min.text)/100},{int(self.avg_valence_max.text)/100}]}},'
    elif self.avg_valence_min.text is not None: filters_json += f'{{"column":"avg_valence","operator":">=","value":[{int(self.avg_valence_min.text)/100}]}},'
    elif self.avg_valence_max.text is not None: filters_json += f'{{"column":"avg_valence","operator":"<=","value":[{int(self.avg_valence_max.text)/100}]}},'
    
    if self.avg_tempo_min.text is not None and self.avg_tempo_max.text is not None:
      filters_json += f'{{"column":"avg_tempo","operator":"BETWEEN","value":[{self.avg_tempo_min.text},{self.avg_tempo_max.text}]}},'
    elif self.avg_tempo_min.text is not None: filters_json += f'{{"column":"avg_tempo","operator":">=","value":[{self.avg_tempo_min.text}]}},'
    elif self.avg_tempo_max.text is not None: filters_json += f'{{"column":"avg_tempo","operator":"<=","value":[{self.avg_tempo_max.text}]}},'

    # 4. Genres
    # genre_data = self.repeating_panel_genre.items
    # if genre_data is not None:
    #   for element in genre_data:
    #     filters_json += f'{{"column":"{element["column"].lower()}","operator":"IN","value":[{element["value"]}]}},'
    genres_list = []
    genre_elements = [self.g1, self.g2, self.g3, self.g4, self.g5, self.g6, self.g7, self.g8, self.g9, self.g10, self.g11, self.g12, self.g13, self.g14, self.g15, self.g16, self.g17, self.g18, self.g19, self.g20, self.g21, self.g22, self.g23, self.g24, self.g25, self.g26, self.g27, self.g28, self.g29]
    for element in genre_elements:
      if element.checked is True:
        genres_list.append(element.text.lower())
    print('genres_list:', genres_list)
    op = 'IN' if self.drop_down_genre.selected_value == '   INCLUIDE GENRES   ' else 'OUT'
    filters_json += f'{{"column":"genre_root","operator":{op},"value":{genres_list}}},'
    
    # 5. Origins
    origin_data = self.repeating_panel_origin.items
    
    if origin_data is not None:
      for element in origin_data:
        if element["value"] == 'True' or element["value"] is True:
          operator = 'IN'
        else:
          operator = 'NOT IN'
        filters_json += f'{{"column":"country_code","operator":"{operator}","value":[{element["column"][:2]}]}},'
    
    # 6. Gender
    if self.drop_down_gender.selected_value == 'Female': filters_json += f'{{"column":"gender","operator":"=","value":["female"]}},'
    if self.drop_down_gender.selected_value == 'Male': filters_json += f'{{"column":"gender","operator":"=","value":["male"]}},'
    if self.drop_down_gender.selected_value == 'Mixed': filters_json += f'{{"column":"gender","operator":"=","value":["mixed"]}},'
    if self.drop_down_gender.selected_value == 'Other': filters_json += f'{{"column":"gender","operator":"=","value":["other"]}},'

    # 7. German Audience
    if self.drop_down_has_top5_de.selected_value == 'True': filters_json += f'{{"column":"has_top5_de","operator":"=","value":["True"]}},'  # ATTENTION!!!
    if self.drop_down_has_top5_de.selected_value == 'False': filters_json += f'{{"column":"has_top5_de","operator":"=","value":["False"]}},'  # ATTENTION!!!
    
    # correct and close the json string
    if filters_json[-1] == ",": filters_json = filters_json[:-1]
    filters_json += "]"

    # check for filter presence
    if filters_json == '[]': filters_json = None
    print(filters_json)
    
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


  def button_search_label_click(self, **event_args):    
    search_data = json.loads(anvil.server.call('search_label', self.text_box_label.text.strip()))
    self.rep_pan_label_selection.items = search_data
    
    self.data_grid_label_selection.visible = True
    self.link_close.visible = True
        
  def link_close_click(self, **event_args):
    self.data_grid_label_selection.visible = False
    self.link_close.visible = False

  
  def button_add_genre_click(self, **event_args):
    new_entry = {'column':self.drop_down_add_genre.selected_value, "operator":"IN", 'value':[self.drop_down_add_value.selected_value]}  # ATTENTION!!!
    genre_data = self.repeating_panel_genre.items
    if genre_data is None:
      genre_data = [new_entry]
    else:
      genre_data.append(new_entry)    
    self.repeating_panel_genre.items = genre_data
    self.label_no_genre_filters.visible = False

  def button_add_origin_click(self, **event_args):
    new_entry = {'column':self.drop_down_add_origin.selected_value, "operator":"IN", 'value':[self.drop_down_add_value2.selected_value]}  # ATTENTION!!!
    origin_data = self.repeating_panel_origin.items
    if origin_data is None:
      origin_data = [new_entry]
    else:
      origin_data.append(new_entry)    
    self.repeating_panel_origin.items = origin_data
    self.label_no_origin_filters.visible = False
