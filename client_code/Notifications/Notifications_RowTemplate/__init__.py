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
    self.name.text = self.item["name"]
    self.no_artists_box.text = self.item["no_artists"]
    self.min_growth_value.text = self.item["min_grow_fit"]
    self.metrics_option_1.text = self.item["metric"]
    self.frequency_option_1.text = self.item["freq_1"]
    self.frequency_option_2.text = self.item["freq_2"]
    self.frequency_option_3.text = self.item["freq_3"]

    # type specific content
    if self.item["type"] == 'mail':
      self.name.icon = 'fa:envelope-o'

    elif self.item["type"] == 'playlist':
      self.name.icon = 'fa:spotify'

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
    # self.refresh_table()

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
    # self.refresh_table()
  
  def update_notification(self, **event_args):
    anvil.server.call('update_notification',
                      notification_id = self.item["notification_id"],
                      type = self.item["type"],
                      name = self.name.text,
                      active = True,
                      freq_1 = 'daily',
                      freq_2 = None,
                      freq_3 = None,
                      metric = 'Growing Fits',
                      no_artists = self.no_artists_box.text,
                      repetition = 'Show artists again',
                      rated = False,
                      watchlist = None,
                      release_days = None,
                      min_grow_fit = 0.75,
                      model_ids = [2, 129])

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
    # self.refresh_table()

  def frequency_option_3_click(self, **event_args):
    if self.frequency_option_3.text == 'Monday':
      self.frequency_option_3.text = 'Tuesday'
      self.frequency_option_3.role = 'genre-box'
    elif self.frequency_option_3.text == 'Tuesday':
      self.frequency_option_3.text = 'Wednesday'
      self.frequency_option_3.role = 'genre-box'
    elif self.frequency_option_3.text == 'Wednesday':
      self.frequency_option_3.text = 'Thursday'
      self.frequency_option_3.role = 'genre-box'
    elif self.frequency_option_3.text == 'Thursday':
      self.frequency_option_3.text = 'Friday'
      self.frequency_option_3.role = 'genre-box'
    elif self.frequency_option_3.text == 'Friday':
      self.frequency_option_3.text = 'Monday'
      self.frequency_option_3.role = 'genre-box'
    # self.refresh_table()

  def metrics_option_1_click(self, **event_args):
    if self.metrics_option_1.text == 'Top Fits':
      self.metrics_option_1.text = 'Growing Fits'
      self.frequency_option_1.role = 'genre-box'
    elif self.metrics_option_1.text == 'Growing Fits':
      self.metrics_option_1.text = 'Releasing Fits'
      self.frequency_option_1.role = 'genre-box'
    elif self.metrics_option_1.text == 'Releasing Fits':
      self.metrics_option_1.text = 'Top Fits'
      self.frequency_option_1.role = 'genre-box'
    # self.refresh_table()

  
  def update_notification_1(self, **event_args):
    if self.frequency_option_1.text == 'Daily':
      freq_2 = None
      freq_3 = None
    elif self.frequency_option_1.text == 'Every X Days':
      freq_2 = self.frequency_option_2.text
      freq_3 = None
    elif self.frequency_option_1.text == 'Monthly':
      freq_2 = None
      freq_3 = self.frequency_picker.text 

    
    if self.min_growth_value.text == '':
      min_growth_value = None
    else:
      min_growth_value = self.min_growth_value.text
    anvil.server.call('update_notification',
                      notification_id = self.item["notification_id"],
                      type = self.item["type"],
                      name = self.name.text,
                      active = True,
                      freq_1 = self.frequency_option_1.text,
                      freq_2 = freq_2,
                      freq_3 = freq_3,
                      metric = self.metrics_option_1.text,
                      no_artists = self.no_artists_box.text,
                      repetition = 'Show artists again',
                      rated = False,
                      watchlist = None,
                      release_days = None,
                      min_grow_fit = min_growth_value ,
                      model_ids = [2, 129])

  def edit_icon_click(self, **event_args):
    if self.name.visible is True: 
      self.name.visible = False
      self.model_name_text.visible = True
      self.model_name_text.text = self.name.text
      self.edit_icon.icon = 'fa:save'
    else:
      self.model_name_text.visible = False
      self.name.visible = True
      self.name.text = self.model_name_text.text
      self.edit_icon.icon = 'fa:pencil'
      anvil.server.call('update_notification',
                      notification_id = self.item["notification_id"],
                      type = self.item["type"],
                      name = self.name.text,
                      active = True,
                      freq_1 = self.frequency_option_1.text,
                      freq_2 = None,
                      freq_3 = None,
                      metric = self.metrics_option_1.text,
                      no_artists = self.no_artists_box.text,
                      repetition = 'Show artists again',
                      rated = False,
                      watchlist = None,
                      release_days = None,
                      min_grow_fit = self.min_growth_value.text ,
                      model_ids = [2, 129])
      # if res == 'success':
      #   get_open_form().refresh_models_components()
      #   Notification("",
      #     title="Model updated!",
      #     style="success").show()

  def edit_icon_click_2(self, **event_args):
    if self.name_link.visible is True: 
      self.name_link.visible = False
      self.model_name_text_2.visible = True
      self.model_name_text_2.text = self.name_link.text
      self.edit_icon.icon = 'fa:save'
    else:
      self.model_name_text_2.visible = False
      self.name_link.visible = True
      self.name_link.text = self.model_name_text_2.text
      self.edit_icon.icon = 'fa:pencil'
      anvil.server.call('update_notification',
                      notification_id = self.item["notification_id"],
                      type = self.item["type"],
                      name = self.name.text,
                      active = True,
                      freq_1 = self.frequency_option_1.text,
                      freq_2 = None,
                      freq_3 = None,
                      metric = self.metrics_option_1.text,
                      no_artists = self.no_artists_box.text,
                      repetition = 'Show artists again',
                      rated = False,
                      watchlist = None,
                      release_days = None,
                      min_grow_fit = self.min_growth_value.text ,
                      model_ids = [2, 129])