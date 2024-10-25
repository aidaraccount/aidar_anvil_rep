from ._anvil_designer import ModelProfileTemplate
from anvil import *
import plotly.graph_objects as go
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

from ..Home import Home
from ..C_EditRefArtists import C_EditRefArtists
from ..C_AddRefArtists import C_AddRefArtists
from ..C_RefArtistsSettings import C_RefArtistsSettings
from ..C_Rating import C_Rating
from ..C_Filter import C_Filter
from ..C_LevelOfPopularity import C_LevelOfPopularity
from ..C_SubModelContribution import C_SubModelContribution

from anvil_extras import routing
from ..nav import click_link, click_button, load_var, save_var

from anvil import js
import anvil.js
import anvil.js.window


@routing.route('model_profile', url_keys=['model_id', 'section'], title='Model Profile')
class ModelProfile(ModelProfileTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.html = '@theme:Modelpage_html_JS.html'
      
    model_id_active = load_var("model_id")
    print(f"ModelProfile model_id_active: {model_id_active}")
    model_id_view = self.url_dict['model_id']
    print(self.url_dict)
    self.model_id_view = model_id_view
    save_var("model_id_view", model_id_view)
    print(f"ModelProfile model_id_view: {model_id_view}")
    section = self.url_dict['section']
    
    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    model_id_active_new = anvil.server.call('get_model_id', user["user_id"])
    print(f"ModelProfile model_id_active_new: {model_id_active_new}")
    
    # initial visibile settings
    self.model_name_text.visible = False
    self.model_description_text.visible = False
    
    self.nav_references.role = 'section_buttons_focused'
    self.sec_filters.visible = False

    # ---------------
    # HEADER LEFT
    infos = json.loads(anvil.server.call('get_model_stats', self.model_id_view))[0]
    self.infos = infos

    # check ramp-up
    if infos["ramp_up"] is True:
      routing.set_url_hash(f'model_setup?model_id={infos["model_id"]}&section=Basics', load_from_cache=False)
      
    else:
      self.retrain_date = infos["train_model_date"]
  
      # model name and description text and text boxes
      self.model_name.text = infos["model_name"]
      if infos["description"] is None:
        self.model_description.text = '-'
      else:
        self.model_description.text = infos["description"]
      if infos["creation_date"] == 'None':
        self.creation_date_value.text = '-'
      else:
        self.creation_date_value.text = infos["creation_date"]
      self.usage_date_value.text = infos["usage_date"]
  
      # activate button
      if int(self.model_id_view) == int(model_id_active_new):
        self.activated.visible = True
        self.activate.visible = False
      else:
        self.activated.visible = False
        self.activate.visible = True   
      
      # ---------------
      # HEADER RIGHT
      # stats
      self.no_references.text = infos["no_references"]
      self.total_ratings.text = infos["total_ratings"]
      self.high_ratings.text = infos["high_ratings"]
      if infos["train_model_date"] == 'None':
        self.retrain_model_date_value.text = '-'
      else:
        self.retrain_model_date_value.text = infos["train_model_date"]
      self.status.text = infos["overall_status"]
      self.status_2.text = infos["overall_status"]
  
      # Level
      self.Level_value.text = infos["overall_level"]
      
      # Overall Progress Circles
      if (infos["total_ratings"] + infos["no_references"]) > 50:
        self.custom_HTML_prediction(infos["overall_acc"])
        self.custom_HTML_prediction_2(infos["overall_acc"])
        self.overall_num_rec.visible = False
      else:
        self.custom_HTML_prediction_inactive((infos["total_ratings"] + infos["no_references"])/50*100)
        self.custom_HTML_prediction_2_inactive((infos["total_ratings"] + infos["no_references"])/50*100)
        self.overall_num_rec.visible = True
        # self.linear_panel_2.visible = True
        # self.linear_panel_2_2.visible = True
        # self.column_panel_5.visible = False
    
    
    # ---------------
    # SECCTIONS      
    # secction routing
    if section == 'Main':
      self.nav_model_click()
    elif section == 'PrevRated':
      self.nav_prev_rated_click()
    elif section == 'Filter':
      self.nav_filters_click()
    elif section == 'AddRefArtists':
      self.nav_add_references_click()
    elif section == 'LevelOfPopularity':
      self.nav_level_of_pop_click()

    self.create_ratings_histogram_chart()
    
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
    self.column_panel_5.add_component(html_panel_1)
      
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
    self.column_panel_5.add_component(html_panel_1)
    
  def custom_HTML_prediction_2(self, accuracy):
    custom_html = f'''
      <li class="note-display" data-note={accuracy}>
        <div class="circle">
          <svg width="168" height="168" class="circle__svg">
            <defs>
              <linearGradient id="grad1" x1="100%" y1="100%" x2="0%" y2="0%">
                <stop offset="0%" style="stop-color:#812675;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#E95F30;stop-opacity:1" />
              </linearGradient>
            </defs>
            <circle cx="84" cy="84" r="79" class="circle__progress circle__progress--path"></circle>
            <circle cx="84" cy="84" r="79" class="circle__progress circle__progress--fill" stroke="url(#grad1)"></circle>
          </svg>
          <div class="percent">
            <span class="percent__int">0.</span>
            <!-- <span class="percent__dec">00</span> -->
            <span class="label" style="font-size: 13px;">Accuracy</span>
          </div>
        </div>
      </li>
    '''
    html_panel_2 = HtmlPanel(html=custom_html)
    self.column_panel_2.add_component(html_panel_2)
    
  def custom_HTML_prediction_2_inactive(self, accuracy):
    custom_html = f'''
      <li class="note-display" data-note={accuracy}>
        <div class="circle">
          <svg width="168" height="168" class="circle__svg">
            <defs>
              <linearGradient id="grad2" x1="100%" y1="100%" x2="0%" y2="0%">
                <stop offset="0%" style="stop-color:#4C4C4C;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#707070;stop-opacity:1" />
              </linearGradient>
            </defs>
            <circle cx="84" cy="84" r="79" class="circle__progress_inactive circle__progress--path"></circle>
            <circle cx="84" cy="84" r="79" class="circle__progress_inactive circle__progress--fill" stroke="url(#grad2)"></circle>
          </svg>
          <div class="percent">
            <span class="percent__int">0.</span>
            <!-- <span class="percent__dec">00</span> -->
            <span class="label" style="font-size: 13px;">Trained</span>
          </div>
        </div>
      </li>
    '''
    html_panel_2 = HtmlPanel(html=custom_html)
    self.column_panel_2.add_component(html_panel_2)
    
  def custom_HTML_level_1_active(self, accuracy):
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
    similarity_html_panel = HtmlPanel(html=custom_html)
    self.similarity_submodel.add_component(similarity_html_panel)
    
  def custom_HTML_level_1_inactive(self, accuracy):
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
    similarity_html_panel = HtmlPanel(html=custom_html)
    self.similarity_submodel.add_component(similarity_html_panel)
    
  def custom_HTML_level_2_active(self, accuracy):
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
    success_html_panel = HtmlPanel(html=custom_html)
    self.success_submodel.add_component(success_html_panel)
    
  def custom_HTML_level_2_inactive(self, accuracy):
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
    success_html_panel = HtmlPanel(html=custom_html)
    self.success_submodel.add_component(success_html_panel)
    
  def custom_HTML_level_3_active(self, accuracy):
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
    fandom_html_panel = HtmlPanel(html=custom_html)
    self.fandom_submodel.add_component(fandom_html_panel)
    
  def custom_HTML_level_3_inactive(self, accuracy):
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
    fandom_html_panel = HtmlPanel(html=custom_html)
    self.fandom_submodel.add_component(fandom_html_panel)
            
  def custom_HTML_level_4_active(self, accuracy):
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
    musical_html_panel = HtmlPanel(html=custom_html)
    self.musical_submodel.add_component(musical_html_panel)
    
  def custom_HTML_level_4_inactive(self, accuracy):
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
    musical_html_panel = HtmlPanel(html=custom_html)
    self.musical_submodel.add_component(musical_html_panel)
            
  def edit_icon_click(self, **event_args):
    if self.model_name.visible is True: 
      self.model_name.visible = False
      self.model_description.visible = False
      self.model_name_text.visible = True
      self.model_description_text.visible = True
      self.model_name_text.text = self.model_name.text
      self.model_description_text.text = self.model_description.text
      self.edit_icon.icon = 'fa:save'
    else:
      self.model_name_text.visible = False
      self.model_description_text.visible = False
      self.model_name.visible = True
      self.model_description.visible = True
      self.model_name.text = self.model_name_text.text
      self.model_description.text = self.model_description_text.text
      self.edit_icon.icon = 'fa:pencil'
      res = anvil.server.call('update_model_stats', self.model_id_view, self.model_name_text.text, self.model_description_text.text, False)
      if res == 'success':
        get_open_form().refresh_models_components()
        Notification("",
          title="Model updated!",
          style="success").show()
  
  
  # def nav_add_references_click(self, **event_args):
  #   self.nav_references.role = 'section_buttons_focused'
  #   self.nav_prev_rated.role = 'section_buttons'
  #   self.nav_filters.role = 'section_buttons'
  #   self.sec_references.visible = True
  #   self.sec_references_master = True
  #   self.sec_models.visible = False
  #   self.sec_prev_rated.visible = False
  #   self.sec_filters.visible = False
  #   self.sec_references.clear()
  #   self.sec_references.add_component(C_AddRefArtists(self.model_id_view))
  
  def nav_references_click(self, **event_args):
    self.nav_references.role = 'section_buttons_focused'
    self.nav_model.role = 'section_buttons'
    self.nav_prev_rated.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons'
    self.nav_level_of_pop.role = 'section_buttons'
    self.nav_submodel_cont.role = 'section_buttons'
    self.sec_references.visible = True
    self.sec_references_master.visible = True
    self.sec_models.visible = False
    self.sec_prev_rated.visible = False
    self.sec_filters.visible = False
    self.sec_level_of_pop_master.visible = False
    self.sec_submodel_contributions_master.visible = False
    self.sec_references.clear()
    # self.sec_references.add_component(C_EditRefArtists(self.model_id_view))
    self.sec_references.add_component(C_RefArtistsSettings())
    
  def nav_prev_rated_click(self, **event_args):    
    self.nav_references.role = 'section_buttons'
    self.nav_model.role = 'section_buttons'
    self.nav_prev_rated.role = 'section_buttons_focused'
    self.nav_filters.role = 'section_buttons'
    self.nav_level_of_pop.role = 'section_buttons'
    self.nav_submodel_cont.role = 'section_buttons'
    self.sec_references.visible = False
    self.sec_references_master.visible = False
    self.sec_models.visible = False
    self.sec_prev_rated.visible = True
    self.sec_filters.visible = False
    self.sec_level_of_pop_master.visible = False
    self.sec_submodel_contributions_master.visible = False
    self.sec_prev_rated.clear()
    self.sec_prev_rated.add_component(C_Rating(self.model_id_view))

  def nav_level_of_pop_click(self, **event_args):
    self.nav_references.role = 'section_buttons'
    self.nav_model.role = 'section_buttons'
    self.nav_prev_rated.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons'
    self.nav_level_of_pop.role = 'section_buttons_focused'
    self.nav_submodel_cont.role = 'section_buttons'
    self.sec_references.visible = False
    self.sec_references_master.visible = False
    self.sec_models.visible = False
    self.sec_prev_rated.visible = False
    self.sec_filters.visible = False
    self.sec_submodel_contributions_master.visible = False    
    self.sec_level_of_pop_master.visible = True
    self.sec_level_of_pop.clear()
    self.sec_level_of_pop.add_component(C_LevelOfPopularity())

  def nav_submodel_cont_click(self, **event_args):
    self.nav_references.role = 'section_buttons'
    self.nav_model.role = 'section_buttons'
    self.nav_prev_rated.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons'
    self.nav_level_of_pop.role = 'section_buttons'
    self.nav_submodel_cont.role = 'section_buttons_focused'
    self.sec_references.visible = False
    self.sec_references_master.visible = False
    self.sec_models.visible = False
    self.sec_prev_rated.visible = False
    self.sec_filters.visible = False
    self.sec_level_of_pop_master.visible = False
    self.sec_submodel_contributions_master.visible = True    
    self.sec_submodel_contributions.clear()
    self.sec_submodel_contributions.add_component(C_SubModelContribution())
  
  def nav_filters_click(self, **event_args):
    self.nav_references.role = 'section_buttons'
    self.nav_model.role = 'section_buttons'
    self.nav_prev_rated.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons_focused'
    self.nav_level_of_pop.role = 'section_buttons'
    self.nav_submodel_cont.role = 'section_buttons'
    self.sec_references.visible = False
    self.sec_references_master.visible = False
    self.sec_models.visible = False
    self.sec_prev_rated.visible = False
    self.sec_filters.visible = True
    self.sec_level_of_pop_master.visible = False
    self.sec_submodel_contributions_master.visible = False
    self.sec_filters.clear()
    self.sec_filters.add_component(C_Filter(self.model_id_view))

  def save_click(self, **event_args):
    anvil.server.call('update_model_popularity_range',
                      int(self.model_id_view),
                      load_var('min_pop'),
                      load_var('max_pop'))
    Notification("",
        title=f"Popularity range is updated from {load_var('min_pop')} to {load_var('max_pop')}!",
        style="success").show()

  def save_click_submodel(self, **event_args):
    anvil.server.call('update_sub_model_contribution',
                      int(self.model_id_view),
                      int(load_var('artist_career_fit')) / 100,
                      0.4,
                      int(load_var('growth_imp_fit')) / 100,
                      int(load_var('musical_fit')) / 100
                     )
    Notification("",
      title= f"""Submodel contributions updated to:        
      - {load_var('artist_career_fit')}% Similarity,
      - {load_var('musical_fit')}% Musical, and
      - {load_var('growth_imp_fit')}% Growth!""",      
      style="success").show()
    # alert(title="Submodel contributions have been saved",
    #     content=f"""
    #     Artist Career Fit Importance: {load_var('artist_career_fit')}%,
    #     Musical Fit: {load_var('musical_fit')}%,
    #     Growth Importance: {load_var('growth_imp_fit')}%!""",
    #     # large=True,
    #     buttons=[("OK", "OK")],
    #     role="alert-notification"
    #   )
  
  def delete_click(self, **event_args):
    result = alert(title='Do you want to delete this model?',
          content="Are you sure to delete this model?\n\nEverything will be lost! All reference artists, all previously rated artists - all you did will be gone for ever.",
          buttons=[
            ("Cancel", "Cancel"),
            ("Delete", "Delete")
          ])
    if result == 'Delete':
      res = anvil.server.call('delete_model', self.model_id_view)
      if res == 'success':
        Notification("",
          title="Model deleted!",
          style="success").show()
        click_button('home', event_args)
        get_open_form().refresh_models_components()
        get_open_form().refresh_models_underline()
  
  def activate_click(self, **event_args):
    anvil.server.call('update_model_usage', user["user_id"], self.model_id_view)
    save_var('model_id', self.model_id_view)
    click_button(f'model_profile?model_id={self.model_id_view}&section=Main', event_args)
    get_open_form().refresh_models_underline()
    
  def discover_click(self, **event_args):
    anvil.server.call('update_model_usage', user["user_id"], self.model_id_view)
    save_var('model_id', self.model_id_view)
    get_open_form().refresh_models_underline()
    temp_artist_id = anvil.server.call('get_next_artist_id', self.model_id_view)
    click_button(f'artists?artist_id={temp_artist_id}', event_args)
    
  def retrain_click(self, **event_args):
    res = anvil.server.call('retrain_model', self.model_id_view)
    if res == 'success':
      self.retrain.visible = False
      self.retrain_wait.visible = True
      self.retrain_model_date_value.text = time.strftime("%Y-%m-%d")
      alert(title='Re-training of your model is running',
            content="We started to re-train your model. This will take roughly 10 minutes to be effective.\n\nDue to high computational effort, re-training the model is only available once per day.",
            buttons=[("Ok", "Ok")]
      )

  def nav_model_click(self, **event_args):
    self.nav_references.role = 'section_buttons'
    self.nav_model.role = 'section_buttons_focused'
    self.nav_prev_rated.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons'
    self.nav_level_of_pop.role = 'section_buttons'
    self.nav_submodel_cont.role = 'section_buttons'
    self.sec_references.visible = False
    self.sec_references_master.visible = False
    self.sec_models.visible = True
    self.sec_prev_rated.visible = False
    self.sec_filters.visible = False
    self.sec_submodel_contributions_master.visible = False
    self.sec_level_of_pop_master.visible = False

    # Model 1
    if self.similarity_submodel.get_components() == []:
      if self.infos["model_1_acc"] is not None:
        self.custom_HTML_level_1_active(round(self.infos["model_1_acc"]))
        self.model_1_accuracy_summary.text = "{}{}".format(round(self.infos["model_1_acc"]), "%")
        self.similarity_active.visible = True
        self.similarity_in_training.visible = False
        self.similarity_cont.text = "{}{}".format(round(self.infos["model_1_cont"]*100), "%")
      else:
        self.custom_HTML_level_1_inactive(min(round(self.infos["total_ratings"]/int(10)*100), 100))
        self.model_1_accuracy_summary.text = "{}{}".format(min(round(self.infos["total_ratings"]/int(10)*100), 100), "%")
        self.similarity_active.visible = False
        self.similarity_in_training.visible = True
        self.similarity_cont.text = "0%"
         
    # Model 2
    if self.success_submodel.get_components() == []:
      if self.infos["model_2_acc"] is not None:
        self.custom_HTML_level_2_active(round(self.infos["model_2_acc"]))
        self.model_2_accuracy_summary.text = "{}{}".format(round(self.infos["model_2_acc"]), "%")
        self.success_active.visible = True
        self.success_in_training.visible = False
        self.success_cont.text = "{}{}".format(round(self.infos["model_2_cont"]*100), "%")
      else:
        self.custom_HTML_level_2_inactive(min(round(self.infos["total_ratings"]/int(50)*100), 100))
        self.model_2_accuracy_summary.text = "{}{}".format(min(round(self.infos["total_ratings"]/int(50)*100), 100), "%")
        self.success_active.visible = False
        self.success_in_training.visible = True
        self.success_cont.text = "0%"
        
    # Model 3
    if self.fandom_submodel.get_components() == []:
      if self.infos["model_3_acc"] is not None:
        self.custom_HTML_level_3_active(round(self.infos["model_3_acc"]))
        self.model_3_accuracy_summary.text = "{}{}".format(round(self.infos["model_3_acc"]), "%")
        self.fandom_active.visible = True
        self.fandom_in_training.visible = False
        self.fandom_cont.text = "{}{}".format(round(self.infos["model_3_cont"]*100), "%")
      else:
        self.custom_HTML_level_3_inactive(min(round(self.infos["total_ratings"]/int(75)*100), 100))
        self.model_3_accuracy_summary.text = "{}{}".format(min(round(self.infos["total_ratings"]/int(75)*100), 100), "%")
        self.fandom_active.visible = False
        self.fandom_in_training.visible = True
        self.fandom_cont.text = "0%"
        
    # Model 4
    if self.musical_submodel.get_components() == []:
      if self.infos["model_1_acc"] is not None:
        self.custom_HTML_level_4_active(round(0.95*self.infos["model_1_acc"]))
        self.model_4_accuracy_summary.text = "{}{}".format(round(0.95*self.infos["model_1_acc"]), "%")
        self.musical_active.visible = True
        self.musical_in_training.visible = False
        self.musical_cont.text = "{}{}".format(round(self.infos["model_4_cont"]*100), "%")
      else:
        self.custom_HTML_level_4_inactive(min(round(self.infos["total_ratings"]/int(100)*100), 100))
        self.model_4_accuracy_summary.text = "{}{}".format(min(round(self.infos["total_ratings"]/int(100)*100), 100), "%")
        self.musical_active.visible = False
        self.musical_in_training.visible = True
        self.musical_cont.text = "0%"

  def create_ratings_histogram_chart(self, ratings_data=None):
    if ratings_data is None:
      ratings_data = self.infos["ratings"]

    rating_values = [item['interest'] for item in self.infos["ratings"]]
    rating_counts = [item['cnt'] for item in self.infos["ratings"]]

    max_y_value = max(rating_counts) * 1.1
    dynamic_tick = max(1, math.ceil(max_y_value / 5))  # Mindestens 1, sonst aufrunden

    # Format the text for the bar annotations
    formatted_text = [f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.1f}K' if x >= 1e3 else str(x) for x in rating_counts]
    
    # Creating the Bar Chart
    fig = go.Figure(data=(
      go.Bar(
        x = rating_values,
        y = rating_counts,
        width=0.5,
        text = formatted_text,
        textposition='none',
        hoverinfo='none',
        hovertext= rating_values,
        hovertemplate= 'Rating: %{hovertext}<br>Count: %{text} <extra></extra>',
      )
    ))

    fig.update_layout(
      title={
        'text': "Distribution of Ratings",
        'y':0.95,  # Adjust the vertical position of the title
        'x':0.5,  # Center the title horizontally
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {
          'size': 14,
          'color': 'white'
        }
      },
      template='plotly_dark',
      plot_bgcolor='rgba(0,0,0,0)',
      paper_bgcolor='rgba(0,0,0,0)',
      xaxis=dict(
        tickvals=rating_values,
        title='Rating',
        titlefont=dict(
          size=12  # Set the font size for the x-axis title
        ),
        tickfont=dict(
          size=10  # Set the font size for the x-axis tick labels
        ),
      ),
      yaxis=dict(
        gridcolor='rgb(175,175,175)',  # Color of the gridlines
        gridwidth=1,  # Thickness of the gridlines
        griddash='dash',  # Dash style of the gridlines
        range=[0, max_y_value],
        tickformat='~s',  # Format numbers with SI unit prefixes
        title='Count',
        titlefont=dict(
          size=12  # Set the font size for the x-axis title
        ),
        tickfont=dict(
          size=10  # Set the font size for the x-axis tick labels
        ),
        zerolinecolor='rgb(240,240,240)',  # Set the color of the zero line
        dtick=dynamic_tick,
      ),
      hoverlabel=dict(
        bgcolor='rgba(237,139,82, 0.4)'
      ),
      autosize=True,  # Automatically adjust the chart size to fit the container
      height=200,  # Adjust the height as needed to fit the container
      margin=dict(
          l=10,  # Left margin
          r=10,  # Right margin
          t=35,  # Top margin
          b=10   # Bottom margin
      )
    )
    # This is to style the bars
    for trace in fig.data:
      trace.update(
        # marker_color='rgb(240,229,252)',
        marker_color='rgba(237,139,82, 1)',
        marker_line_color='rgb(237,139,82)',
        marker_line_width=0.1,
        opacity=0.9
      )
    self.Ratings_histogram.figure = fig
