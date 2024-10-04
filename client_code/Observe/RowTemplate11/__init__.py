from ._anvil_designer import RowTemplate11Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import datetime
from anvil.js.window import observeFitLikelihoodCircle


from anvil_extras import routing
from ...nav import click_link, click_button, logout, login_check, load_var


class RowTemplate11(RowTemplate11Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.
    # name and flag
    artist_name_component = Label(text=self.item["Name"], role="artist-name-tile", spacing_above=0, spacing_below=0)
    self.Artist_Name_Details.add_component(artist_name_component)

    if self.item["CountryCode"] == 'None' or self.item["CountryCode"] is None:
      pass
    else:
      country_flag = Image(source="https://flagcdn.com/w40/" + self.item["CountryCode"].lower() + ".png", spacing_below=0, spacing_above=0)
      country_flag.role = 'country-flag-icon'
      country_flag.tooltip = self.item["CountryCode"]
      self.Artist_Name_Details.add_component(country_flag)
    
    # birt date
    if self.item["BirthDate"] is None:
      self.birthday.visible = False
    else:
      self.birthday.visible = True
      self.birthday.text = self.convert_date(self.item["BirthDate"])

    # gender
    if self.item["Gender"] is None:
      self.gender.visible = False
    else:
      self.gender.visible = True
      self.gender.text = self.item["Gender"]

    # line condition
    if self.item["BirthDate"] is not None and self.item["Gender"] is not None:
      self.gender_birthday_line.visible = True
    else:
      self.gender_birthday_line.visible = False

    # genres
    if self.item["genres_list"] is None:
      pass
    else:
      genres_list = self.item["genres_list"]
      for g in (range(0, min(len(genres_list), 4))):
        genre_label = Label(text=genres_list[g])
        genre_label.role = 'genre-box'
        self.flow_panel_genre_tile.add_component(genre_label)
      if len(genres_list) > 4:
        genre_label = Label(text='...')
        genre_label.role = 'genre-box'
        self.flow_panel_genre_tile.add_component(genre_label)
    
    # stats
    if self.item['ArtistFollower_lat'] is None:
      self.label_sp_fol.text = '-'
    else:
      self.label_sp_fol.text = self.shorten_number(self.item["ArtistFollower_lat"])
      
    if self.item['SpotifyMtlListeners_lat'] is None:
      self.label_mtl_fol.text = '-'
    else:
      self.label_mtl_fol.text = self.shorten_number(self.item["SpotifyMtlListeners_lat"])
      
    if self.item['TikTokFollower_lat'] is None:
      self.label_tiktok_fol.text = '-'
    else:
      self.label_tiktok_fol.text = self.shorten_number(self.item["TikTokFollower_lat"])
    
    # fit likelihood
    pred = "{:.0f}".format(round(float(self.item["Prediction"])/7*100,0))
    custom_html = f'''
    <li class="note-display" data-note="{pred}">
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
    '''
    html_panel = HtmlPanel(html=custom_html)
    self.column_panel_pred.add_component(html_panel)
    anvil.js.call_js('observeFitLikelihoodCircle')


  def pic_click(self, **event_args):
    click_link(self.link_pic, f'artists?artist_id={self.item["ArtistID"]}', event_args)

  def name_click(self, **event_args):
    click_link(self.link_name, f'artists?artist_id={self.item["ArtistID"]}', event_args)

  def shorten_number(self, num):
    thresholds = [
      (1_000_000_000_000, 'T'),  # Trillion
      (1_000_000_000, 'B'),      # Billion
      (1_000_000, 'M'),          # Million
      (1_000, 'K')               # Thousand
    ]    
    if num >= thresholds[3][0]:
      for threshold, suffix in thresholds:
        if num >= threshold:
          return f'{num / threshold:.1f}{suffix}'
    else:
      return f'{num:.0f}'

  def convert_date(self, date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%b %d, %Y')