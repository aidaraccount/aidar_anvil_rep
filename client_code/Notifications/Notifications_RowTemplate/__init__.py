from ._anvil_designer import Notifications_RowTemplateTemplate
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


class Notifications_RowTemplate(Notifications_RowTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # general content
    self.name_link.text = self.item["name"]
    self.no_artists_box.text = self.item["no_artists"]
    self.min_growth_value.text = self.item["min_grow_fit"]
    self.metrics_option_1.text = self.item["metric"]
    self.frequency_option_1.text = self.item["freq_1"]
    self.frequency_option_2.text = self.item["freq_2"]
    self.frequency_option_3.text = self.item["freq_3"]
    self.days_since_rel_field_value.text = self.item["release_days"]
    self.notif_rep_value.text = self.item["repetition"]
    # activate Notification
    if self.item["active"] is True:
      self.activate.visible = False
      self.deactivate.visible = True
    else:
      self.activate.visible = True
      self.deactivate.visible = False
    # type specific content
    if self.item["type"] == 'mail':
      self.name_link.icon = 'fa:envelope-o'
    elif self.item["type"] == 'playlist':
      self.name_link.icon = 'fa:spotify'

    if self.frequency_option_1.text == 'Every X Days':
      self.frequency_option_2.visible = True
      self.frequency_option_4.visible = True
    elif self.frequency_option_1.text == 'Monthly':
      self.frequency_days_label.visible = True
      self.frequency_picker.visible = True

    
    # for i in range(0, len(models)):
    #   if models[i]["is_last_used"] is True:        
    #     model_link = Link(
    #       text=models[i]["model_name"],
    #       tag=models[i]["model_id"],
    #       role='genre-box'
    #       )
    #     if models[i]["fully_trained"] is False:
    #       is_last_used_is_not_trained = True
    #   else:
    #     model_link = Link(
    #       text=models[i]["model_name"],
    #       tag=models[i]["model_id"],
    #       role='genre-box-deselect'
    #       )
      
    #   if models[i]["fully_trained"] is False:        
    #     model_link = Link(
    #       text=models[i]["model_name"],
    #       tag=models[i]["model_id"],
    #       role='genre-box-deactive'
    #       )
    #   else:        
    #     working_model = True
        
    #   model_link.set_event_handler('click', self.create_activate_model_handler(models[i]["model_id"]))
    #   self.flow_panel_models.add_component(model_link)

  def activate_notification(self, **event_args):
    if self.activate.visible is True:
      self.activate.visible = False
      self.deactivate.visible = True
    else:
      self.activate.visible = True
      self.deactivate.visible = False
    self.update_notification_1()
    
  # RATED BUTTON
  def artist_selection_option_click(self, **event_args):
    if self.artist_selection_option.text == 'Rated':
      self.artist_selection_option.text = 'Unrated'
      self.artist_selection_option.role = 'genre-box'
    elif self.artist_selection_option.text == 'Unrated':
      self.artist_selection_option.text = 'All'
      self.artist_selection_option.role = 'genre-box-deselect'
    elif self.artist_selection_option.text == 'All':
      self.artist_selection_option.text = 'Rated'
      self.artist_selection_option.role = 'genre-box'

  # WATCHLIST BUTTON
  def watchlist_selection_option_click(self, **event_args):
    if self.watchlist_selection_option.text == 'On watchlist':
      self.watchlist_selection_option.text = 'Not on watchlist'
      self.watchlist_selection_option.role = 'genre-box'
    elif self.watchlist_selection_option.text == 'Not on watchlist':
      self.watchlist_selection_option.text = 'All'
      self.watchlist_selection_option.role = 'genre-box-deselect'
    elif self.watchlist_selection_option.text == 'All':
      self.watchlist_selection_option.text = 'On watchlist'
      self.watchlist_selection_option.role = 'genre-box'      
  
  def delete_notification_click(self, **event_args):
    anvil.server.call('delete_notification',
                      notification_id = self.item["notification_id"])

    self.parent.parent.parent.parent.get_notifications()
  
  def frequency_option_1_click(self, **event_args):
    if self.frequency_option_1.text == 'Daily':
      self.frequency_option_1.text = 'Every X Days'
      self.frequency_option_1.role = 'genre-box'
      self.frequency_days_label.visible = False
      self.frequency_option_2.visible = True
      self.frequency_option_3.visible = False
      self.frequency_option_4.visible = True
      self.frequency_option_4.text = 'Days'
    elif self.frequency_option_1.text == 'Every X Days':
      self.frequency_option_1.text = 'Monthly'
      self.frequency_option_1.role = 'genre-box'
      self.frequency_days_label.visible = True
      self.frequency_days_label.text = 'Starting:'
      self.frequency_option_2.visible = False
      self.frequency_picker.visible = True
      self.frequency_option_4.visible = False
    elif self.frequency_option_1.text == 'Monthly':
      self.frequency_option_1.text = 'Daily'
      self.frequency_days_label.visible = False
      self.frequency_option_3.visible = False
      self.frequency_picker.visible = False

  def notification_repetition_value_click(self, **event_args):
    if self.notif_rep_value.text == 'Show artists again':
      self.notif_rep_value.text = 'Show artists twice'
      self.notif_rep_value.role = 'genre-box'
    elif self.notif_rep_value.text == 'Show artists twice':
      self.notif_rep_value.text = 'Repetitive'
      self.notif_rep_value.role = 'genre-box'
    elif self.notif_rep_value.text == 'Repetitive':
      self.notif_rep_value.text = 'Show artists again'
      self.notif_rep_value.role = 'genre-box'
      
  # def frequency_option_3_click(self, **event_args):
  #   if self.frequency_option_3.text == 'Monday':
  #     self.frequency_option_3.text = 'Tuesday'
  #     self.frequency_option_3.role = 'genre-box'
  #   elif self.frequency_option_3.text == 'Tuesday':
  #     self.frequency_option_3.text = 'Wednesday'
  #     self.frequency_option_3.role = 'genre-box'
  #   elif self.frequency_option_3.text == 'Wednesday':
  #     self.frequency_option_3.text = 'Thursday'
  #     self.frequency_option_3.role = 'genre-box'
  #   elif self.frequency_option_3.text == 'Thursday':
  #     self.frequency_option_3.text = 'Friday'
  #     self.frequency_option_3.role = 'genre-box'
  #   elif self.frequency_option_3.text == 'Friday':
  #     self.frequency_option_3.text = 'Monday'
  #     self.frequency_option_3.role = 'genre-box'

  def metrics_option_1_click(self, **event_args):
    if self.metrics_option_1.text == 'Top Fits':
      self.metrics_option_1.text = 'Growing Fits'
      self.frequency_option_1.role = 'genre-box'
      self.min_growth_fit.visible = True
    elif self.metrics_option_1.text == 'Growing Fits':
      self.metrics_option_1.text = 'Releasing Fits'
      self.frequency_option_1.role = 'genre-box'
      self.min_growth_fit.visible = False
      self.max_days_since_rel.visible = True
    elif self.metrics_option_1.text == 'Releasing Fits':
      self.metrics_option_1.text = 'Top Fits'
      self.frequency_option_1.role = 'genre-box'
      self.max_days_since_rel.visible = False

  def update_notification_1(self, **event_args):
    if self.frequency_option_1.text == 'Daily':
      freq_2 = None
      freq_3 = None
    elif self.frequency_option_1.text == 'Every X Days':
      freq_2 = self.frequency_option_2.text
      freq_3 = None
    elif self.frequency_option_1.text == 'Monthly':
      freq_2 = None
      freq_3 = self.frequency_picker.date
    
    if self.min_growth_value.text == '':
      min_growth_value = None
    else:
      min_growth_value = self.min_growth_value.text

    if self.days_since_rel_field_value.text == '':
      release_days = None
    else:
      release_days = self.days_since_rel_field_value.text
      
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
                      repetition = 'Show artists again',
                      rated = False,
                      watchlist = None,
                      release_days = release_days,
                      min_grow_fit = min_growth_value ,
                      model_ids = [28])

  # def edit_icon_click(self, **event_args):
  #   if self.name_link.visible is True: 
  #     self.name_link.visible = False
  #     self.model_name_text.visible = True
  #     self.model_name_text.text = self.name_link.text
  #     self.edit_icon.icon = 'fa:save'
  #   else:
  #     self.model_name_text.visible = False
  #     self.name_link.visible = True
  #     self.name_link.text = self.model_name_text.text
  #     self.edit_icon.icon = 'fa:pencil'

  def edit_icon_click_2(self, **event_args):
    if self.name_link.visible is True: 
      self.name_link.visible = False
      self.model_name_text_2.visible = True
      self.model_name_text_2.text = self.name_link.text
      # self.edit_icon.icon = 'fa:save'
    else:
      self.model_name_text_2.visible = False
      self.name_link.visible = True
      self.name_link.text = self.model_name_text_2.text
      # self.edit_icon.icon = 'fa:pencil'


