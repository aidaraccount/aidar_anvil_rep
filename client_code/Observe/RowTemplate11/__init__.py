from ._anvil_designer import RowTemplate11Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from anvil_extras import routing
from ...nav import click_link, click_button, logout, login_check, load_var


class RowTemplate11(RowTemplate11Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.html = '@theme:Observe.html'
    
    # Any code you write here will run before the form opens.
    # name and flag
    artist_name_component = Label(text=self.item["Name"], role="artist-name-tile", spacing_above=0, spacing_below=0)
    self.Artist_Name_Details.add_component(artist_name_component)

    print(self.item["CountryCode"])
    if self.item["CountryCode"] == 'None' or self.item["CountryCode"] is None:
      pass
    else:
      country_flag = Image(source="https://flagcdn.com/w40/" + self.item["CountryCode"].lower() + ".png", spacing_below=0, spacing_above=0)
      country_flag.role = 'country-flag-icon'
      country_flag.tooltip = self.item["CountryCode"]
      self.Artist_Name_Details.add_component(country_flag)
      

    
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

  def pic_click(self, **event_args):
    click_link(self.link_pic, f'artists?artist_id={self.item["ArtistID"]}', event_args)

  def name_click(self, **event_args):
    click_link(self.link_name, f'artists?artist_id={self.item["ArtistID"]}', event_args)
    