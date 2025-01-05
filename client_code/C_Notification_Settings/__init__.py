from ._anvil_designer import C_Notification_SettingsTemplate
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
from ..nav import click_link, click_button, logout, login_check, load_var, save_var


class C_Notification_Settings(C_Notification_SettingsTemplate):
  def __init__(self, items, notification_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # vars
    global user
    user = anvil.users.get_user()
    items = items[0]
    self.items = items
    self.notification_id = notification_id

    # visibility
    self.column_panel_min_max.visible = False
    
    # -------------
    # HEADER
    # a) Name & its Icon
    self.notification_name.text = items["name"]
    if items["type"] == "mail":
      self.notification_name.icon = "fa:envelope-o"
    elif items["type"] == "playlist":
      self.notification_name.icon = "fa:spotify"

    # ----------
    # STATIC INFORMATION
    # a) static mail information
    if items["type"] == "mail":
      self.playlist_status.visible = False
      
    # b) static playlist information
    if items["type"] == "playlist":
      self.mail_status.visible = False
      
      if items["sp_playlist_id"] is None or items["sp_playlist_id"] == "":
        self.playlist_in_creation.visible = True
        self.last_updated_spotify.visible = False
      else:
        self.playlist_url.visible = True
        self.last_updated_spotify.visible = True
        self.playlist_url.url = (f"https://open.spotify.com/playlist/{items['sp_playlist_id']}")
        self.playlist_url.text = (f"https://open.spotify.com/playlist/{items['sp_playlist_id']}")
        self.larst_updated_value.text = items["last_update"][:-3]

    # ----------
    # MAIL SETTINGS
    self.mail_settings.visible = False
    if items["type"] == "mail":
      self.frequency_master_1.visible = True
      self.last_updated_spotify.visible = False

      # activate/ deactivate Button
      if items["active"] is True:
        self.activate.visible = False
        self.deactivate.visible = True
        self.mail_status_details.visible = True
        self.mail_status_active.text = 'notification is active!'
        self.mail_status_active.role = ['header-7', 'orange']
      else:
        self.activate.visible = True
        self.deactivate.visible = False
        self.mail_status_details.visible = False
        self.mail_status_active.text = 'notification is deactivated'
        self.mail_status_active.role = ['header-7', 'white']

      # load settings
      self.frequency_option_1.text = items["freq_1"]
      self.frequency_option_2.text = items["freq_2"]
      self.frequency_picker.date = items["freq_3"]

      if self.frequency_option_1.text == "Daily":
        self.flow_panel_freq_2.visible = False
        self.flow_panel_freq_3.visible = False
        self.mail_status_details.text = 'Mail is sent daily!'
      elif self.frequency_option_1.text == "Every X Days":
        self.flow_panel_freq_2.visible = True
        self.flow_panel_freq_3.visible = True
        self.mail_status_details.text = f'Mail is sent every {self.frequency_option_2.text} days starting {self.frequency_picker.date}!'
      elif self.frequency_option_1.text == "Monthly":
        self.flow_panel_freq_2.visible = False
        self.flow_panel_freq_3.visible = True
        self.mail_status_details.text = f'Mail is sent monthly starting {self.frequency_picker.date}!'
    
    # ----------
    # NOTIFICATION SETTINGS
    # a) General
    self.no_artists_box.text = items["no_artists"]
    self.notif_rep_value.text = items["repetition_1"]
    self.artist_rep_x_days_freq.text = items["repetition_2"]
    if items["repetition_1"] == "Repeat after X days":
      self.column_panel_rep.visible = True
    else:
      self.column_panel_rep.visible = False

    # for playlists
    if items["type"] == "playlist":
      self.song_selection.visible = True
      self.no_latest_releases.visible = True

      self.song_selection_type.text = items["song_selection_1"]
      self.no_latest_rel_box_spotify.text = items["song_selection_2"]

    # b) Metric
    self.metrics_option_1.text = items["metric"]
    self.days_since_rel_field_value.text = items["release_days"]

    if items["min_grow_fit"] is None:
      self.min_growth_value.text = 0
    else:
      self.min_growth_value.text = int(
        "{:.0f}".format(float(items["min_grow_fit"]) * 100)
      )

    if self.metrics_option_1.text == "Growing Fits":
      self.min_growth_fit.visible = True
    elif self.metrics_option_1.text == "Releasing Fits":
      self.max_days_since_rel.visible = True

    # c) Selection Parameters
    # artist selection
    if items["rated"] is True:
      self.artist_selection_option.text = "Rated"
    elif items["rated"] is False:
      self.artist_selection_option.text = "Unrated"
    elif items["rated"] is None:
      self.artist_selection_option.text = "All"

    # watchlist selection
    if items["watchlist"] is True:
      self.watchlist_selection_option.text = "On watchlist"
    elif items["watchlist"] is False:
      self.watchlist_selection_option.text = "Not on watchlist"
    elif items["watchlist"] is None:
      self.watchlist_selection_option.text = "All"

    # model selection
    models = json.loads(anvil.server.call("get_model_ids", user["user_id"]))
    active_models = items["model_ids"]

    for i in range(0, len(models)):
      if models[i]["model_id"] in active_models:
        model_link = Link(
          text=models[i]["model_name"], tag=models[i]["model_id"], role="genre-box"
        )
      else:
        model_link = Link(
          text=models[i]["model_name"],
          tag=models[i]["model_id"],
          role="genre-box-deselect",
        )

      if models[i]["fully_trained"] is False:
        model_link = Link(
          text=models[i]["model_name"],
          tag=models[i]["model_id"],
          role="genre-box-deactive",
        )

      model_link.set_event_handler(
        "click", self.create_activate_model_handler(models[i]["model_id"])
      )
      self.flow_panel_models.add_component(model_link)

    # # set toggle
    # toggle = load_var('toggle')
    # if toggle == 'down':
    #   self.column_panel_min_max.visible = True
    #   self.edit_icon.icon = "fa:save"
    # else:
    #   self.column_panel_min_max.visible = False
    #   self.edit_icon.icon = "fa:pencil"

  
  # NOTIFICATION MODIFICATION
  def update_notification(self, **event_args):
    # prepare data
    # # frequency 2 and 3
    # if self.frequency_option_1.text == "Daily":
    #   freq_2 = None
    #   freq_3 = None
    # elif self.frequency_option_1.text == "Every X Days":
    #   freq_2 = self.frequency_option_2.text
    #   freq_3 = self.frequency_picker.date
    # elif self.frequency_option_1.text == "Monthly":
    #   freq_2 = None
    #   freq_3 = self.frequency_picker.date

    # artist selection = self.items["rated"] True(Rated) False None(All)
    options = {"Rated": True, "Unrated": False, "All": None}
    artist_selection_option = options.get(self.artist_selection_option.text)

    # watchilist selection = self.items["watchlist"] True(On watchlist) False None(All)
    options = {"On watchlist": True, "Not on watchlist": False, "All": None}
    watchlist_selection_option = options.get(self.watchlist_selection_option.text)

    if self.min_growth_value.text == "":
      min_growth_value = None
    elif self.min_growth_value.text.isalpha():
      min_growth_value = None
    else:
      min_growth_value = float(self.min_growth_value.text) / 100

    if self.days_since_rel_field_value.text == "":
      release_days = None
    else:
      release_days = self.days_since_rel_field_value.text

    # Collect selected model IDs
    model_ids = []
    for component in self.flow_panel_models.get_components():
      if (
        isinstance(component, Link) and component.role == "genre-box"
      ):  # Only active models
        model_ids.append(component.tag)

    # do the update
    anvil.server.call(
      "update_notification",
      notification_id=self.items["notification_id"],
      type=self.items["type"],
      name=self.notification_name.text,
      active=self.deactivate.visible,
      freq_1=self.frequency_option_1.text,
      freq_2=self.frequency_option_2.text,
      freq_3=self.frequency_picker.date,
      metric=self.metrics_option_1.text,
      no_artists=self.no_artists_box.text,
      repetition_1=self.notif_rep_value.text,
      repetition_2=self.artist_rep_x_days_freq.text,
      rated=artist_selection_option,
      watchlist=watchlist_selection_option,
      release_days=release_days,
      min_grow_fit=min_growth_value,
      model_ids=model_ids,
      song_selection_1=self.song_selection_type.text,
      song_selection_2=self.no_latest_rel_box_spotify.text,
    )

    self.parent.parent.parent.get_all_notifications(self.notification_id)

  def activate_notification(self, **event_args):
    if self.activate.visible is True:
      self.activate.visible = False
      self.deactivate.visible = True
    else:
      self.activate.visible = True
      self.deactivate.visible = False
      
    self.button_save_mail.role = ['header-6', 'call-to-action-button']
    self.edit_icon.role = ['icon-button']

  
  def delete_notification_click(self, **event_args):
    result = alert(title='Sure to delete?',
          content="Are you sure to delete this notification?",
          buttons=[
            ("Cancel", "Cancel"),
            ("Delete", "Delete")
          ])
    if result == 'Delete':
      anvil.server.call("delete_notification", notification_id=self.items["notification_id"])
      self.parent.parent.parent.get_all_notifications(None)

  
  # BUTTON FUNCTIONALITIES
  # name
  def edit_icon_click_2(self, **event_args):  # !!!!!!!! TO DELETE??????
    self.notification_name.visible = False
    self.model_name_text.visible = True
    self.model_name_text.text = self.notification_name.text
    self.model_name_text.focus()

  # mail settings
  def frequency_option_1_click(self, **event_args):
    if self.frequency_option_1.text == "Daily":
      self.frequency_option_1.text = "Every X Days"
      self.flow_panel_freq_2.visible = True
      self.frequency_days_label_days.visible = True
      self.frequency_days_label_days.text = "Days"
      self.flow_panel_freq_3.visible = True
    elif self.frequency_option_1.text == "Every X Days":
      self.frequency_option_1.text = "Monthly"
      self.flow_panel_freq_2.visible = False
      self.flow_panel_freq_3.visible = True
      self.frequency_days_label_days.visible = False
    elif self.frequency_option_1.text == "Monthly":
      self.frequency_option_1.text = "Daily"
      self.flow_panel_freq_2.visible = False
      self.flow_panel_freq_3.visible = False
    self.button_save_mail.role = ['header-6', 'call-to-action-button']
    self.edit_icon.role = ['icon-button']

  # selection settings
  def artist_selection_option_click(self, **event_args):
    if self.artist_selection_option.text == "Rated":
      self.artist_selection_option.text = "Unrated"
    elif self.artist_selection_option.text == "Unrated":
      self.artist_selection_option.text = "All"
    elif self.artist_selection_option.text == "All":
      self.artist_selection_option.text = "Rated"
    self.button_save.role = ['header-6', 'call-to-action-button']
    self.edit_icon.role = ['icon-button']

  def watchlist_selection_option_click(self, **event_args):
    if self.watchlist_selection_option.text == "On watchlist":
      self.watchlist_selection_option.text = "Not on watchlist"
    elif self.watchlist_selection_option.text == "Not on watchlist":
      self.watchlist_selection_option.text = "All"
    elif self.watchlist_selection_option.text == "All":
      self.watchlist_selection_option.text = "On watchlist"
    self.button_save.role = ['header-6', 'call-to-action-button']
    self.edit_icon.role = ['icon-button']

  def notification_repetition_value_click(self, **event_args):
    if self.notif_rep_value.text == "Suggest artists once":
      self.notif_rep_value.text = "Repeat suggestions"
    elif self.notif_rep_value.text == "Repeat suggestions":
      self.notif_rep_value.text = "Repeat after X days"
      self.column_panel_rep.visible = True
    elif self.notif_rep_value.text == "Repeat after X days":
      self.notif_rep_value.text = "Suggest artists once"
      self.column_panel_rep.visible = False
    self.button_save.role = ['header-6', 'call-to-action-button']
    self.edit_icon.role = ['icon-button']

  def metrics_option_1_click(self, **event_args):
    if self.metrics_option_1.text == "Top Fits":
      self.metrics_option_1.text = "Growing Fits"
      self.min_growth_fit.visible = True
    elif self.metrics_option_1.text == "Growing Fits":
      self.metrics_option_1.text = "Releasing Fits"
      self.min_growth_fit.visible = False
      self.max_days_since_rel.visible = True
    elif self.metrics_option_1.text == "Releasing Fits":
      self.metrics_option_1.text = "Top Fits"
      self.max_days_since_rel.visible = False
    self.button_save.role = ['header-6', 'call-to-action-button']
    self.edit_icon.role = ['icon-button']

  
  # LOST FOCUS CHECKS
  # name
  def edit_icon_click_2_lose_focus(self, **event_args):   # !!!!!!!! TO DELETE??????
    self.model_name_text.visible = False
    self.notification_name.visible = True
    self.notification_name.text = self.model_name_text.text
    self.button_save_mail.role = ['header-6', 'call-to-action-button']
    self.edit_icon.role = ['icon-button']

  # mail settings
  def frequency_option_2_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.frequency_option_1.text == "Every X Days":
      if (
        not self.frequency_option_2.text.strip()
        or not self.frequency_option_2.text.isdigit()
        or int(self.frequency_option_2.text) < 1
      ):
        self.every_x_days_warning.visible = True
        self.button_save_mail.role = ['header-6', 'call-to-action-button-disabled']
        self.edit_icon.role = ['icon-button-disabled']
      else:
        self.every_x_days_warning.visible = False
        self.button_save_mail.role = ['header-6', 'call-to-action-button']
        self.edit_icon.role = ['icon-button']

  def date_picker_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.frequency_option_1.text in ["Every X Days", "Monthly"]:
      if self.frequency_picker.date is None:
        self.every_x_days_start_warning.visible = True
        self.button_save_mail.role = ['header-6', 'call-to-action-button-disabled']
        self.edit_icon.role = ['icon-button-disabled']
      else:
        self.every_x_days_start_warning.visible = False
        self.button_save_mail.role = ['header-6', 'call-to-action-button']
        self.edit_icon.role = ['icon-button']

  # selection settings
  def artist_rep_x_days_freq_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.notif_rep_value.text == "Repeat after X days":
      if (
        not self.artist_rep_x_days_freq.text.strip()
        or not self.artist_rep_x_days_freq.text.isdigit()
        or int(self.artist_rep_x_days_freq.text) < 1
      ):
        self.artist_rep_x_days_freq_warning.visible = True
        self.button_save.role = ['header-6', 'call-to-action-button-disabled']
        self.edit_icon.role = ['icon-button-disabled']
      else:
        self.artist_rep_x_days_freq_warning.visible = False
        self.button_save.role = ['header-6', 'call-to-action-button']
        self.edit_icon.role = ['icon-button']

  def min_growth_value_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.metrics_option_1.text == "Growing Fits":
      if (
        not self.min_growth_value.text.strip()
        or not self.min_growth_value.text.isdigit()
        or int(self.min_growth_value.text) < 0
        or int(self.min_growth_value.text) > 100
      ):
        self.min_growth_warning.visible = True
        self.button_save.role = ['header-6', 'call-to-action-button-disabled']
        self.edit_icon.role = ['icon-button-disabled']
      else:
        self.min_growth_warning.visible = False
        self.button_save.role = ['header-6', 'call-to-action-button']
        self.edit_icon.role = ['icon-button']

  def max_days_since_rel_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.metrics_option_1.text == "Releasing Fits":
      if (
        not self.days_since_rel_field_value.text.strip()
        or not self.days_since_rel_field_value.text.isdigit()
      ):
        self.days_since_rel_field_warning.visible = True
        self.button_save.role = ['header-6', 'call-to-action-button-disabled']
        self.edit_icon.role = ['icon-button-disabled']
      else:
        self.days_since_rel_field_warning.visible = False
        self.button_save.role = ['header-6', 'call-to-action-button']
        self.edit_icon.role = ['icon-button']

  def no_latest_rel_box_spotify_lost_focus(self, **event_args):
    # Validate number latest releases only if "Latest Releases" is selected
    if self.song_selection_type.text == "Latest Releases":
      if (
        not self.no_latest_rel_box_spotify.text.strip()
        or not self.no_latest_rel_box_spotify.text.isdigit()
        or int(self.no_latest_rel_box_spotify.text) < 0
        or int(self.no_latest_rel_box_spotify.text) > 10
      ):
        self.no_latest_rel_box_spotify_warning.visible = True
        self.button_save.role = ['header-6', 'call-to-action-button-disabled']
        self.edit_icon.role = ['icon-button-disabled']
      else:
        self.no_latest_rel_box_spotify_warning.visible = False
        self.button_save.role = ['header-6', 'call-to-action-button']
        self.edit_icon.role = ['icon-button']

  def no_artists_box_lost_focus(self, **event_args):
    # Validate the no_artists_box input (ensure it's between 1 and 20)
    if (
      not self.no_artists_box.text.strip()
      or not self.no_artists_box.text.isdigit()
      or int(self.no_artists_box.text) < 0
      or int(self.no_artists_box.text) > 20
    ):
      self.max_number_artist_warning.visible = True
      self.button_save.role = ['header-6', 'call-to-action-button-disabled']
      self.edit_icon.role = ['icon-button-disabled']
    else:
      self.max_number_artist_warning.visible = False
      self.button_save.role = ['header-6', 'call-to-action-button']
      self.edit_icon.role = ['icon-button']

  
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
          if component.role == "genre-box-deactive":
            Notification(
              "",
              title="Model not fully trained yet - you need at least 50 ratings!",
              style="info",
            ).show()
          else:
            if component.role == "genre-box":
              component.role = "genre-box-deselect"
            else:
              component.role = "genre-box"

    # Check if any models are selected
    # a) ccollect selected model IDs
    model_ids = []
    for component in self.flow_panel_models.get_components():
      if (
        isinstance(component, Link) and component.role == "genre-box"
      ):  # Only active models
        model_ids.append(component.tag)

    # b) show warning or update_notification
    if not model_ids:
      self.models_warning.visible = True
      self.button_save_mail.role = ['header-6', 'call-to-action-button-disabled']
      self.edit_icon.role = ['icon-button-disabled']
    else:
      self.models_warning.visible = False
      self.button_save_mail.role = ['header-6', 'call-to-action-button']
      self.edit_icon.role = ['icon-button']

  def edit_icon_click(self, **event_args):
    if self.edit_icon.icon == "fa:pencil":
      # save_var('toggle', 'down')
      if self.items["type"] == "mail":
        self.mail_settings.visible = True
      else:
        self.mail_settings.visible = False
      self.column_panel_min_max.visible = True
      self.edit_icon.icon = "fa:save"
      self.edit_icon.role = ['icon-button-disabled']
    else:
      # save_var('toggle', 'up')
      self.mail_settings.visible = False
      print(self.column_panel_min_max.visible)
      self.column_panel_min_max.visible = False
      print(self.column_panel_min_max.visible)
      self.edit_icon.icon = "fa:pencil"
      self.edit_icon.role = ['icon-button']

  def button_save_mail_click(self, **event_args):
    if self.button_save_mail.role == ['header-6', 'call-to-action-button']:      
      # notification
      if self.activate.visible is True:
        Notification("", title=f'"{self.notification_name.text}" is no longer active', style="warning").show()
      else:
        Notification("", title=f'"{self.notification_name.text}" is activated!', style="success").show()
        
      # update icons & change button
      self.edit_icon_click()
      self.button_save_mail.role = ['header-6', 'call-to-action-button-disabled']
      self.edit_icon.role = ['icon-button-disabled']
      
      # save data (& reload notifications)
      self.update_notification()

  
  def button_save_click(self, **event_args):
    if self.button_save.role == ['header-6', 'call-to-action-button']:  
      # notification
      pass
      
      # update icons & change button
      self.edit_icon_click()
      self.button_save.role = ['header-6', 'call-to-action-button-disabled']
      self.edit_icon.role = ['icon-button-disabled']
      
      # save data
      self.update_notification()
