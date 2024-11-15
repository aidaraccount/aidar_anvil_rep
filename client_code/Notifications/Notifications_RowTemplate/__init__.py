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
    global user
    user = anvil.users.get_user()
    
    # general content
    self.name_link.text = self.item["name"]
    self.no_artists_box.text = self.item["no_artists"]
    self.metrics_option_1.text = self.item["metric"]
    self.frequency_option_1.text = self.item["freq_1"]
    self.frequency_option_2.text = self.item["freq_2"]
    self.weekdays.text = self.item["freq_3"]
    self.days_since_rel_field_value.text = self.item["release_days"]
    self.notif_rep_value.text = self.item["repetition"]
    self.frequency_picker.date = self.item["freq_3"]

    if self.item['min_grow_fit'] is None:
      self.min_growth_value.text = 0
    else:
      self.min_growth_value.text = float(self.item["min_grow_fit"])*100
    # Rated Value
    if self.item["rated"] is True:
      self.artist_selection_option.text = 'Rated'
    elif self.item["rated"] is False:
      self.artist_selection_option.text = 'Unrated'
    elif self.item["rated"] is None:
      self.artist_selection_option.text = 'All'

    # Watchlist Value
    if self.item["watchlist"] is True:
      self.watchlist_selection_option.text = 'On watchlist'
    elif self.item["watchlist"] is False:
      self.watchlist_selection_option.text = 'Not on watchlist'
    elif self.item["watchlist"] is None:
      self.watchlist_selection_option.text = 'All'
      
    # activate Notification
    if self.item["active"] is True:
      self.activate.visible = False
      self.deactivate.visible = True
      self.notification_status.text = 'Notification is active'
    else:
      self.activate.visible = True
      self.deactivate.visible = False
      self.notification_status.text = 'Notification is inactive'
    # type specific content
    if self.item["type"] == 'mail':
      self.name_link.icon = 'fa:envelope-o'
    elif self.item["type"] == 'playlist':
      self.name_link.icon = 'fa:spotify'

    if self.frequency_option_1.text == 'Every X Days':
      self.frequency_option_2.visible = True
      self.frequency_days_label_days.visible = True
      self.frequency_days_label_starting.visible = True
      self.frequency_picker.visible = True
    elif self.frequency_option_1.text == 'Monthly':
      self.frequency_days_label_starting.visible = True
      self.frequency_picker.visible = True

    if self.metrics_option_1.text == 'Growing Fits':
      self.min_growth_fit.visible = True
    elif self.metrics_option_1.text == 'Releasing Fits':
      self.max_days_since_rel.visible = True

    # models
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
          role='genre-box-deactive'
          )
      
      model_link.set_event_handler('click', self.create_activate_model_handler(models[i]["model_id"]))
      self.flow_panel_models.add_component(model_link)

  
  def activate_notification(self, **event_args):
    if self.activate.visible is True:
      self.activate.visible = False
      self.deactivate.visible = True
      self.notification_status.text = 'Notification is active'
    else:
      self.activate.visible = True
      self.deactivate.visible = False
      self.notification_status.text = 'Notification is inactive'
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
      self.frequency_days_label_starting.visible = True
      self.frequency_option_2.visible = True
      self.weekdays.visible = False
      self.frequency_days_label_days.visible = True
      self.frequency_days_label_days.text = 'Days'
      self.frequency_picker.visible = True
    elif self.frequency_option_1.text == 'Every X Days':
      self.frequency_option_1.text = 'Monthly'
      self.frequency_option_1.role = 'genre-box'
      self.frequency_days_label_starting.visible = True
      self.frequency_option_2.visible = False
      self.frequency_picker.visible = True
      self.frequency_days_label_days.visible = False
    elif self.frequency_option_1.text == 'Monthly':
      self.frequency_option_1.text = 'Daily'
      self.frequency_days_label_starting.visible = False
      self.weekdays.visible = False
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
      
  # def weekdays_click(self, **event_args):
  #   if self.weekdays.text == 'Monday':
  #     self.weekdays.text = 'Tuesday'
  #     self.weekdays.role = 'genre-box'
  #   elif self.weekdays.text == 'Tuesday':
  #     self.weekdays.text = 'Wednesday'
  #     self.weekdays.role = 'genre-box'
  #   elif self.weekdays.text == 'Wednesday':
  #     self.weekdays.text = 'Thursday'
  #     self.weekdays.role = 'genre-box'
  #   elif self.weekdays.text == 'Thursday':
  #     self.weekdays.text = 'Friday'
  #     self.weekdays.role = 'genre-box'
  #   elif self.weekdays.text == 'Friday':
  #     self.weekdays.text = 'Monday'
  #     self.weekdays.role = 'genre-box'

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
      freq_3 = self.frequency_picker.date
    elif self.frequency_option_1.text == 'Monthly':
      freq_2 = None
      freq_3 = self.frequency_picker.date

    # artist selection = self.item["rated"] True(Rated) False None(All)
    if self.artist_selection_option.text == 'Rated':
      artist_selection_option = True
    elif self.artist_selection_option.text == 'Unrated':
      artist_selection_option = False
    elif self.artist_selection_option.text == 'All':
      artist_selection_option = None

    # watchilist selection = self.item["watchlist"] True(On watchlist) False None(All)
    if self.watchlist_selection_option.text == 'On watchlist':
      watchlist_selection_option = True
    elif self.watchlist_selection_option.text == 'Not on watchlist':
      watchlist_selection_option = False
    elif self.watchlist_selection_option.text == 'All':
      watchlist_selection_option = None
      
    if self.min_growth_value.text == '':
      min_growth_value = None
    else:
      min_growth_value = float(self.min_growth_value.text)/100

    if self.days_since_rel_field_value.text == '':
      release_days = None
    else:
      release_days = self.days_since_rel_field_value.text

    model_ids = []
    for component in self.flow_panel_models.get_components():
      if isinstance(component, Link):
        if component.role == 'genre-box':
          model_ids.append(component.tag)
    
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
                      rated = artist_selection_option,
                      watchlist = watchlist_selection_option,
                      release_days = release_days,
                      min_grow_fit = min_growth_value ,
                      model_ids = model_ids)
    Notification("",
        title="The notification setting has been updated",
        style="success").show()

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

  # MODEL BUTTONS
  def create_activate_model_handler(self, model_id):
    def handler(**event_args):
      self.activate_model(model_id)
    return handler

  # change active status
  def activate_model(self, model_id):
    working_model = False
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
        else:
          pass
          
        # check for active model
        if component.role == 'genre-box':
          working_model = True

    # # update data
    # if working_model is True:
    #   self.refresh_table()
    # else:
    #   self.no_artists.visible = True
    #   self.data_grid.visible = False

