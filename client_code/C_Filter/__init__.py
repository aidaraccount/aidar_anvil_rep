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
    fil = json.loads(anvil.server.call('get_filters', cur_model_id))
    # 1. General
    self.artist_popularity_lat_min.text = fil["artist_popularity_lat_min"]
    self.artist_popularity_lat_max.text = fil["artist_popularity_lat_max"]
    self.artist_follower_lat_min.text = fil["artist_follower_lat_min"]
    self.artist_follower_lat_max.text = fil["artist_follower_lat_max"]
    # 2. Musical Features
    # a) prepare key
    tonleiter = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
    if fil["avg_key_min"] == 'None': key_min = None
    else: key_min = tonleiter[int(round(float(fil["avg_key_min"]),0))]
    if fil["avg_key_max"] == 'None': key_max = None
    else: key_max = tonleiter[int(round(float(fil["avg_key_max"]),0))]
    # b) fill everything
    self.avg_duration_min.text = fil["avg_duration_min"]
    self.avg_duration_max.text = fil["avg_duration_max"]
    self.avg_danceability_min.text = fil["avg_danceability_min"]
    self.avg_danceability_max.text = fil["avg_danceability_max"]
    self.avg_energy_min.text = fil["avg_energy_min"]
    self.avg_energy_max.text = fil["avg_energy_max"]    
    self.avg_key_min.text = key_min
    self.avg_key_max.text = key_max
    self.avg_loudness_min.text = fil["avg_loudness_min"]
    self.avg_loudness_max.text = fil["avg_loudness_max"]
    self.avg_mode_min.text = fil["avg_mode_min"]
    self.avg_mode_max.text = fil["avg_mode_max"]
    self.avg_speechiness_min.text = fil["avg_speechiness_min"]
    self.avg_speechiness_max.text = fil["avg_speechiness_max"]
    self.avg_acousticness_min.text = fil["avg_acousticness_min"]
    self.avg_acousticness_max.text = fil["avg_acousticness_max"]
    self.avg_instrumentalness_min.text = fil["avg_instrumentalness_min"]
    self.avg_instrumentalness_max.text = fil["avg_instrumentalness_max"]
    self.avg_liveness_min.text = fil["avg_liveness_min"]
    self.avg_liveness_max.text = fil["avg_liveness_max"]
    self.avg_valence_min.text = fil["avg_valence_min"]
    self.avg_valence_max.text = fil["avg_valence_max"]
    self.avg_tempo_min.text = fil["avg_tempo_min"]
    self.avg_tempo_max.text = fil["avg_tempo_max"]
    
    if(fil["pop"] == '1'): self.check_box_pop_t.checked = True
    elif(fil["pop"] == '0'): self.check_box_pop_f.checked = True
    if(fil["rock"] == '1'): self.check_box_rock_t.checked = True
    elif(fil["rock"] == '0'): self.check_box_rock_f.checked = True
    if(fil["indie"] == '1'): self.check_box_indie_t.checked = True
    elif(fil["indie"] == '0'): self.check_box_indie_f.checked = True
    if(fil["country"] == '1'): self.check_box_country_t.checked = True
    elif(fil["country"] == '0'): self.check_box_country_f.checked = True
    if(fil["classic"] == '1'): self.check_box_classic_t.checked = True
    elif(fil["classic"] == '0'): self.check_box_classic_f.checked = True
    if(fil["latin"] == '1'): self.check_box_latin_t.checked = True
    elif(fil["latin"] == '0'): self.check_box_latin_f.checked = True
    if(fil["soul"] == '1'): self.check_box_soul_t.checked = True
    elif(fil["soul"] == '0'): self.check_box_soul_f.checked = True
    if(fil["house"] == '1'): self.check_box_house_t.checked = True
    elif(fil["house"] == '0'): self.check_box_house_f.checked = True
    if(fil["funk"] == '1'): self.check_box_funk_t.checked = True
    elif(fil["funk"] == '0'): self.check_box_funk_f.checked = True
    if(fil["disco"] == '1'): self.check_box_disco_t.checked = True
    elif(fil["disco"] == '0'): self.check_box_disco_f.checked = True
    if(fil["schlager"] == '1'): self.check_box_schlager_t.checked = True
    elif(fil["schlager"] == '0'): self.check_box_schlager_f.checked = True
    if(fil["edm"] == '1'): self.check_box_edm_t.checked = True
    elif(fil["edm"] == '0'): self.check_box_edm_f.checked = True
    if(fil["electro"] == '1'): self.check_box_electro_t.checked = True
    elif(fil["electro"] == '0'): self.check_box_electro_f.checked = True
    if(fil["dance"] == '1'): self.check_box_dance_t.checked = True
    elif(fil["dance"] == '0'): self.check_box_dance_f.checked = True
    if(fil["hip_hop"] == '1'): self.check_box_hip_hop_t.checked = True
    elif(fil["hip_hop"] == '0'): self.check_box_hip_hop_f.checked = True
    if(fil["rap"] == '1'): self.check_box_rap_t.checked = True
    elif(fil["rap"] == '0'): self.check_box_rap_f.checked = True
    if(fil["reggae"] == '1'): self.check_box_reggae_t.checked = True
    elif(fil["reggae"] == '0'): self.check_box_reggae_f.checked = True
    if(fil["jazz"] == '1'): self.check_box_jazz_t.checked = True
    elif(fil["jazz"] == '0'): self.check_box_jazz_f.checked = True
    if(fil["blues"] == '1'): self.check_box_blues_t.checked = True
    elif(fil["blues"] == '0'): self.check_box_blues_f.checked = True
    if(fil["folk"] == '1'): self.check_box_folk_t.checked = True
    elif(fil["folk"] == '0'): self.check_box_folk_f.checked = True
    if(fil["punk"] == '1'): self.check_box_punk_t.checked = True
    elif(fil["punk"] == '0'): self.check_box_punk_f.checked = True
    if(fil["metal"] == '1'): self.check_box_metal_t.checked = True
    elif(fil["metal"] == '0'): self.check_box_metal_f.checked = True
    if(fil["euro"] == '1'): self.check_box_euro_t.checked = True
    elif(fil["euro"] == '0'): self.check_box_euro_f.checked = True
    if(fil["asian"] == '1'): self.check_box_asian_t.checked = True
    elif(fil["asian"] == '0'): self.check_box_asian_f.checked = True
    if(fil["american"] == '1'): self.check_box_american_t.checked = True
    elif(fil["american"] == '0'): self.check_box_american_f.checked = True
    if(fil["african"] == '1'): self.check_box_african_t.checked = True
    elif(fil["african"] == '0'): self.check_box_african_f.checked = True
    if(fil["australian"] == '1'): self.check_box_australian_t.checked = True
    elif(fil["australian"] == '0'): self.check_box_australian_f.checked = True
    if(fil["canadian"] == '1'): self.check_box_canadian_t.checked = True
    elif(fil["canadian"] == '0'): self.check_box_canadian_f.checked = True
    if(fil["uk"] == '1'): self.check_box_uk_t.checked = True
    elif(fil["uk"] == '0'): self.check_box_uk_f.checked = True
    if(fil["german"] == '1'): self.check_box_german_t.checked = True
    elif(fil["german"] == '0'): self.check_box_german_f.checked = True
    if(fil["austrian"] == '1'): self.check_box_austrian_t.checked = True
    elif(fil["austrian"] == '0'): self.check_box_austrian_f.checked = True
    if(fil["danish"] == '1'): self.check_box_danish_t.checked = True
    elif(fil["danish"] == '0'): self.check_box_danish_f.checked = True
    if(fil["swiss"] == '1'): self.check_box_swiss_t.checked = True
    elif(fil["swiss"] == '0'): self.check_box_swiss_f.checked = True
    if(fil["swedish"] == '1'): self.check_box_swedish_t.checked = True
    elif(fil["swedish"] == '0'): self.check_box_swedish_f.checked = True
    if(fil["finnish"] == '1'): self.check_box_finnish_t.checked = True
    elif(fil["finnish"] == '0'): self.check_box_finnish_f.checked = True
    if(fil["norwegian"] == '1'): self.check_box_norwegian_t.checked = True
    elif(fil["norwegian"] == '0'): self.check_box_norwegian_f.checked = True
    if(fil["dutch"] == '1'): self.check_box_dutch_t.checked = True
    elif(fil["dutch"] == '0'): self.check_box_dutch_f.checked = True
    if(fil["scottish"] == '1'): self.check_box_scottish_t.checked = True
    elif(fil["scottish"] == '0'): self.check_box_scottish_f.checked = True
    if(fil["irish"] == '1'): self.check_box_irish_t.checked = True
    elif(fil["irish"] == '0'): self.check_box_irish_f.checked = True
    if(fil["czech"] == '1'): self.check_box_czech_t.checked = True
    elif(fil["czech"] == '0'): self.check_box_czech_f.checked = True
    if(fil["spanish"] == '1'): self.check_box_spanish_t.checked = True
    elif(fil["spanish"] == '0'): self.check_box_spanish_f.checked = True
    if(fil["french"] == '1'): self.check_box_french_t.checked = True
    elif(fil["french"] == '0'): self.check_box_french_f.checked = True
    if(fil["italian"] == '1'): self.check_box_italian_t.checked = True
    elif(fil["italian"] == '0'): self.check_box_italian_f.checked = True
    if(fil["russian"] == '1'): self.check_box_russian_t.checked = True
    elif(fil["russian"] == '0'): self.check_box_russian_f.checked = True
    if(fil["turkish"] == '1'): self.check_box_turkish_t.checked = True
    elif(fil["turkish"] == '0'): self.check_box_turkish_f.checked = True
    if(fil["ukrainian"] == '1'): self.check_box_ukrainian_t.checked = True
    elif(fil["ukrainian"] == '0'): self.check_box_ukrainian_f.checked = True
    if(fil["polish"] == '1'): self.check_box_polish_t.checked = True
    elif(fil["polish"] == '0'): self.check_box_polish_f.checked = True
    if(fil["greek"] == '1'): self.check_box_greek_t.checked = True
    elif(fil["greek"] == '0'): self.check_box_greek_f.checked = True
    if(fil["icelandic"] == '1'): self.check_box_icelandic_t.checked = True
    elif(fil["icelandic"] == '0'): self.check_box_icelandic_f.checked = True
    if(fil["indian"] == '1'): self.check_box_indian_t.checked = True
    elif(fil["indian"] == '0'): self.check_box_indian_f.checked = True
    if(fil["taiwan"] == '1'): self.check_box_taiwan_t.checked = True
    elif(fil["taiwan"] == '0'): self.check_box_taiwan_f.checked = True
    if(fil["chinese"] == '1'): self.check_box_chinese_t.checked = True
    elif(fil["chinese"] == '0'): self.check_box_chinese_f.checked = True
    if(fil["malaysian"] == '1'): self.check_box_malaysian_t.checked = True
    elif(fil["malaysian"] == '0'): self.check_box_malaysian_f.checked = True
    if(fil["indonesian"] == '1'): self.check_box_indonesian_t.checked = True
    elif(fil["indonesian"] == '0'): self.check_box_indonesian_f.checked = True
    if(fil["vietnamese"] == '1'): self.check_box_vietnamese_t.checked = True
    elif(fil["vietnamese"] == '0'): self.check_box_vietnamese_f.checked = True
    if(fil["japanese"] == '1'): self.check_box_japanese_t.checked = True
    elif(fil["japanese"] == '0'): self.check_box_japanese_f.checked = True
    if(fil["korean"] == '1'): self.check_box_korean_t.checked = True
    elif(fil["korean"] == '0'): self.check_box_korean_f.checked = True
    if(fil["mexican"] == '1'): self.check_box_mexican_t.checked = True
    elif(fil["mexican"] == '0'): self.check_box_mexican_f.checked = True
    if(fil["dominican"] == '1'): self.check_box_dominican_t.checked = True
    elif(fil["dominican"] == '0'): self.check_box_dominican_f.checked = True
    if(fil["puerto_rican"] == '1'): self.check_box_puerto_rican_t.checked = True
    elif(fil["puerto_rican"] == '0'): self.check_box_puerto_rican_f.checked = True
    if(fil["brazilian"] == '1'): self.check_box_brazilian_t.checked = True
    elif(fil["brazilian"] == '0'): self.check_box_brazilian_f.checked = True
    if(fil["argentin"] == '1'): self.check_box_argentin_t.checked = True
    elif(fil["argentin"] == '0'): self.check_box_argentin_f.checked = True
    if(fil["albanian"] == '1'): self.check_box_albanian_t.checked = True
    elif(fil["albanian"] == '0'): self.check_box_albanian_f.checked = True
    if(fil["peruan"] == '1'): self.check_box_peruan_t.checked = True
    elif(fil["peruan"] == '0'): self.check_box_peruan_f.checked = True
    if(fil["moroccan"] == '1'): self.check_box_moroccan_t.checked = True
    elif(fil["moroccan"] == '0'): self.check_box_moroccan_f.checked = True
    if(fil["jamaican"] == '1'): self.check_box_jamaican_t.checked = True
    elif(fil["jamaican"] == '0'): self.check_box_jamaican_f.checked = True
    if(fil["arab"] == '1'): self.check_box_arab_t.checked = True
    elif(fil["arab"] == '0'): self.check_box_arab_f.checked = True
    if(fil["armenian"] == '1'): self.check_box_armenian_t.checked = True
    elif(fil["armenian"] == '0'): self.check_box_armenian_f.checked = True
    if(fil["israeli"] == '1'): self.check_box_israeli_t.checked = True
    elif(fil["israeli"] == '0'): self.check_box_israeli_f.checked = True

  
  def apply_filters_click(self, **event_args):
    # 1. General
    artist_popularity_lat_min = self.artist_popularity_lat_min.text
    artist_popularity_lat_max = self.artist_popularity_lat_max.text
    artist_follower_lat_min = self.artist_follower_lat_min.text
    artist_follower_lat_max = self.artist_follower_lat_max.text
    # 2. Musical Features
    # a) prepare key
    tonleiter = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
    if self.avg_key_min.text == '': avg_key_min = self.avg_key_min.text
    else: avg_key_min = tonleiter.index(self.avg_key_min.text)
    if self.avg_key_max.text == '': avg_key_max = self.avg_key_max.text
    else: avg_key_max = tonleiter.index(self.avg_key_max.text)
    print(self.avg_key_min.text)
    print(avg_key_min)
    
    # b) fill everything
    avg_duration_min = self.avg_duration_min.text
    avg_duration_max = self.avg_duration_max.text
    avg_danceability_min = self.avg_danceability_min.text
    avg_danceability_max = self.avg_danceability_max.text
    avg_energy_min = self.avg_energy_min.text
    avg_energy_max = self.avg_energy_max.text
    #avg_key_min = self.avg_key_min.text
    #avg_key_max = self.avg_key_max.text
    avg_loudness_min = self.avg_loudness_min.text
    avg_loudness_max = self.avg_loudness_max.text
    avg_mode_min = self.avg_mode_min.text
    avg_mode_max = self.avg_mode_max.text
    avg_speechiness_min = self.avg_speechiness_min.text
    avg_speechiness_max = self.avg_speechiness_max.text
    avg_acousticness_min = self.avg_acousticness_min.text
    avg_acousticness_max = self.avg_acousticness_max.text
    avg_instrumentalness_min = self.avg_instrumentalness_min.text
    avg_instrumentalness_max = self.avg_instrumentalness_max.text
    avg_liveness_min = self.avg_liveness_min.text
    avg_liveness_max = self.avg_liveness_max.text
    avg_valence_min = self.avg_valence_min.text
    avg_valence_max = self.avg_valence_max.text
    avg_tempo_min = self.avg_tempo_min.text
    avg_tempo_max = self.avg_tempo_max.text

    if(self.check_box_pop_t.checked == True): pop = 1
    elif(self.check_box_pop_f.checked == True): pop = 0
    else: pop = None
    if(self.check_box_rock_t.checked == True): rock = 1
    elif(self.check_box_rock_f.checked == True): rock = 0
    else: rock = None
    if(self.check_box_indie_t.checked == True): indie = 1
    elif(self.check_box_indie_f.checked == True): indie = 0
    else: indie = None
    if(self.check_box_country_t.checked == True): country = 1
    elif(self.check_box_country_f.checked == True): country = 0
    else: country = None
    if(self.check_box_classic_t.checked == True): classic = 1
    elif(self.check_box_classic_f.checked == True): classic = 0
    else: classic = None
    if(self.check_box_latin_t.checked == True): latin = 1
    elif(self.check_box_latin_f.checked == True): latin = 0
    else: latin = None
    if(self.check_box_soul_t.checked == True): soul = 1
    elif(self.check_box_soul_f.checked == True): soul = 0
    else: soul = None
    if(self.check_box_house_t.checked == True): house = 1
    elif(self.check_box_house_f.checked == True): house = 0
    else: house = None
    if(self.check_box_funk_t.checked == True): funk = 1
    elif(self.check_box_funk_f.checked == True): funk = 0
    else: funk = None
    if(self.check_box_disco_t.checked == True): disco = 1
    elif(self.check_box_disco_f.checked == True): disco = 0
    else: disco = None
    if(self.check_box_schlager_t.checked == True): schlager = 1
    elif(self.check_box_schlager_f.checked == True): schlager = 0
    else: schlager = None
    if(self.check_box_edm_t.checked == True): edm = 1
    elif(self.check_box_edm_f.checked == True): edm = 0
    else: edm = None
    if(self.check_box_electro_t.checked == True): electro = 1
    elif(self.check_box_electro_f.checked == True): electro = 0
    else: electro = None
    if(self.check_box_dance_t.checked == True): dance = 1
    elif(self.check_box_dance_f.checked == True): dance = 0
    else: dance = None
    if(self.check_box_hip_hop_t.checked == True): hip_hop = 1
    elif(self.check_box_hip_hop_f.checked == True): hip_hop = 0
    else: hip_hop = None
    if(self.check_box_rap_t.checked == True): rap = 1
    elif(self.check_box_rap_f.checked == True): rap = 0
    else: rap = None
    if(self.check_box_reggae_t.checked == True): reggae = 1
    elif(self.check_box_reggae_f.checked == True): reggae = 0
    else: reggae = None
    if(self.check_box_jazz_t.checked == True): jazz = 1
    elif(self.check_box_jazz_f.checked == True): jazz = 0
    else: jazz = None
    if(self.check_box_blues_t.checked == True): blues = 1
    elif(self.check_box_blues_f.checked == True): blues = 0
    else: blues = None
    if(self.check_box_folk_t.checked == True): folk = 1
    elif(self.check_box_folk_f.checked == True): folk = 0
    else: folk = None
    if(self.check_box_punk_t.checked == True): punk = 1
    elif(self.check_box_punk_f.checked == True): punk = 0
    else: punk = None
    if(self.check_box_metal_t.checked == True): metal = 1
    elif(self.check_box_metal_f.checked == True): metal = 0
    else: metal = None
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
    
    anvil.server.call('change_filters',
                      cur_model_id,
                      artist_popularity_lat_min,
                      artist_popularity_lat_max,
                      artist_follower_lat_min,
                      artist_follower_lat_max,
                      avg_duration_min,
                      avg_duration_max,
                      avg_danceability_min,
                      avg_danceability_max,
                      avg_energy_min,
                      avg_energy_max,
                      avg_key_min,
                      avg_key_max,
                      avg_loudness_min,
                      avg_loudness_max,
                      avg_mode_min,
                      avg_mode_max,
                      avg_speechiness_min,
                      avg_speechiness_max,
                      avg_acousticness_min,
                      avg_acousticness_max,
                      avg_instrumentalness_min,
                      avg_instrumentalness_max,
                      avg_liveness_min,
                      avg_liveness_max,
                      avg_valence_min,
                      avg_valence_max,
                      avg_tempo_min,
                      avg_tempo_max,
                      pop,
                      rock,
                      indie,
                      country,
                      classic,
                      latin,
                      soul,
                      house,
                      funk,
                      disco,
                      schlager,
                      edm,
                      electro,
                      dance,
                      hip_hop,
                      rap,
                      reggae,
                      jazz,
                      blues,
                      folk,
                      punk,
                      metal,
                      euro,
                      asian,
                      american,
                      african,
                      australian,
                      canadian,
                      uk,
                      german,
                      austrian,
                      danish,
                      swiss,
                      swedish,
                      finnish,
                      norwegian,
                      dutch,
                      scottish,
                      irish,
                      czech,
                      spanish,
                      french,
                      italian,
                      russian,
                      turkish,
                      ukrainian,
                      polish,
                      greek,
                      icelandic,
                      indian,
                      taiwan,
                      chinese,
                      malaysian,
                      indonesian,
                      vietnamese,
                      japanese,
                      korean,
                      mexican,
                      dominican,
                      puerto_rican,
                      brazilian,
                      argentin,
                      albanian,
                      peruan,
                      moroccan,
                      jamaican,
                      arab,
                      armenian,
                      israeli
                     )
    self.content_panel.clear()
    self.content_panel.add_component(C_Investigate(temp_artist_id=None))