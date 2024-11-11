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

    # type specific content
    if self.item["type"] == 'mail':
      self.name.icon = 'fa:envelope-o'

    elif self.item["type"] == 'playlist':
      self.name.icon = 'fa:spotify'

  # RATED BUTTON
  def artist_selection_option_click(self, **event_args):
    if self.artist_selection_option.text == 'rated':
      self.artist_selection_option.text = 'unrated'
      self.artist_selection_option.role = 'genre-box'
    elif self.artist_selection_option.text == 'unrated':
      self.artist_selection_option.text = 'all'
      self.artist_selection_option.role = 'genre-box-deselect'
    elif self.artist_selection_option.text == 'all':
      self.artist_selection_option.text = 'rated'
      self.artist_selection_option.role = 'genre-box'
    # self.refresh_table()

  # WATCHLIST BUTTON
  def link_watchlist_click(self, **event_args):
    if self.watchlist_selection_option.text == 'on watchlist':
      self.watchlist_selection_option.text = 'not on watchlist'
      self.watchlist_selection_option.role = 'genre-box'
    elif self.watchlist_selection_option.text == 'not on watchlist':
      self.watchlist_selection_option.text = 'all'
      self.watchlist_selection_option.role = 'genre-box-deselect'
    elif self.watchlist_selection_option.text == 'all':
      self.watchlist_selection_option.text = 'on watchlist'
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
      self.frequency_days_option.visible = True
    elif self.frequency_option_1.text == 'Every X Days':
      self.frequency_option_1.text = 'Monthly'
      self.frequency_option_1.role = 'genre-box'
      self.frequency_option_2.visible = True
      self.frequency_option_2.text = 'Starting:'
      self.frequency_option_2.role = ''
      self.frequency_option_3.visible = True
      self.frequency_option_3.text = 'Monday'  
      self.frequency_days_option.visible = False
    elif self.frequency_option_1.text == 'Monthly':
       self.frequency_option_1.text = 'Daily'
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