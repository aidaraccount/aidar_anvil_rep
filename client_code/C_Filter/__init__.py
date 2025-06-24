from ._anvil_designer import C_FilterTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import datetime

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var, save_var

from ..Discover import Discover


class C_Filter(C_FilterTemplate):
  def __init__(self, model_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    #print(f"{datetime.now()}: C_Filter - __init__ - 1", flush=True)
    global user
    user = anvil.users.get_user()
    self.model_id=model_id

    self.data_grid_label_selection.visible = False
    self.link_close.visible = False
    
    #print(f"{datetime.now()}: C_Filter - __init__ - 2", flush=True)

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
    #print(f"{datetime.now()}: C_Filter - __init__ - 3", flush=True)

  
  def load_filters(self, **event_args):
    # General Filters
    my_dict = {"artist_popularity_lat >=": "artist_popularity_lat_min",
               "artist_popularity_lat <=": "artist_popularity_lat_max",
               "artist_follower_lat >=": "artist_follower_lat_min",
               "artist_follower_lat <=": "artist_follower_lat_max",
               "major_coop =": "drop_down_major",
               "sub_major_coop =": "drop_down_submajor",
               "days_since_first_release <=": "years_since_first_release",
               "days_since_last_release <=": "days_since_last_release",
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
    print('fil:', fil)

    # Process filters and handle BETWEEN operators
    processed_filters = []
    for f in fil:
        if f['operator'] == 'BETWEEN' and len(f['value']) == 2:
            # Create a copy for >= filter
            ge_filter = dict(f)
            ge_filter['operator'] = '>='
            ge_filter['value'] = [f['value'][0]]
            processed_filters.append(ge_filter)
            
            # Create a copy for <= filter
            le_filter = dict(f)
            le_filter['operator'] = '<='
            le_filter['value'] = [f['value'][1]]
            processed_filters.append(le_filter)
        else:
            processed_filters.append(f)
    print('processed_filters:', processed_filters)

    # set filter element
    for filter in processed_filters:
      if filter["column"] in ("artist_popularity_lat", "artist_follower_lat", "avg_duration", "avg_loudness", "avg_tempo", "days_since_last_release"):
        element = getattr(self, my_dict[f'{filter["column"]} {filter["operator"]}'], None)
        element.text = "{:.0f}".format(round(float(filter["value"][0]), 0))
      
      elif filter["column"] in ("avg_danceability", "avg_energy", "avg_mode", "avg_speechiness", "avg_acousticness", "avg_instrumentalness", "avg_liveness", "avg_valence"):
        element = getattr(self, my_dict[f'{filter["column"]} {filter["operator"]}'], None)
        element.text = "{:.0f}".format(round(float(filter["value"][0])*100, 0))
      
      elif filter["column"] in ("avg_key"):
        element = getattr(self, my_dict[f'{filter["column"]} {filter["operator"]}'], None)
        tonleiter = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
        element.selected_value = tonleiter[int("{:.0f}".format(round(float(filter["value"][0]), 0)))]
      
      elif filter["column"] in ("major_coop", "sub_major_coop"):
        element = getattr(self, my_dict[f'{filter["column"]} {filter["operator"]}'], None)
        if filter["value"][0] == '1': element.selected_value = 'Yes'
        if filter["value"][0] == '0': element.selected_value = 'No'
      
      elif filter["column"] in ("gender"):
        element = getattr(self, my_dict[f'{filter["column"]} {filter["operator"]}'], None)
        if filter["value"][0] == 'female': element.selected_value = 'Female'
        if filter["value"][0] == 'male': element.selected_value = 'Male'
        if filter["value"][0] == 'mixed': element.selected_value = 'Mixed'
        if filter["value"][0] == 'other': element.selected_value = 'Other'
      
      elif filter["column"] in ("has_top5_de"):
        element = getattr(self, my_dict[f'{filter["column"]} {filter["operator"]}'], None)
        if filter["value"][0] == 'True': element.selected_value = 'True'
        if filter["value"][0] == 'False': element.selected_value = 'False'
      
      elif filter["column"] in ("days_since_first_release"):
        element = getattr(self, my_dict[f'{filter["column"]} {filter["operator"]}'], None)
        element.text = "{:.1f}".format(float(filter["value"][0]) / 365)

      # Label Filters
      elif filter['column'] == 'label':
        filter_label = []
        filter_type = 'include' if filter['operator'] == 'IN' else 'exclude'
        for label in filter['value']:
            # Remove any surrounding quotes from the label name
            label_name = label.strip("'\"")
            filter_label.append({
                'column': label_name,
                'operator': filter_type
            })    
        if filter_label:
          self.rep_pan_label.items = filter_label
          self.label_no_label_filters.visible = False
        
      # Genre Filters
      elif filter['column'] == 'genre_root':
        filter_genre = []
        if filter['operator'] == 'IN':
          filter_type = 'include'
        elif filter['operator'] == 'NOT IN':
          filter_type = 'exclude'
        else:
          filter_type = filter['operator']
        for genre in filter['value']:
            # Remove any surrounding quotes from the genre name
            genre_name = genre.strip("'\"")
            filter_genre.append({
                'column': genre_name,
                'operator': filter_type
            })    
        if filter_genre:
          self.repeating_panel_genre.items = filter_genre
          self.label_no_genre_filters.visible = False

      # Origin Filters
      elif filter['column'] == 'country_code':
        filter_origin = []
        if filter['operator'] == 'IN':
          filter_type = 'include'
        elif filter['operator'] == 'NOT IN':
          filter_type = 'exclude'
        else:
          filter_type = filter['operator']
        for origin in filter['value']:
            # Remove any surrounding quotes from the origin name
            origin_name = origin.strip("'\"")
            filter_origin.append({
                'column': origin_name,
                'operator': filter_type
            })    
        if filter_origin:
          self.repeating_panel_origin.items = filter_origin
          self.label_no_origin_filters.visible = False
    
  
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
    genre_data = self.repeating_panel_genre.items
    print(genre_data)
    genres_list = []

    if genre_data is not None:
      if any(item['operator'] == 'include' for item in genre_data):
        genre_data = [item for item in genre_data if item['operator'] != 'Exclude']
        print(genre_data)
      for element in genre_data:
        genres_list.append(element["column"])
        print(genres_list)
      # op = 'IN' if element["operator"] == 'include' else 'NOT IN'
      if element["operator"] == 'include':
        op = 'IN'
      elif element["operator"] == 'exclude':
        op = 'NOT IN'
      else:
        op = element["operator"]
      if genres_list != []:
        filters_json += f'{{"column":"genre_root","operator":"{op}","value":{json.dumps(genres_list)}}},'
    
    # 5. Origins
    origin_data = self.repeating_panel_origin.items
    origin_list = []

    if origin_data is not None:
      if any(item['operator'] == 'include' for item in origin_data):
        origin_data = [item for item in origin_data if item['operator'] != 'Exclude']
  
      for element in origin_data:
        origin_list.append(element["column"][:2])
        
      # op = 'IN' if element["operator"] == 'include' else 'NOT IN'
      if element["operator"] == 'include':
        op = 'IN'
      elif element["operator"] == 'exclude':
        op = 'NOT IN'
      else:
        op = element["operator"]
      if origin_list != []:
        filters_json += f'{{"column":"country_code","operator":"{op}","value":{json.dumps(origin_list)}}},'
    
    # 6. Gender
    if self.drop_down_gender.selected_value == 'Female': filters_json += '{"column":"gender","operator":"=","value":["female"]},'
    if self.drop_down_gender.selected_value == 'Male': filters_json += '{"column":"gender","operator":"=","value":["male"]},'
    if self.drop_down_gender.selected_value == 'Mixed': filters_json += '{"column":"gender","operator":"=","value":["mixed"]},'
    if self.drop_down_gender.selected_value == 'Other': filters_json += '{"column":"gender","operator":"=","value":["other"]},'

    # 7. German Audience
    if self.drop_down_has_top5_de.selected_value == 'True': filters_json += '{"column":"has_top5_de","operator":"=","value":["True"]},'  # ATTENTION!!!
    if self.drop_down_has_top5_de.selected_value == 'False': filters_json += '{"column":"has_top5_de","operator":"=","value":["False"]},'  # ATTENTION!!!
    
    # correct and close the json string
    if filters_json[-1] == ",": filters_json = filters_json[:-1]
    filters_json += "]"

    # check for filter presence
    if filters_json == '[]': filters_json = None
    print('filters_json:', filters_json)
    
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
    new_entry = {'column':self.drop_down_add_genre.selected_value, 'value':self.drop_down_add_value.selected_value}
    genre_data = self.repeating_panel_genre.items
    if genre_data is None:
      genre_data = [new_entry]
    elif new_entry in genre_data:
      pass
    else:
      genre_data.append(new_entry)    
    self.repeating_panel_genre.items = genre_data
    self.label_no_genre_filters.visible = False

  def button_add_origin_click(self, **event_args):
    new_entry = {'column':self.drop_down_add_origin.selected_value, 'value':self.drop_down_add_value2.selected_value}
    origin_data = self.repeating_panel_origin.items
    if origin_data is None:
      origin_data = [new_entry]
    elif new_entry in origin_data:
      pass
    else:
      origin_data.append(new_entry)
    self.repeating_panel_origin.items = origin_data
    self.label_no_origin_filters.visible = False
