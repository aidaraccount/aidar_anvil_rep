from ._anvil_designer import ModelProfile_newTemplate
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

from ..Home import Home
from ..C_EditRefArtists import C_EditRefArtists
from ..C_AddRefArtists import C_AddRefArtists
from ..C_Rating import C_Rating
from ..C_Filter import C_Filter

from anvil_extras import routing
from ..nav import click_link, click_button, load_var, save_var

from anvil import js
import anvil.js
import anvil.js.window


@routing.route('model_profile_new', url_keys=['model_id', 'section'], title='Model Profile New')
class ModelProfile_new(ModelProfile_newTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.html = '@theme:Modelpage_html_JS.html'
      
    model_id_active = load_var("model_id")
    print(f"ModelProfile model_id_active: {model_id_active}")
    model_id_view = self.url_dict['model_id']
    self.model_id_view = model_id_view
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
    self.retrain_date = infos["train_model_date"]
    print(infos)

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

    # Progress Circle
    if infos["overall_status"] == 'Running':
      self.custom_HTML_prediction(infos["overall_acc"])
    else:
      self.linear_panel_2.visible = True
      self.column_panel_5.visible = False
    
    # ---------------
    # SECCTIONS
    # # retrain button
    # if infos["total_ratings"] < 75:
    #   self.retrain.visible = False
    #   self.retrain_wait.visible = True
    #   self.retrain_wait.text = 'At least 75 ratings required for training the model'
    # elif self.retrain_date != time.strftime("%Y-%m-%d"):
    #   self.retrain.visible = True
    #   self.retrain_wait.visible = False
    # else:
    #   self.retrain.visible = False
    #   self.retrain_wait.visible = True
      
    # secction routing
    if section == 'Main':
      self.nav_model_click()
    elif section == 'PrevRated':
      self.nav_prev_rated_click()
    elif section == 'Filter':
      self.nav_filters_click()
    elif section == 'AddRefArtists':
      self.nav_add_references_click()   
    
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
      res = anvil.server.call('update_model_stats', self.model_id_view, self.model_name_text.text, self.model_description_text.text)
      if res == 'success':
        Notification("",
          title="Model updated!",
          style="success").show()

  def nav_references_click(self, **event_args):
    self.nav_references.role = 'section_buttons_focused'
    self.nav_model.role = 'section_buttons'
    self.nav_prev_rated.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons'
    self.sec_references.visible = True
    self.sec_models.visible = False
    self.sec_prev_rated.visible = False
    self.sec_filters.visible = False
    self.sec_references.clear()
    self.sec_references.add_component(C_EditRefArtists(self.model_id_view))

  def nav_add_references_click(self, **event_args):
    self.nav_references.role = 'section_buttons_focused'
    self.nav_prev_rated.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons'
    self.sec_references.visible = True
    self.sec_models.visible = False
    self.sec_prev_rated.visible = False
    self.sec_filters.visible = False
    self.sec_references.clear()
    self.sec_references.add_component(C_AddRefArtists(self.model_id_view))
  
  def nav_prev_rated_click(self, **event_args):    
    self.nav_references.role = 'section_buttons'
    self.nav_prev_rated.role = 'section_buttons_focused'
    self.nav_model.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons'
    self.sec_references.visible = False
    self.sec_models.visible = False
    self.sec_prev_rated.visible = True
    self.sec_filters.visible = False
    self.sec_prev_rated.clear()
    self.sec_prev_rated.add_component(C_Rating(self.model_id_view))
    
  def nav_filters_click(self, **event_args):
    self.nav_references.role = 'section_buttons'
    self.nav_prev_rated.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons_focused'
    self.nav_model.role = 'section_buttons'
    self.sec_references.visible = False
    self.sec_prev_rated.visible = False
    self.sec_models.visible = False
    self.sec_filters.visible = True
    self.sec_filters.clear()
    self.sec_filters.add_component(C_Filter(self.model_id_view))

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
    click_button(f'model_profile_new?model_id={self.model_id_view}&section=Main', event_args)
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
    self.nav_model.role = 'section_buttons_focused'
    self.nav_references.role = 'section_buttons'
    self.nav_prev_rated.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons'
    self.sec_references.visible = False
    self.sec_models.visible = True
    self.sec_prev_rated.visible = False
    self.sec_filters.visible = False

    # Model 1
    if self.similarity_submodel.get_components() == []:
      if self.infos["model_1_acc"] is not None:
        self.custom_HTML_level_1_active(self.infos["model_1_acc"])
      else:
        self.custom_HTML_level_1_inactive(min(self.infos["total_ratings"]/float(10)*100, 100))
      
    # Model 2
    if self.success_submodel.get_components() == []:
      if self.infos["model_2_acc"] is not None:
        self.custom_HTML_level_2_active(self.infos["model_2_acc"])
      else:
        self.custom_HTML_level_2_inactive(min(self.infos["total_ratings"]/float(50)*100, 100))
        
    # Model 3
    if self.fandom_submodel.get_components() == []:
      if self.infos["model_3_acc"] is not None:
        self.custom_HTML_level_3_active(self.infos["model_3_acc"])
      else:
        self.custom_HTML_level_3_inactive(min(self.infos["total_ratings"]/float(75)*100, 100))
        
    # Model 4
    if self.musical_submodel.get_components() == []:
      if self.infos["model_4_acc"] is not None:
        self.custom_HTML_level_4_active(self.infos["model_4_acc"])
      else:
        self.custom_HTML_level_4_inactive(min(self.infos["total_ratings"]/float(100)*100, 100))

    
