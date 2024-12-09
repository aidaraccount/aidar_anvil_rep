from ._anvil_designer import Notifications_mailTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import datetime
import re

from anvil_extras import routing
from ...nav import click_link, click_button, logout, login_check, load_var


class Notifications_mail(Notifications_mailTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    # -------------
    # load initial data
    # 0) Header
    # Name & its Icon
    self.name_link.text = self.item["name"]
    if self.item["type"] == 'mail':
      self.name_link.icon = 'fa:envelope-o'
    elif self.item["type"] == 'playlist':
      self.name_link.icon = 'fa:spotify'
    
    # activate/ deactivate Button
    if self.item["active"] is True:
      self.activate.visible = False
      self.deactivate.visible = True
    else:
      self.activate.visible = True
      self.deactivate.visible = False
    
    # A1) Frequency
    if self.item["type"] == 'mail':
      self.frequency_master_1.visible = True
      self.frequency_field_title.visible = True
      
      self.frequency_option_1.text = self.item["freq_1"]
      self.frequency_option_2.text = self.item["freq_2"]
      self.frequency_picker.date = self.item["freq_3"]
      # self.weekdays.text = self.item["freq_3"]    
  
      if self.frequency_option_1.text == 'Daily':
        self.flow_panel_freq_2.visible = False
        self.flow_panel_freq_3.visible = False
      elif self.frequency_option_1.text == 'Every X Days':
        self.flow_panel_freq_2.visible = True
        self.flow_panel_freq_3.visible = True
      elif self.frequency_option_1.text == 'Monthly':
        self.flow_panel_freq_2.visible = False
        self.flow_panel_freq_3.visible = True

    # A2) Status
    if self.item["type"] == 'playlist':
      self.status_field_title.visible = True
      

      print(self.item["sp_playlist_id"])
      if self.item["sp_playlist_id"] is None or self.item["sp_playlist_id"] == '':
        self.playlist_in_creation.visible = True
      else:
        self.url_master.visible = True
        self.last_updated_spotify.visible = True
        self.playlist_url.url = f"https://open.spotify.com/playlist/{self.item['sp_playlist_id']}"
        self.larst_updated_value.text = self.item["last_update"][:-3]
    
    # B) General
    self.no_artists_box.text = self.item["no_artists"]
    self.notif_rep_value.text = self.item["repetition_1"]
    self.artist_rep_x_days_freq.text = self.item["repetition_2"]
    if self.item["repetition_1"] == 'Repeat after X days':
      self.column_panel_rep.visible = True
    else:
      self.column_panel_rep.visible = False    

    # for playlists
    if self.item["type"] == 'playlist':
      self.song_selection.visible = True
      self.no_latest_releases.visible = True
      
      self.song_selection_type.text = self.item["song_selection_1"]
      self.no_latest_rel_box_spotify.text = self.item["song_selection_2"]
    
    # C) Metric
    self.metrics_option_1.text = self.item["metric"]
    self.days_since_rel_field_value.text = self.item["release_days"]
        
    if self.item['min_grow_fit'] is None:
      self.min_growth_value.text = 0
    else:
      self.min_growth_value.text = int("{:.0f}".format(float(self.item["min_grow_fit"])*100))      
    
    if self.metrics_option_1.text == 'Growing Fits':
      self.min_growth_fit.visible = True
    elif self.metrics_option_1.text == 'Releasing Fits':
      self.max_days_since_rel.visible = True
      
    # D) Selection Parameters
    # artist selection
    if self.item["rated"] is True:
      self.artist_selection_option.text = 'Rated'
    elif self.item["rated"] is False:
      self.artist_selection_option.text = 'Unrated'
    elif self.item["rated"] is None:
      self.artist_selection_option.text = 'All'

    # watchlist selection
    if self.item["watchlist"] is True:
      self.watchlist_selection_option.text = 'On watchlist'
    elif self.item["watchlist"] is False:
      self.watchlist_selection_option.text = 'Not on watchlist'
    elif self.item["watchlist"] is None:
      self.watchlist_selection_option.text = 'All'

    # model selection
    models = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))
    active_models = self.item["model_ids"]

    for i in range(0, len(models)):
      if models[i]["model_id"] in active_models:        
        model_link = Link(
          text=models[i]["model_name"],
          tag=models[i]["model_id"],
          role='genre-box'
          )
      else:
        model_link = Link(
          text=models[i]["model_name"],
          tag=models[i]["model_id"],
          role='genre-box-deselect'
          )
      
      if models[i]["fully_trained"] is False:        
        model_link = Link(
          text=models[i]["model_name"],
          tag=models[i]["model_id"],
          role='genre-box-deactive',
          )
      
      model_link.set_event_handler('click', self.create_activate_model_handler(models[i]["model_id"]))
      self.flow_panel_models.add_component(model_link)

  
  # NOTIFICATION MODIFICATION
  def update_notification(self, **event_args):
    # prepare data
    # frequency 2 and 3
    if self.frequency_option_1.text == 'Daily':
      freq_2 = None
      freq_3 = None
    elif self.frequency_option_1.text == 'Every X Days':
      freq_2 = self.frequency_option_2.text
      freq_3 = self.frequency_picker.date
    elif self.frequency_option_1.text == 'Monthly':
      freq_2 = None
      freq_3 = self.frequency_picker.date

    # artist selection = self.item["rated"] True(Rated) False None(All)
    options = {'Rated': True, 'Unrated': False, 'All': None}
    artist_selection_option = options.get(self.artist_selection_option.text)

    # watchilist selection = self.item["watchlist"] True(On watchlist) False None(All)
    options = {'On watchlist': True, 'Not on watchlist': False, 'All': None}
    watchlist_selection_option = options.get(self.watchlist_selection_option.text)
      
    if self.min_growth_value.text == '':
      min_growth_value = None
    elif self.min_growth_value.text.isalpha():
      min_growth_value = None
    else:
      min_growth_value = float(self.min_growth_value.text)/100

    if self.days_since_rel_field_value.text == '':
      release_days = None
    else:
      release_days = self.days_since_rel_field_value.text

    # Collect selected model IDs
    model_ids = []
    for component in self.flow_panel_models.get_components():
        if isinstance(component, Link) and component.role == 'genre-box':  # Only active models
            model_ids.append(component.tag)

    # do the update
    anvil.server.call('update_notification',
                      notification_id = self.item["notification_id"],
                      type = self.item["type"],
                      name = self.name_link.text,
                      active = self.deactivate.visible,
                      freq_1 = self.frequency_option_1.text,
                      freq_2 = freq_2,
                      freq_3 = freq_3,
                      metric = self.metrics_option_1.text,
                      no_artists = self.no_artists_box.text,
                      repetition_1 = self.notif_rep_value.text,
                      repetition_2 = self.artist_rep_x_days_freq.text,
                      rated = artist_selection_option,
                      watchlist = watchlist_selection_option,
                      release_days = release_days,
                      min_grow_fit = min_growth_value,
                      model_ids = model_ids,
                      song_selection_1 = self.song_selection_type.text,
                      song_selection_2 = self.no_latest_rel_box_spotify.text)

  def activate_notification(self, **event_args):
    if self.activate.visible is True:
      self.activate.visible = False
      self.deactivate.visible = True
      Notification("",
        title=f'"{self.name_link.text}" is activated',
        style="success").show()
    else:
      self.activate.visible = True
      self.deactivate.visible = False
      Notification("",
        title=f'"{self.name_link.text}" is no longer active',
        style="success").show()      
    self.update_notification()

  def delete_notification_click(self, **event_args):
    anvil.server.call('delete_notification',
                      notification_id = self.item["notification_id"])
    self.parent.parent.parent.parent.get_notifications()

  
  # BUTTON FUNCTIONALITIES
  def edit_icon_click_2(self, **event_args):
    self.name_link.visible = False
    self.model_name_text.visible = True
    self.model_name_text.text = self.name_link.text
    self.model_name_text.focus()
      
  def artist_selection_option_click(self, **event_args):
    if self.artist_selection_option.text == 'Rated':
      self.artist_selection_option.text = 'Unrated'
    elif self.artist_selection_option.text == 'Unrated':
      self.artist_selection_option.text = 'All'
    elif self.artist_selection_option.text == 'All':
      self.artist_selection_option.text = 'Rated'      
    self.update_notification()

  def watchlist_selection_option_click(self, **event_args):
    if self.watchlist_selection_option.text == 'On watchlist':
      self.watchlist_selection_option.text = 'Not on watchlist'
    elif self.watchlist_selection_option.text == 'Not on watchlist':
      self.watchlist_selection_option.text = 'All'
    elif self.watchlist_selection_option.text == 'All':
      self.watchlist_selection_option.text = 'On watchlist'      
    self.update_notification()

  def frequency_option_1_click(self, **event_args):
    if self.frequency_option_1.text == 'Daily':
      self.frequency_option_1.text = 'Every X Days'
      self.flow_panel_freq_2.visible = True
      self.weekdays.visible = False
      self.frequency_days_label_days.visible = True
      self.frequency_days_label_days.text = 'Days'
      self.flow_panel_freq_3.visible = True
    elif self.frequency_option_1.text == 'Every X Days':
      self.frequency_option_1.text = 'Monthly'
      self.flow_panel_freq_2.visible = False
      self.flow_panel_freq_3.visible = True
      self.frequency_days_label_days.visible = False
    elif self.frequency_option_1.text == 'Monthly':
      self.frequency_option_1.text = 'Daily'
      self.flow_panel_freq_2.visible = False
      self.weekdays.visible = False
      self.flow_panel_freq_3.visible = False      
    self.update_notification()

  def notification_repetition_value_click(self, **event_args):
    if self.notif_rep_value.text == 'Suggest artists once':
      self.notif_rep_value.text = 'Repeat suggestions'
    elif self.notif_rep_value.text == 'Repeat suggestions':
      self.notif_rep_value.text = 'Repeat after X days'
      self.column_panel_rep.visible = True
    elif self.notif_rep_value.text == 'Repeat after X days':
      self.notif_rep_value.text = 'Suggest artists once'
      self.column_panel_rep.visible = False      
    self.update_notification()

  def metrics_option_1_click(self, **event_args):
    if self.metrics_option_1.text == 'Top Fits':
      self.metrics_option_1.text = 'Growing Fits'
      self.min_growth_fit.visible = True
    elif self.metrics_option_1.text == 'Growing Fits':
      self.metrics_option_1.text = 'Releasing Fits'
      self.min_growth_fit.visible = False
      self.max_days_since_rel.visible = True
    elif self.metrics_option_1.text == 'Releasing Fits':
      self.metrics_option_1.text = 'Top Fits'
      self.max_days_since_rel.visible = False
    self.update_notification()
    
  
  # LOST FOCUS CHECKS
  def edit_icon_click_2_lose_focus(self, **event_args):
    self.model_name_text.visible = False
    self.name_link.visible = True
    self.name_link.text = self.model_name_text.text      
    self.update_notification()
      
  def frequency_option_2_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.frequency_option_1.text == "Every X Days":
      if not self.frequency_option_2.text.strip() or not self.frequency_option_2.text.isdigit() or int(self.frequency_option_2.text) < 1:
        self.every_x_days_warning.visible = True
      else:
        self.every_x_days_warning.visible = False    
        self.update_notification()
        
  def date_picker_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.frequency_option_1.text in ["Every X Days", "Monthly"]:
      print(self.frequency_picker.date)
      if self.frequency_picker.date is None:
        self.every_x_days_start_warning.visible = True
      else:
        self.every_x_days_start_warning.visible = False    
        self.update_notification()
        
  def artist_rep_x_days_freq_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.notif_rep_value.text == "Repeat after X days":
      if not self.artist_rep_x_days_freq.text.strip() or not self.artist_rep_x_days_freq.text.isdigit() or int(self.artist_rep_x_days_freq.text) < 1:
        self.artist_rep_x_days_freq_warning.visible = True
      else:
        self.artist_rep_x_days_freq_warning.visible = False    
        self.update_notification()
        
  def min_growth_value_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.metrics_option_1.text == "Growing Fits":
      if not self.min_growth_value.text.strip() or not self.min_growth_value.text.isdigit() or int(self.min_growth_value.text) < 0 or int(self.min_growth_value.text) > 100:
        self.min_growth_warning.visible = True
      else:
        self.min_growth_warning.visible = False    
        self.update_notification()
        
  def max_days_since_rel_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.metrics_option_1.text == "Releasing Fits":
      if not self.days_since_rel_field_value.text.strip() or not self.days_since_rel_field_value.text.isdigit():
        self.days_since_rel_field_warning.visible = True
      else:
        self.days_since_rel_field_warning.visible = False    
        self.update_notification()

  def no_latest_rel_box_spotify_lost_focus(self, **event_args):
    # Validate number latest releases only if "Latest Releases" is selected
    if self.song_selection_type.text == "Latest Releases":
      if not self.no_latest_rel_box_spotify.text.strip() or not self.no_latest_rel_box_spotify.text.isdigit() or int(self.no_latest_rel_box_spotify.text) < 0 or int(self.no_latest_rel_box_spotify.text) > 10:
        self.no_latest_rel_box_spotify_warning.visible = True
      else:
        self.no_latest_rel_box_spotify_warning.visible = False    
        self.update_notification()

  def no_artists_box_lost_focus(self, **event_args):
    # Validate the no_artists_box input (ensure it's between 1 and 20)
    if not self.no_artists_box.text.strip() or not self.no_artists_box.text.isdigit() or int(self.no_artists_box.text) < 0 or int(self.no_artists_box.text) > 20:
      self.max_number_artist_warning.visible = True
    else:
      self.max_number_artist_warning.visible = False    
      self.update_notification()

  
  # BASE FUNCTIONS
  # MODEL BUTTONS
  def create_activate_model_handler(self, model_id):
    def handler(**event_args):
      self.activate_model(model_id)
    return handler

  # change active status of MODEL BUTTONS
  def activate_model(self, model_id):
    for component in self.flow_panel_models.get_components():
      if isinstance(component, Link):        
        # change activation
        if int(component.tag) == model_id:
          if component.role == 'genre-box-deactive':
            Notification("",
              title="Model not fully trained yet - you need at least 50 ratings!",
              style="info").show()
          else:
            if component.role == 'genre-box':
              component.role = 'genre-box-deselect'
            else:
              component.role = 'genre-box'
    
    # Check if any models are selected    
    # a) ccollect selected model IDs
    model_ids = []
    for component in self.flow_panel_models.get_components():
        if isinstance(component, Link) and component.role == 'genre-box':  # Only active models
            model_ids.append(component.tag)

    # b) show warning or update_notification
    if not model_ids:
      self.models_warning.visible = True
    else:
      self.models_warning.visible = False
      self.update_notification()
