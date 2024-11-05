from ._anvil_designer import C_ProgressMessageTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random
import string
import json
import time
import math

from anvil_extras import routing
from ..nav import click_link, click_button, load_var, save_var

from anvil import js
import anvil.js
import anvil.js.window


class C_ProgressMessage(C_ProgressMessageTemplate):
  def __init__(self, model_id, milestone, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.html = '@theme:Modelpage_html_JS.html'
    self.model_id = model_id
    infos = json.loads(anvil.server.call('get_model_stats', self.model_id))[0]
    self.infos = infos
    self.congrats_message.content = f"You have reached {milestone} ratings! \n\n Keep up the great work!"

    if (infos["total_ratings"] + infos["no_references"]) > 50:
      self.custom_HTML_prediction(infos["overall_acc"])
    else:
      self.custom_HTML_prediction_inactive((infos["total_ratings"] + infos["no_references"])/50*100)

  def custom_HTML_prediction(self, accuracy):
    custom_html = f'''
      <li class="note-display" data-note={accuracy}>
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
            <span class="label" style="font-size: 13px;">Accuracy</span>
          </div>
        </div>
      </li>
    '''
    html_panel_1 = HtmlPanel(html=custom_html)
    self.circle_slot_spot.add_component(html_panel_1)

  def custom_HTML_prediction_inactive(self, accuracy):
    custom_html = f'''
      <li class="note-display" data-note={accuracy}>
        <div class="circle">
          <svg width="140" height="140" class="circle__svg">
            <defs>
              <linearGradient id="grad2" x1="100%" y1="100%" x2="0%" y2="0%">
                <stop offset="0%" style="stop-color:#4C4C4C;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#707070;stop-opacity:1" />
              </linearGradient>
            </defs>
            <circle cx="70" cy="70" r="65" class="circle__progress_inactive circle__progress--path"></circle>
            <circle cx="70" cy="70" r="65" class="circle__progress_inactive circle__progress--fill" stroke="url(#grad2)"></circle>
          </svg>
          <div class="percent">
            <span class="percent__int">0.</span>
            <!-- <span class="percent__dec">00</span> -->
            <span class="label" style="font-size: 13px;">Trained</span>
          </div>
        </div>
      </li>
    '''
    html_panel_1 = HtmlPanel(html=custom_html)
    self.circle_slot_spot.add_component(html_panel_1)

  def Ok_button_click(self, **event_args):
    self.raise_event("x-close-alert")
    
