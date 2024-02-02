from ._anvil_designer import C_FilterTemplate
from ._anvil_designer import C_FilterTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


from ..C_Investigate import C_Investigate

class C_Filter(C_FilterTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.    
    global user
    global cur_model_id
    user = anvil.users.get_user()
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])

    self.load_filters()

  
  def load_filters(self, **event_args):

    # General Filters
    my_dict = {"ArtistPopularity_lat >=": "artist_popularity_lat_min",
               "ArtistPopularity_lat <=": "artist_popularity_lat_max",
               "ArtistFollower_lat >=": "artist_follower_lat_min",
               "ArtistFollower_lat <=": "artist_follower_lat_max",
               "AvgDuration >=": "avg_duration_min",
               "AvgDuration <=": "avg_duration_max",
               "AvgDanceability >=": "avg_danceability_min",
               "AvgDanceability <=": "avg_danceability_max",
               "AvgEnergy >=": "avg_energy_min",
               "AvgEnergy <=": "avg_energy_max",
               "AvgKey >=": "avg_key_min",
               "AvgKey <=": "avg_key_max",
               "AvgLoudness >=": "avg_loudness_min",
               "AvgLoudness <=": "avg_loudness_max",
               "AvgMode >=": "avg_mode_min",
               "AvgMode <=": "avg_mode_max",
               "AvgSpeechiness >=": "avg_speechiness_min",
               "AvgSpeechiness <=": "avg_speechiness_max",
               "AvgAcousticness >=": "avg_acousticness_min",
               "AvgAcousticness <=": "avg_acousticness_max",
               "AvgInstrumentalness >=": "avg_instrumentalness_min",
               "AvgInstrumentalness <=": "avg_instrumentalness_max",
               "AvgLiveness >=": "avg_liveness_min",
               "AvgLiveness <=": "avg_liveness_max",
               "AvgValence >=": "avg_valence_min",
               "AvgValence <=": "avg_valence_max",
               "AvgTempo >=": "avg_tempo_min",
               "AvgTempo <=": "avg_tempo_max"}
    
    fil = json.loads(anvil.server.call('get_filters', cur_model_id))
    
    for filter in fil:
      if filter["Type"] == 'general':
        element = getattr(self, my_dict[f'{filter["Column"]} {filter["Operator"]}'], None)
        if filter["Column"] in ("ArtistPopularity_lat", "ArtistFollower_lat", "Duration", "AvgLoudness", "AvgTempo"):
          element.text = "{:.0f}".format(round(float(filter["Value"]), 0))
        elif filter["Column"] in ("AvgDanceability", "AvgEnergy", "AvgMode", "AvgSpeechiness", "AvgAcousticness", "AvgInstrumentalness", "AvgLiveness", "AvgValence"):
          element.text = "{:.0f}".format(round(float(filter["Value"])*100, 0))
        elif filter["Column"] in ("AvgKey"):
          tonleiter = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
          element.selected_value = tonleiter[int("{:.0f}".format(round(float(filter["Value"]), 0)))]

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
    if self.artist_popularity_lat_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"ArtistPopularity_lat","Operator":">=","Value":"{self.artist_popularity_lat_min.text}"}},'
    if self.artist_popularity_lat_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"ArtistPopularity_lat","Operator":"<=","Value":"{self.artist_popularity_lat_max.text}"}},'
    if self.artist_follower_lat_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"ArtistFollower_lat","Operator":">=","Value":"{self.artist_follower_lat_min.text}"}},'
    if self.artist_follower_lat_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"ArtistFollower_lat","Operator":"<=","Value":"{self.artist_follower_lat_max.text}"}},'
    
    if self.avg_duration_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgDuration","Operator":">=","Value":"{self.avg_duration_min.text}"}},'
    if self.avg_duration_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgDuration","Operator":"<=","Value":"{self.avg_duration_max.text}"}},'
    
    if self.avg_danceability_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgDanceability","Operator":">=","Value":"{int(self.avg_danceability_min.text)/100}"}},'
    if self.avg_danceability_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgDanceability","Operator":"<=","Value":"{int(self.avg_danceability_max.text)/100}"}},'
    
    if self.avg_energy_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgEnergy","Operator":">=","Value":"{int(self.avg_energy_min.text)/100}"}},'
    if self.avg_energy_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgEnergy","Operator":"<=","Value":"{int(self.avg_energy_max.text)/100}"}},'

    tonleiter = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
    if self.avg_key_min.selected_value != '': filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgKey","Operator":">=","Value":"{tonleiter.index(self.avg_key_min.selected_value)}"}},'
    if self.avg_key_max.selected_value != '': filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgKey","Operator":"<=","Value":"{tonleiter.index(self.avg_key_max.selected_value)}"}},'
    
    if self.avg_loudness_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgLoudness","Operator":">=","Value":"{self.avg_loudness_min.text}"}},'
    if self.avg_loudness_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgLoudness","Operator":"<=","Value":"{self.avg_loudness_max.text}"}},'
    
    if self.avg_mode_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgMode","Operator":">=","Value":"{int(self.avg_mode_min.text)/100}"}},'
    if self.avg_mode_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgMode","Operator":"<=","Value":"{int(self.avg_mode_max.text)/100}"}},'
    
    if self.avg_speechiness_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgSpeechiness","Operator":">=","Value":"{int(self.avg_speechiness_min.text)/100}"}},'
    if self.avg_speechiness_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgSpeechiness","Operator":"<=","Value":"{int(self.avg_speechiness_max.text)/100}"}},'
    
    if self.avg_acousticness_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgAcousticness","Operator":">=","Value":"{int(self.avg_acousticness_min.text)/100}"}},'
    if self.avg_acousticness_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgAcousticness","Operator":"<=","Value":"{int(self.avg_acousticness_max.text)/100}"}},'
    
    if self.avg_instrumentalness_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgInstrumentalness","Operator":">=","Value":"{int(self.avg_instrumentalness_min.text)/100}"}},'
    if self.avg_instrumentalness_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgInstrumentalness","Operator":"<=","Value":"{int(self.avg_instrumentalness_max.text)/100}"}},'
    
    if self.avg_liveness_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgLiveness","Operator":">=","Value":"{int(self.avg_liveness_min.text)/100}"}},'
    if self.avg_liveness_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgLiveness","Operator":"<=","Value":"{int(self.avg_liveness_max.text)/100}"}},'

    if self.avg_valence_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgValence","Operator":">=","Value":"{int(self.avg_valence_min.text)/100}"}},'
    if self.avg_valence_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgValence","Operator":"<=","Value":"{int(self.avg_valence_max.text)/100}"}},'
    
    if self.avg_tempo_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgTempo","Operator":">=","Value":"{self.avg_tempo_min.text}"}},'
    if self.avg_tempo_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Type":"general","Column":"AvgTempo","Operator":"<=","Value":"{self.avg_tempo_max.text}"}},'

    # 2. Genres
    genre_data = self.repeating_panel_genre.items
    if genre_data is not None:
      for element in genre_data:
        filters_json += f'{{"ModelID":"{cur_model_id}","Type":"genre","Column":"{element["Column"]}","Operator":"is","Value":"{element["Value"]}"}},'
    
    # 3. Origins
    origin_data = self.repeating_panel_origin.items
    if origin_data is not None:
      for element in origin_data:
        filters_json += f'{{"ModelID":"{cur_model_id}","Type":"origin","Column":"{element["Column"]}","Operator":"is","Value":"{element["Value"]}"}},'
    
    # correct and close the json string
    if filters_json[-1] == ",": filters_json = filters_json[:-1]
    filters_json += "]"

    # check for filter presence
    if filters_json == '[]': filters_json = None
    
    # change filters
    anvil.server.call('change_filters',
                      cur_model_id,
                      filters_json
                     )
    self.content_panel.clear()
    self.content_panel.add_component(C_Investigate(temp_artist_id=None))

  def clear_filters_button_click(self, **event_args):
    
    anvil.server.call('change_filters',
                      cur_model_id,
                      filters_json = None
                     )
    self.content_panel.clear()
    self.content_panel.add_component(C_Investigate(temp_artist_id=None))

  def button_add_genre_click(self, **event_args):
    new_entry = {"ModelID":cur_model_id, "Type":"genre", 'Column':self.drop_down_add_genre.selected_value, "Operator":"is", 'Value':self.drop_down_add_value.selected_value}
    genre_data = self.repeating_panel_genre.items
    if genre_data is None:
      genre_data = [new_entry]
    else:
      genre_data.append(new_entry)    
    self.repeating_panel_genre.items = genre_data
    self.label_no_genre_filters.visible = False

  def button_add_origin_click(self, **event_args):
    new_entry = {"ModelID":cur_model_id, "Type":"origin", 'Column':self.drop_down_add_origin.selected_value, "Operator":"is", 'Value':self.drop_down_add_value2.selected_value}
    origin_data = self.repeating_panel_origin.items
    if origin_data is None:
      origin_data = [new_entry]
    else:
      origin_data.append(new_entry)    
    self.repeating_panel_origin.items = origin_data
    self.label_no_origin_filters.visible = False
