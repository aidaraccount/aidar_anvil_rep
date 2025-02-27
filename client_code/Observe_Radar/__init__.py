from ._anvil_designer import Observe_RadarTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import time
from datetime import date, datetime

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var, save_var

from ..C_NotificationSettings import C_NotificationSettings

from anvil_labs.non_blocking import call_async


@routing.route("radar", url_keys=['notification_id'], title="Observe - Artist Radar")
class Observe_Radar(Observe_RadarTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # print(f"{datetime.now()}: Observe 0", flush=True)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    if user is None:
      self.visible = False
      
    elif user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      routing.set_url_hash('no_subs', load_from_cache=False)
      get_open_form().SearchBar.visible = False
      
    else:
      model_id = load_var("model_id")
      self.model_id = model_id
      print(f"Notifications model_id: {model_id}")

      self.no_trained_model.visible = False
      self.no_notifications.visible = False
      self.no_artists.visible = False
      
      url_notification_id = self.url_dict['notification_id']
      self.url_notification_id = url_notification_id
      
      # GENERAL  
      self.get_all_notifications(url_notification_id)

    
  # GET ALL NOTIFICATIONS
  def get_all_notifications(self, notification_id, **event_args):
    self.notifications = json.loads(anvil.server.call("get_notifications", user["user_id"], 'mail'))
    
    # clear all navigation components
    self.flow_panel.clear()
    
    # adding navigation components
    self.flow_panel.visible = True
    self.flow_panel_create.visible = True
    
    # adding navigation components
    for notification in self.notifications:
      notification_link = Link(
        text=notification["name"],
        role='section_buttons',
        tag=notification["notification_id"]
      )
      notification_link.set_event_handler('click', self.create_click_notification_handler(notification["notification_id"], notification_link))
      self.flow_panel.add_component(notification_link)

    # load and activate defined/first notification
    if len(self.notifications) > 0:
      self.no_notifications.visible = False
      self.no_trained_model.visible = False
  
      if notification_id is None or notification_id == 'None':
        notification_id = self.notifications[0]["notification_id"]
      else:
        notification_id = int(notification_id)
      
      self.activate_notification(notification_id)

    else:
      self.flow_panel.visible = False
      self.flow_panel_create.visible = False
      self.notification_settings.visible = False
      self.data_grid.visible = False
  
      models = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))    
      if not any(item.get('fully_trained', True) for item in models):
        # if no trained model
        self.no_trained_model.visible = True
        self.no_notifications.visible = False
        self.no_artists.visible = False
  
      else:
        # else, just missing notification      
        self.no_trained_model.visible = False
        self.no_notifications.visible = True
        self.no_artists.visible = False
    

  # ACTIVATE NOTIFICATION
  def activate_notification(self, notification_id):
    for component in self.flow_panel.get_components():
      if isinstance(component, Link):          
        if int(component.tag) == notification_id:
          component.role = 'section_buttons_focused'
          self.get_notification_settings(notification_id)
        else:
          component.role = 'section_buttons'

  # GET NOTIFICATION SETTINGS
  def get_notification_settings(self, notification_id, **event_args):
    items = [item for item in self.notifications if item["notification_id"] == notification_id]
    
    self.notification_settings.clear()
    self.notification_settings.add_component(C_NotificationSettings(items, notification_id))
    self.notification_settings.visible = True
    
    self.get_observed(notification_id)
    
  # GET PLAYLIST DETAILS
  def get_observed(self, notification_id):
    print('1. get_observed start')
    
    # get data
    notification = [item for item in self.notifications if item["notification_id"] == notification_id][0]

    print('2. get_observed hand over')
    """Calls the server asynchronously without blocking the UI."""
    async_call = call_async("anvil_get_observed", user["user_id"], notification, timeout = 600)
    async_call.on_result(self.get_observed_follow_up)
    
  def get_observed_follow_up(self, result):
    print('3. get_observed start follow up')
    """Handles successful server response."""
    observed, notification = result
    
    # add numbering & metric
    for i, artist in enumerate(observed, start=1):
      artist['Number'] = i
      artist['Metric'] = notification["metric"]
    
    # hand-over the data
    if len(observed) > 0:
      self.no_artists.visible = False
      self.repeating_panel_table.items = observed
      self.data_grid.visible = True
    else:
      self.data_grid.visible = False
      self.no_artists.visible = True
    
    # pushover
    anvil.server.call('sent_push_over',  'Observe_Radar', f'User {user["user_id"]}: using Artist Radar')
    print('4. get_observed end')
    
  # CREATE A NEW OBSERBATION
  def add_observation_click(self, **event_args):
    # get a trained model to activate it at the beginning
    models = json.loads(anvil.server.call("get_model_ids", user["user_id"]))

    model_id_pre_select = None
    for i in range(0, len(models)):
      if models[i]["is_last_used"] is True and models[i]["fully_trained"] is True:
        model_id_pre_select = models[i]["model_id"]

      else:
        for i in range(0, len(models)):
          if models[i]["fully_trained"] is True:
            model_id_pre_select = models[i]["model_id"]
            break

    if model_id_pre_select:
      model_ids = [model_id_pre_select]
    else:
      model_ids = []

    # save the initial notification
    notification_id = anvil.server.call(
      "create_notification",
      user_id=user["user_id"],
      type="mail",
      name="My Radar",
      active=True,
      freq_1="Daily",
      freq_2=7,
      freq_3=date.today().strftime("%Y-%m-%d"),
      metric="Top Fits",
      no_artists=5,
      repetition_1="Repeat suggestions",
      repetition_2=90,
      rated=False,
      watchlist=None,
      release_days=21,
      min_grow_fit=0.75,
      model_ids=model_ids,
      song_selection_1="Latest Releases",
      song_selection_2="2",
    )
    
    # update the notifications table
    click_link(self.create_observation, f'radar?notification_id={notification_id}', event_args)

  
  # BASE FUNCTION FOR LINK EVENTS
  def create_click_notification_handler(self, notification_id, notification_link):
    def handler(**event_args):
      click_link(notification_link, f'radar?notification_id={notification_id}', event_args)
    return handler
