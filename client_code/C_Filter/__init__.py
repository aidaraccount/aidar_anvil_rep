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
      if filter["Operator"] in (">=", "<="):
        element = getattr(self, my_dict[f'{filter["Column"]} {filter["Operator"]}'], None)
        element.text = filter["Value"]

    # Genre Filters
    #genre_data = [
    #              {'Genre':'Indie', 'Value':'False'},
    #              {'Genre':'Pop', 'Value':'True'}
    #             ]
    print([item for item in fil if item['Operator'] == 'is'])
    self.repeating_panel_genre.items = [item for item in fil if item['Operator'] == 'is']
  
  
  def apply_filters_click(self, **event_args):
    
    filters_json = '['
    
    # 1. General
    if self.artist_popularity_lat_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"ArtistPopularity_lat","Operator":">=","Value":"{self.artist_popularity_lat_min.text}"}},'
    if self.artist_popularity_lat_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"ArtistPopularity_lat","Operator":"<=","Value":"{self.artist_popularity_lat_max.text}"}},'
    if self.artist_follower_lat_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"ArtistFollower_lat","Operator":">=","Value":"{self.artist_follower_lat_min.text}"}},'
    if self.artist_follower_lat_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"ArtistFollower_lat","Operator":"<=","Value":"{self.artist_follower_lat_max.text}"}},'
    
    # 2. Musical Features
    if self.avg_duration_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgDuration","Operator":">=","Value":"{self.avg_duration_min.text}"}},'
    if self.avg_duration_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgDuration","Operator":"<=","Value":"{self.avg_duration_max.text}"}},'
    
    if self.avg_danceability_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgDanceability","Operator":">=","Value":"{int(self.avg_danceability_min.text)/100}"}},'
    if self.avg_danceability_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgDanceability","Operator":">=","Value":"{int(self.avg_danceability_max.text)/100}"}},'
    
    if self.avg_energy_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgEnergy","Operator":">=","Value":"{int(self.avg_energy_min.text)/100}"}},'
    if self.avg_energy_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgEnergy","Operator":">=","Value":"{int(self.avg_energy_max.text)/100}"}},'

    tonleiter = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
    if self.avg_key_min.selected_value != '': filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgKey","Operator":">=","Value":"{tonleiter.index(self.avg_key_min.selected_value)}"}},'
    if self.avg_key_max.selected_value != '': filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgKey","Operator":">=","Value":"{tonleiter.index(self.avg_key_max.selected_value)}"}},'
    
    if self.avg_loudness_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgLoudness","Operator":">=","Value":"{self.avg_loudness_min.text}"}},'
    if self.avg_loudness_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgLoudness","Operator":"<=","Value":"{self.avg_loudness_max.text}"}},'
    
    if self.avg_mode_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgMode","Operator":">=","Value":"{int(self.avg_mode_min.text)/100}"}},'
    if self.avg_mode_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgMode","Operator":">=","Value":"{int(self.avg_mode_max.text)/100}"}},'
    
    if self.avg_speechiness_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgSpeechiness","Operator":">=","Value":"{int(self.avg_speechiness_min.text)/100}"}},'
    if self.avg_speechiness_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgSpeechiness","Operator":">=","Value":"{int(self.avg_speechiness_max.text)/100}"}},'
    
    if self.avg_acousticness_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgAcousticness","Operator":">=","Value":"{int(self.avg_acousticness_min.text)/100}"}},'
    if self.avg_acousticness_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgAcousticness","Operator":">=","Value":"{int(self.avg_acousticness_max.text)/100}"}},'
    
    if self.avg_instrumentalness_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgInstrumentalness","Operator":">=","Value":"{int(self.avg_instrumentalness_min.text)/100}"}},'
    if self.avg_instrumentalness_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgInstrumentalness","Operator":">=","Value":"{int(self.avg_instrumentalness_max.text)/100}"}},'
    
    if self.avg_liveness_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgLiveness","Operator":">=","Value":"{int(self.avg_liveness_min.text)/100}"}},'
    if self.avg_liveness_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgLiveness","Operator":">=","Value":"{int(self.avg_liveness_max.text)/100}"}},'

    if self.avg_valence_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgValence","Operator":">=","Value":"{int(self.avg_valence_min.text)/100}"}},'
    if self.avg_valence_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgValence","Operator":">=","Value":"{int(self.avg_valence_max.text)/100}"}},'
    
    if self.avg_tempo_min.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgTempo","Operator":">=","Value":"{self.avg_tempo_min.text}"}},'
    if self.avg_tempo_max.text is not None: filters_json += f'{{"ModelID":"{cur_model_id}","Column":"AvgTempo","Operator":"<=","Value":"{self.avg_tempo_max.text}"}},'

    # 3. Genres
    genre_data = self.repeating_panel_genre.items

    if len(genre_data) > 0:
      for element in genre_data:
        print(element)
        filters_json += f'{{"ModelID":"{cur_model_id}","Column":"{element["Genre"]}","Operator":"is","Value":"{element["Value"]}"}},'
    

    # 4. Origins
    if(self.check_box_euro_t.checked == True): euro = 1
    elif(self.check_box_euro_f.checked == True): euro = 0
    else: euro = None
    if(self.check_box_asian_t.checked == True): asian = 1
    elif(self.check_box_asian_f.checked == True): asian = 0
    else: asian = None
    if(self.check_box_american_t.checked == True): american = 1
    elif(self.check_box_american_f.checked == True): american = 0
    else: american = None
    if(self.check_box_african_t.checked == True): african = 1
    elif(self.check_box_african_f.checked == True): african = 0
    else: african = None
    if(self.check_box_australian_t.checked == True): australian = 1
    elif(self.check_box_australian_f.checked == True): australian = 0
    else: australian = None
    if(self.check_box_canadian_t.checked == True): canadian = 1
    elif(self.check_box_canadian_f.checked == True): canadian = 0
    else: canadian = None
    if(self.check_box_uk_t.checked == True): uk = 1
    elif(self.check_box_uk_f.checked == True): uk = 0
    else: uk = None
    if(self.check_box_german_t.checked == True): german = 1
    elif(self.check_box_german_f.checked == True): german = 0
    else: german = None
    if(self.check_box_austrian_t.checked == True): austrian = 1
    elif(self.check_box_austrian_f.checked == True): austrian = 0
    else: austrian = None
    if(self.check_box_danish_t.checked == True): danish = 1
    elif(self.check_box_danish_f.checked == True): danish = 0
    else: danish = None
    if(self.check_box_swiss_t.checked == True): swiss = 1
    elif(self.check_box_swiss_f.checked == True): swiss = 0
    else: swiss = None
    if(self.check_box_swedish_t.checked == True): swedish = 1
    elif(self.check_box_swedish_f.checked == True): swedish = 0
    else: swedish = None
    if(self.check_box_finnish_t.checked == True): finnish = 1
    elif(self.check_box_finnish_f.checked == True): finnish = 0
    else: finnish = None
    if(self.check_box_norwegian_t.checked == True): norwegian = 1
    elif(self.check_box_norwegian_f.checked == True): norwegian = 0
    else: norwegian = None
    if(self.check_box_dutch_t.checked == True): dutch = 1
    elif(self.check_box_dutch_f.checked == True): dutch = 0
    else: dutch = None
    if(self.check_box_scottish_t.checked == True): scottish = 1
    elif(self.check_box_scottish_f.checked == True): scottish = 0
    else: scottish = None
    if(self.check_box_irish_t.checked == True): irish = 1
    elif(self.check_box_irish_f.checked == True): irish = 0
    else: irish = None
    if(self.check_box_czech_t.checked == True): czech = 1
    elif(self.check_box_czech_f.checked == True): czech = 0
    else: czech = None
    if(self.check_box_spanish_t.checked == True): spanish = 1
    elif(self.check_box_spanish_f.checked == True): spanish = 0
    else: spanish = None
    if(self.check_box_french_t.checked == True): french = 1
    elif(self.check_box_french_f.checked == True): french = 0
    else: french = None
    if(self.check_box_italian_t.checked == True): italian = 1
    elif(self.check_box_italian_f.checked == True): italian = 0
    else: italian = None
    if(self.check_box_russian_t.checked == True): russian = 1
    elif(self.check_box_russian_f.checked == True): russian = 0
    else: russian = None
    if(self.check_box_turkish_t.checked == True): turkish = 1
    elif(self.check_box_turkish_f.checked == True): turkish = 0
    else: turkish = None
    if(self.check_box_ukrainian_t.checked == True): ukrainian = 1
    elif(self.check_box_ukrainian_f.checked == True): ukrainian = 0
    else: ukrainian = None
    if(self.check_box_polish_t.checked == True): polish = 1
    elif(self.check_box_polish_f.checked == True): polish = 0
    else: polish = None
    if(self.check_box_greek_t.checked == True): greek = 1
    elif(self.check_box_greek_f.checked == True): greek = 0
    else: greek = None
    if(self.check_box_icelandic_t.checked == True): icelandic = 1
    elif(self.check_box_icelandic_f.checked == True): icelandic = 0
    else: icelandic = None
    if(self.check_box_indian_t.checked == True): indian = 1
    elif(self.check_box_indian_f.checked == True): indian = 0
    else: indian = None
    if(self.check_box_taiwan_t.checked == True): taiwan = 1
    elif(self.check_box_taiwan_f.checked == True): taiwan = 0
    else: taiwan = None
    if(self.check_box_chinese_t.checked == True): chinese = 1
    elif(self.check_box_chinese_f.checked == True): chinese = 0
    else: chinese = None
    if(self.check_box_malaysian_t.checked == True): malaysian = 1
    elif(self.check_box_malaysian_f.checked == True): malaysian = 0
    else: malaysian = None
    if(self.check_box_indonesian_t.checked == True): indonesian = 1
    elif(self.check_box_indonesian_f.checked == True): indonesian = 0
    else: indonesian = None
    if(self.check_box_vietnamese_t.checked == True): vietnamese = 1
    elif(self.check_box_vietnamese_f.checked == True): vietnamese = 0
    else: vietnamese = None
    if(self.check_box_japanese_t.checked == True): japanese = 1
    elif(self.check_box_japanese_f.checked == True): japanese = 0
    else: japanese = None
    if(self.check_box_korean_t.checked == True): korean = 1
    elif(self.check_box_korean_f.checked == True): korean = 0
    else: korean = None
    if(self.check_box_mexican_t.checked == True): mexican = 1
    elif(self.check_box_mexican_f.checked == True): mexican = 0
    else: mexican = None
    if(self.check_box_dominican_t.checked == True): dominican = 1
    elif(self.check_box_dominican_f.checked == True): dominican = 0
    else: dominican = None
    if(self.check_box_puerto_rican_t.checked == True): puerto_rican = 1
    elif(self.check_box_puerto_rican_f.checked == True): puerto_rican = 0
    else: puerto_rican = None
    if(self.check_box_brazilian_t.checked == True): brazilian = 1
    elif(self.check_box_brazilian_f.checked == True): brazilian = 0
    else: brazilian = None
    if(self.check_box_argentin_t.checked == True): argentin = 1
    elif(self.check_box_argentin_f.checked == True): argentin = 0
    else: argentin = None
    if(self.check_box_albanian_t.checked == True): albanian = 1
    elif(self.check_box_albanian_f.checked == True): albanian = 0
    else: albanian = None
    if(self.check_box_peruan_t.checked == True): peruan = 1
    elif(self.check_box_peruan_f.checked == True): peruan = 0
    else: peruan = None
    if(self.check_box_moroccan_t.checked == True): moroccan = 1
    elif(self.check_box_moroccan_f.checked == True): moroccan = 0
    else: moroccan = None
    if(self.check_box_jamaican_t.checked == True): jamaican = 1
    elif(self.check_box_jamaican_f.checked == True): jamaican = 0
    else: jamaican = None
    if(self.check_box_arab_t.checked == True): arab = 1
    elif(self.check_box_arab_f.checked == True): arab = 0
    else: arab = None
    if(self.check_box_armenian_t.checked == True): armenian = 1
    elif(self.check_box_armenian_f.checked == True): armenian = 0
    else: armenian = None
    if(self.check_box_israeli_t.checked == True): israeli = 1
    elif(self.check_box_israeli_f.checked == True): israeli = 0
    else: israeli = None

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
    new_entry = {'Genre': self.drop_down_add_genre.selected_value, 'Value': self.drop_down_add_value.selected_value}
    genre_data.append(new_entry)    
    self.repeating_panel_genre.items = genre_data
