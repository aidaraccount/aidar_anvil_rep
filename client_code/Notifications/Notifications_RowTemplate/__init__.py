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
  
  def update_notifications(self, **event_args):
    # anvil.server.call('update_notification',
    #                   notification_id = self.item["notification_id"],
    #                   type = self.item["type"],
    #                   name = self.name.text,
    #                   active =,
    #                   freq_1 =,
    #                   freq_2 =,
    #                   freq_3 =,
    #                   metric =,
    #                   no_artists = self.no_artists_box.text,
    #                   repetition =,
    #                   rated =,
    #                   watchlist =,
    #                   model_ids =,
    #                   release_days =,
    #                   min_grow_fit =)
    pass
