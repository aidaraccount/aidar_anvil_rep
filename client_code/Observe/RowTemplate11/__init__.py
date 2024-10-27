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
    # print(f"{datetime.now()}: Observe Row 1", flush=True)
    
    # Any code you write here will run before the form opens.
    # name and flag
    artist_name_component = Label(text=self.item["Name"], role="artist-name-tile", spacing_above=0, spacing_below=0)
    self.Artist_Name_Details.add_component(artist_name_component)

    # print(f"{datetime.now()}: Observe Row 2", flush=True)
    if self.item["CountryCode"] == 'None' or self.item["CountryCode"] is None:
      pass
    else:
      country_flag = Image(source="https://flagcdn.com/w40/" + self.item["CountryCode"].lower() + ".png", spacing_below=0, spacing_above=0)
      country_flag.role = 'country-flag-icon'
      country_flag.tooltip = self.item["CountryCode"]
      self.Artist_Name_Details.add_component(country_flag)

    self.gender_birth_spacer.visible = False
    # birt date
    if self.item["BirthDate"] is None:
      self.birthday.visible = False
    else:
      self.gender_birth_spacer.visible = True
      self.birthday.visible = True
      self.birthday.text = self.convert_date(self.item["BirthDate"])

    # gender
    if self.item["Gender"] is None:
      self.gender.visible = False
    else:
      self.gender_birth_spacer.visible = True
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
      for g in (range(0, min(len(genres_list), 3))):
        genre_label = Label(text=genres_list[g])
        genre_label.role = 'genre-box'
        self.flow_panel_genre_tile.add_component(genre_label)
      if len(genres_list) > 3:
        genre_label = Label(text='...')
        genre_label.role = 'genre-box'
        self.flow_panel_genre_tile.add_component(genre_label)
    
    # print(f"{datetime.now()}: Observe Row 3", flush=True)
    # stats
    # label_sp_fol: fcg.ev_sp_fol_30, fcg.ev_sp_li_30, fcg.ev_tt_fol_30
    if self.item["ArtistFollower_lat"] == 'None':
      self.label_sp_fol.content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">-</span>"""
    else:
      self.label_sp_fol.content = f"""<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">{get_open_form().shorten_number(self.item["ArtistFollower_lat"])}</span>"""
      
      if self.item["ev_sp_fol_30"] is not None:
        val = int("{:.0f}".format(round(float(self.item["ev_sp_fol_30"])*100, 0)))
        if val >= 3:
          ev = f"""+{val}%"""
          "{:.0f}".format(round(float(self.item["ev_sp_fol_30"])*100, 0))
          col = 'green'
        elif val < 0:
          ev = f"""{val}%"""
          col = 'red'
        else:
          ev = f"""+{val}%"""
          col = 'grey'
        
        self.label_sp_fol.content = self.label_sp_fol.content + f"""<br><span style="font-size: 16px; color: {col};">{ev}</span>"""

    # print(f"{datetime.now()}: Observe Row 3a", flush=True)
    # label_mtl_lis:
    if self.item["SpotifyMtlListeners_lat"] == 'None':
      self.label_mtl_lis.content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">-</span>"""
    else:
      self.label_mtl_lis.content = f"""<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">{get_open_form().shorten_number(self.item["SpotifyMtlListeners_lat"])}</span>"""
      
      if self.item["ev_sp_li_30"] is not None:
        val = int("{:.0f}".format(round(float(self.item["ev_sp_li_30"])*100, 0)))
        if val >= 3:
          ev = f"""+{val}%"""
          "{:.0f}".format(round(float(self.item["ev_sp_li_30"])*100, 0))
          col = 'green'
        elif val < 0:
          ev = f"""{val}%"""
          col = 'red'
        else:
          ev = f"""+{val}%"""
          col = 'grey'
        
        self.label_mtl_lis.content = self.label_mtl_lis.content + f"""<br><span style="font-size: 16px; color: {col};">{ev}</span>"""
    
    # print(f"{datetime.now()}: Observe Row 3b", flush=True)
    # label_tiktok_fol:
    if self.item["TikTokFollower_lat"] == 'None':
      self.label_tiktok_fol.content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">-</span>"""
    else:
      self.label_tiktok_fol.content = f"""<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">{get_open_form().shorten_number(self.item["TikTokFollower_lat"])}</span>"""
      
      if self.item["ev_tt_fol_30"] is not None:
        val = int("{:.0f}".format(round(float(self.item["ev_tt_fol_30"])*100, 0)))
        if val >= 3:
          ev = f"""+{val}%"""
          "{:.0f}".format(round(float(self.item["ev_tt_fol_30"])*100, 0))
          col = 'green'
        elif val < 0:
          ev = f"""{val}%"""
          col = 'red'
        else:
          ev = f"""+{val}%"""
          col = 'grey'
        
        self.label_tiktok_fol.content = self.label_tiktok_fol.content + f"""<br><span style="font-size: 16px; color: {col};">{ev}</span>"""

    # INVIVIDUAL STATS
    # self.nav_grow_fits.role = 'section_buttons_focused'
    print(self.item["Type"])
    if self.item["Type"] == 'top_fits':
      self.label_indiv.content = 'Spotify<br>Pop.'
      self.label_indiv_cont.role = 'header-5'
      font_size = 20
      var = get_open_form().shorten_number(self.item["ArtistPopularity_lat"])
      ev_var = self.item["ev_sp_pop_30"]
    elif self.item["Type"] == 'grow_fits':
      self.label_indiv.content = 'Growth<br>Fit'
      self.label_indiv_cont.role = 'header-5'
      font_size = 20
      var = str(round(self.item["prediction_growth"]/7*100)) + '%'
      ev_var = None
    elif self.item["Type"] == 'release_fits':
      self.label_indiv.content = 'Latest<br>Release'
      self.label_indiv_cont.role = 'header-6'
      font_size = 18
      var = self.convert_date(str(self.item["LastReleaseDate"]))
      ev_var = None
      
    if var == 'None':
      self.label_indiv_cont.content = """<span style="font-family: GS-regular; font-size: 20px; color: rgb(255, 255, 255);">-</span>"""
    else:
      self.label_indiv_cont.content = f"""<span style="font-family: GS-regular; font-size: {font_size}px; color: rgb(255, 255, 255);">{var}</span>"""
      
      if ev_var is not None:
        val = int("{:.0f}".format(round(float(ev_var)*100, 0)))
        if val >= 3:
          ev = f"""+{val}%"""
          "{:.0f}".format(round(float(ev_var)*100, 0))
          col = 'green'
        elif val < 0:
          ev = f"""{val}%"""
          col = 'red'
        else:
          ev = f"""+{val}%"""
          col = 'grey'
        
        self.label_indiv_cont.content = self.label_indiv_cont.content + f"""<br><span style="font-size: 16px; color: {col};">{ev}</span>"""



    
    # print(f"{datetime.now()}: Observe Row 4", flush=True)
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
    # print(f"{datetime.now()}: Observe Row 5", flush=True)


  def pic_click(self, **event_args):
    click_link(self.link_pic, f'artists?artist_id={self.item["ArtistID"]}', event_args)

  def name_click(self, **event_args):
    click_link(self.link_name, f'artists?artist_id={self.item["ArtistID"]}', event_args)


  def convert_date(self, date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%b %d, %Y')
