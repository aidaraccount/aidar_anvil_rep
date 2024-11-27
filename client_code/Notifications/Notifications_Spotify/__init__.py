from ._anvil_designer import Notifications_SpotifyTemplate
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


class Notifications_Spotify(Notifications_SpotifyTemplate):
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
    if self.item["type"] == "mail":
      self.name_link.icon = "fa:envelope-o"
    elif self.item["type"] == "playlist":
      self.name_link.icon = "fa:spotify"

    # activate/ deactivate Button
    if self.item["active"] is True:
      self.activate.visible = False
      self.deactivate.visible = True
      # self.notification_status.text = 'Notification is active'
    else:
      self.activate.visible = True
      self.deactivate.visible = False
      # self.notification_status.text = 'Notification is inactive'

    # A) Frequency
    self.frequency_option_1.text = self.item["freq_1"]
    self.frequency_option_2.text = self.item["freq_2"]
    self.frequency_picker.date = self.item["freq_3"]
    # self.weekdays.text = self.item["freq_3"]

    if self.frequency_option_1.text == "Daily":
      self.flow_panel_freq_2.visible = False
      self.flow_panel_freq_3.visible = False
    elif self.frequency_option_1.text == "Every X Days":
      self.flow_panel_freq_2.visible = True
      self.flow_panel_freq_3.visible = True
    elif self.frequency_option_1.text == "Monthly":
      self.flow_panel_freq_2.visible = False
      self.flow_panel_freq_3.visible = True

    # B) General
    self.no_artists_box.text = self.item["no_artists"]
    self.notif_rep_value.text = self.item["repetition_1"]
    self.artist_rep_x_days_freq.text = self.item["repetition_2"]
    if self.item["repetition_1"] == "Repeat after X days":
      self.column_panel_rep.visible = True
    else:
      self.column_panel_rep.visible = False

    # C) Metric
    self.metrics_option_1.text = self.item["metric"]
    self.days_since_rel_field_value.text = self.item["release_days"]

    if self.item["min_grow_fit"] is None:
      self.min_growth_value.text = 0
    else:
      self.min_growth_value.text = int(
        "{:.0f}".format(float(self.item["min_grow_fit"]) * 100)
      )

    if self.metrics_option_1.text == "Growing Fits":
      self.min_growth_fit.visible = True
    elif self.metrics_option_1.text == "Releasing Fits":
      self.max_days_since_rel.visible = True

    # D) Selection Parameters
    # artist selection
    if self.item["rated"] is True:
      self.artist_selection_option.text = "Rated"
    elif self.item["rated"] is False:
      self.artist_selection_option.text = "Unrated"
    elif self.item["rated"] is None:
      self.artist_selection_option.text = "All"

    # watchlist selection
    if self.item["watchlist"] is True:
      self.watchlist_selection_option.text = "On watchlist"
    elif self.item["watchlist"] is False:
      self.watchlist_selection_option.text = "Not on watchlist"
    elif self.item["watchlist"] is None:
      self.watchlist_selection_option.text = "All"

    # model selection
    models = json.loads(anvil.server.call("get_model_ids", user["user_id"]))
    active_models = self.item["model_ids"]

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

  def frequency_option_2_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.frequency_option_1.text == "Every X Days":
      if (
        not self.frequency_option_2.text.strip()
        or not self.frequency_option_2.text.isdigit()
        or int(self.frequency_option_2.text) < 1
      ):
        self.every_x_days_warning.visible = True
      else:
        self.every_x_days_warning.visible = False
        self.update_notification_1()

  def date_picker_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.frequency_option_1.text in ["Every X Days", "Monthly"]:
      print(self.frequency_picker.date)
      if self.frequency_picker.date is None:
        self.every_x_days_start_warning.visible = True
      else:
        self.every_x_days_start_warning.visible = False
        self.update_notification_1()

  def artist_rep_x_days_freq_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.notif_rep_value.text == "Repeat after X days":
      if (
        not self.artist_rep_x_days_freq.text.strip()
        or not self.artist_rep_x_days_freq.text.isdigit()
        or int(self.artist_rep_x_days_freq.text) < 1
      ):
        self.artist_rep_x_days_freq_warning.visible = True
      else:
        self.artist_rep_x_days_freq_warning.visible = False
        self.update_notification_1()

  def min_growth_value_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.metrics_option_1.text == "Growing Fits":
      if (
        not self.min_growth_value.text.strip()
        or not self.min_growth_value.text.isdigit()
        or int(self.min_growth_value.text) < 0
      ):
        self.min_growth_warning.visible = True
      else:
        self.min_growth_warning.visible = False
        self.update_notification_1()

  def max_days_since_rel_lost_focus(self, **event_args):
    # Validate number of days only if "Every X Days" is selected
    if self.metrics_option_1.text == "Releasing Fits":
      if (
        not self.days_since_rel_field_value.text.strip()
        or not self.days_since_rel_field_value.text.isdigit()
      ):
        self.days_since_rel_field_warning.visible = True
      else:
        self.days_since_rel_field_warning.visible = False
        self.update_notification_1()

  def update_notification_1(self, **event_args):
    # Validate the no_artists_box input (ensure it's between 1 and 20)
    try:
      if not self.no_artists_box.text.strip():  # Check if the field is empty
        # alert("The number of artists field cannot be empty. Please enter a value between 1 and 20.",
        #       title="Missing Input", buttons=[("OK", "OK")], role=["remove-focus"])
        self.max_number_artist_warning.visible = True
        return  # Stop execution if the field is empty
      else:
        self.max_number_artist_warning.visible = False
      no_artists = int(self.no_artists_box.text)
      if no_artists < 1 or no_artists > 50:
        self.max_number_artist_warning.visible = True
        return
    except ValueError:
      self.max_number_artist_warning.visible = True
      return  # Stop execution if the input is not a number

    if self.frequency_option_1.text == "Daily":
      freq_2 = None
      freq_3 = None
    elif self.frequency_option_1.text == "Every X Days":
      freq_2 = self.frequency_option_2.text
      freq_3 = self.frequency_picker.date
    elif self.frequency_option_1.text == "Monthly":
      freq_2 = None
      freq_3 = self.frequency_picker.date

    # artist selection = self.item["rated"] True(Rated) False None(All)
    options = {"Rated": True, "Unrated": False, "All": None}
    artist_selection_option = options.get(self.artist_selection_option.text)

    # watchilist selection = self.item["watchlist"] True(On watchlist) False None(All)
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

    # model_ids = []
    # for component in self.flow_panel_models.get_components():
    #   if isinstance(component, Link):
    #     if component.role == 'genre-box':
    #       model_ids.append(component.tag)

    # Collect selected model IDs
    model_ids = []
    for component in self.flow_panel_models.get_components():
      if (
        isinstance(component, Link) and component.role == "genre-box"
      ):  # Only active models
        model_ids.append(component.tag)

    # Check if any models are selected
    if not model_ids:
      self.models_warning.visible = True
      return  # Stop execution if no models are selected
    else:
      self.models_warning.visible = False

    anvil.server.call(
      "update_notification",
      notification_id=self.item["notification_id"],
      type=self.item["type"],
      name=self.name_link.text,
      active=self.deactivate.visible,
      freq_1=self.frequency_option_1.text,
      freq_2=freq_2,
      freq_3=freq_3,
      metric=self.metrics_option_1.text,
      no_artists=self.no_artists_box.text,
      repetition_1=self.notif_rep_value.text,
      repetition_2=self.artist_rep_x_days_freq.text,
      rated=artist_selection_option,
      watchlist=watchlist_selection_option,
      release_days=release_days,
      min_grow_fit=min_growth_value,
      model_ids=model_ids,
    )

  def activate_notification(self, **event_args):
    if self.activate.visible is True:
      self.activate.visible = False
      self.deactivate.visible = True
      # self.notification_status.text = 'Notification is active'
      Notification(
        "", title=f'"{self.name_link.text}" is activated', style="success"
      ).show()
    else:
      self.activate.visible = True
      self.deactivate.visible = False
      # self.notification_status.text = 'Notification is inactive'
      Notification(
        "", title=f'"{self.name_link.text}" is no longer active', style="success"
      ).show()
    self.update_notification_1()

  # RATED BUTTON
  def artist_selection_option_click(self, **event_args):
    if self.artist_selection_option.text == "Rated":
      self.artist_selection_option.text = "Unrated"
    elif self.artist_selection_option.text == "Unrated":
      self.artist_selection_option.text = "All"
    elif self.artist_selection_option.text == "All":
      self.artist_selection_option.text = "Rated"
    self.update_notification_1()

  # WATCHLIST BUTTON
  def watchlist_selection_option_click(self, **event_args):
    if self.watchlist_selection_option.text == "On watchlist":
      self.watchlist_selection_option.text = "Not on watchlist"
    elif self.watchlist_selection_option.text == "Not on watchlist":
      self.watchlist_selection_option.text = "All"
    elif self.watchlist_selection_option.text == "All":
      self.watchlist_selection_option.text = "On watchlist"
    self.update_notification_1()

  def delete_notification_click(self, **event_args):
    anvil.server.call(
      "delete_notification", notification_id=self.item["notification_id"]
    )

    self.parent.parent.parent.parent.get_playlist()

  def frequency_option_1_click(self, **event_args):
    if self.frequency_option_1.text == "Daily":
      self.frequency_option_1.text = "Every X Days"
      self.flow_panel_freq_2.visible = True
      self.weekdays.visible = False
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
      self.weekdays.visible = False
      self.flow_panel_freq_3.visible = False
    self.update_notification_1()

  def notification_repetition_value_click(self, **event_args):
    if self.notif_rep_value.text == "Suggest artists once":
      self.notif_rep_value.text = "Repeat suggestions"
    elif self.notif_rep_value.text == "Repeat suggestions":
      self.notif_rep_value.text = "Repeat after X days"
      self.column_panel_rep.visible = True
    elif self.notif_rep_value.text == "Repeat after X days":
      self.notif_rep_value.text = "Suggest artists once"
      self.column_panel_rep.visible = False

    self.update_notification_1()

  def metrics_option_1_click(self, **event_args):
    if self.metrics_option_1.text == "Top Fits":
      self.metrics_option_1.text = "Growing Fits"
      self.min_growth_fit.visible = True
    elif self.metrics_option_1.text == "Growing Fits":
      self.metrics_option_1.text = "Releasing Fits"
      self.min_growth_fit.visible = False
      self.max_days_since_rel.visible = True
      self.min_growth_warning.visible = False
    elif self.metrics_option_1.text == "Releasing Fits":
      self.metrics_option_1.text = "Top Fits"
      self.max_days_since_rel.visible = False
      self.days_since_rel_field_warning.visible = False
    self.update_notification_1()

  def edit_icon_click_2(self, **event_args):
    if self.name_link.visible is True:
      self.name_link.visible = False
      self.model_name_text.visible = True
      self.model_name_text.text = self.name_link.text
      self.model_name_text.focus()

  def edit_icon_click_2_lose_focus(self, **event_args):
    if self.model_name_text.visible is True:
      self.model_name_text.visible = False
      self.name_link.visible = True
      self.name_link.text = self.model_name_text.text
      self.update_notification_1()

  def edit_icon_click_2_enter(self, **event_args):
    if self.model_name_text.visible is True:
      self.model_name_text.visible = False
      self.name_link.visible = True
      self.name_link.text = self.model_name_text.text
      self.update_notification_1()

  # MODEL BUTTONS
  def create_activate_model_handler(self, model_id):
    def handler(**event_args):
      self.activate_model(model_id)

    return handler

  # change active status
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
    self.update_notification_1()

  # def weekdays_click(self, **event_args):
  #   if self.weekdays.text == 'Monday':
  #     self.weekdays.text = 'Tuesday'
  #   elif self.weekdays.text == 'Tuesday':
  #     self.weekdays.text = 'Wednesday'
  #   elif self.weekdays.text == 'Wednesday':
  #     self.weekdays.text = 'Thursday'
  #   elif self.weekdays.text == 'Thursday':
  #     self.weekdays.text = 'Friday'
  #   elif self.weekdays.text == 'Friday':
  #     self.weekdays.text = 'Monday'
