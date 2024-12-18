from ._anvil_designer import Observe_RadarTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import date, datetime

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var, save_var

from ..C_Notification_Settings import C_Notification_Settings


@routing.route("radar", url_keys=['notification_id'], title="Observe - Artist Radar")
class Observe_Radar(Observe_RadarTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # print(f"{datetime.now()}: Observe 0", flush=True)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    if user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      routing.set_url_hash('no_subs', load_from_cache=False)
      get_open_form().SearchBar.visible = False
      
    else:      
      model_id = load_var("model_id")
      self.model_id = model_id
      print(f"Notifications model_id: {model_id}")
  
      url_notification_id = self.url_dict['notification_id']
      self.url_notification_id = url_notification_id
      
      save_var('toggle', 'up')
      
      # GENERAL
  
      self.get_all_notifications(url_notification_id)

    
  # GET ALL NOTIFICATIONS
  def get_all_notifications(self, notification_id, **event_args):
    self.notifications = json.loads(anvil.server.call("get_notifications", user["user_id"], 'mail'))
    print('get_all_notifications - all:', self.notifications)
    print('get_all_notifications:', notification_id)
    print('get_all_notifications - type:', type(notification_id))
    
    # clear all navigation components
    self.flow_panel.clear()
    
    # adding navigation components
    self.flow_panel.visible = True
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
  
      if notification_id is None or notification_id == 'None':
        notification_id = self.notifications[0]["notification_id"]
      else:
        notification_id = int(notification_id)
      
      self.activate_notification(notification_id)
      
    else:
      self.flow_panel.visible = False
      self.notification_settings.visible = False
      self.no_notifications.visible = True

  # ACTIVATE NOTIFICATION
  def activate_notification(self, notification_id):
    print('activate_notification:', notification_id)
    for component in self.flow_panel.get_components():
      if isinstance(component, Link):          
        if int(component.tag) == notification_id:
          component.role = 'section_buttons_focused'
          self.get_notification_settings(notification_id)
        else:
          component.role = 'section_buttons'

  # GET NOTIFICATION SETTINGS
  def get_notification_settings(self, notification_id, **event_args):
    print('get_notification_settings:', notification_id)
    items = [item for item in self.notifications if item["notification_id"] == notification_id]
    
    self.notification_settings.clear()
    self.notification_settings.add_component(C_Notification_Settings(items, notification_id))
    self.notification_settings.visible = True
    
    self.get_observed(notification_id)
    
  # GET PLAYLIST DETAILS
  def get_observed(self, notification_id, **event_args):
    print('get_observed:', notification_id)

    # get data
    notification = [item for item in self.notifications if item["notification_id"] == notification_id][0]
    
    observed = json.loads(anvil.server.call('get_observed', 
                                            user["user_id"],
                                            notification["model_ids"],
                                            notification["metric"],
                                            notification["rated"],
                                            notification["watchlist"],
                                            notification["min_grow_fit"],
                                            notification["release_days"]
                                            ))
    
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
      name="My Observation",
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
    print('add_observation_click:', notification_id)
    
    # update the notifications table
    save_var('toggle', 'down')
    click_link(self.create_observation, f'radar?notification_id={notification_id}', event_args)

  
  # BASE FUNCTION FOR LINK EVENTS
  def create_click_notification_handler(self, notification_id, notification_link):
    def handler(**event_args):
      click_link(notification_link, f'radar?notification_id={notification_id}', event_args)
    return handler
    





      
  #     # model_selection
  #     # print(f"{datetime.now()}: Observe 1", flush=True)
  #     models = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))
  
  #     working_model = False
  #     is_last_used_is_not_trained = False
  #     for i in range(0, len(models)):
  #       if models[i]["is_last_used"] is True:        
  #         model_link = Link(
  #           text=models[i]["model_name"],
  #           tag=models[i]["model_id"],
  #           role='genre-box'
  #           )
  #         if models[i]["fully_trained"] is False:
  #           is_last_used_is_not_trained = True
  #       else:
  #         model_link = Link(
  #           text=models[i]["model_name"],
  #           tag=models[i]["model_id"],
  #           role='genre-box-deselect'
  #           )
        
  #       if models[i]["fully_trained"] is False:        
  #         model_link = Link(
  #           text=models[i]["model_name"],
  #           tag=models[i]["model_id"],
  #           role='genre-box-deactive'
  #           )
  #       else:        
  #         working_model = True
          
  #       model_link.set_event_handler('click', self.create_activate_model_handler(models[i]["model_id"]))
  #       self.flow_panel_models.add_component(model_link)
  
  #     # if is_last_used is not fully trained, activate first trained:
  #     if is_last_used_is_not_trained is True:
  #       for component in self.flow_panel_models.get_components():
  #         if isinstance(component, Link):
  #           if component.role == 'genre-box-deselect':
  #             component.role = 'genre-box'
  #             break
        
  #     # print(f"{datetime.now()}: Observe 2", flush=True)
  #     # table
  #     if working_model is True:
  #       self.refresh_table()
  #     else:
  #       self.no_trained_model.visible = True
  #       self.notification_link.visible = False
  #       self.no_artists.visible = False
  #       self.flow_panel_ratings.visible = False
  #       self.flow_panel_models.visible = False
  #       self.flow_panel_wl.visible = False
  #       self.flow_panel_sections.visible = False
  #       self.data_grid.visible = False
      
  #     # print(f"{datetime.now()}: Observe 3", flush=True)

  
  # # GET TABLE DATA
  # def refresh_table(self, **event_args):    
  #   # print(f"{datetime.now()}: Observe 2a", flush=True)
  #   # get list of activated models
  #   model_ids = []
  #   for component in self.flow_panel_models.get_components():
  #     if isinstance(component, Link):
  #       if component.role == 'genre-box':
  #         model_ids.append(component.tag)

  #   # get metric status
  #   if self.nav_top_fits.role == 'section_buttons_focused':
  #     metric = 'Top Fits'
  #     min_grow_fit = None
  #     release_days = None
  #   elif self.nav_grow_fits.role == 'section_buttons_focused':
  #     metric = 'Growing Fits'
  #     min_grow_fit = self.min_growth_pred.text/100
  #     release_days = None
  #   elif self.nav_release_fits.role == 'section_buttons_focused':
  #     metric = 'Releasing Fits'
  #     min_grow_fit = None
  #     release_days = self.max_release_days.text
    
  #   # get rated status
  #   if self.link_rated.text == 'rated':
  #     rated = True
  #   elif self.link_rated.text == 'unrated':
  #     rated = False
  #   else:
  #     rated = None

  #   # get watchlist status
  #   if self.link_watchlist.text == 'on watchlist':
  #     watchlist = True
  #   elif self.link_watchlist.text == 'not on watchlist':
  #     watchlist = False
  #   else:
  #     watchlist = None

  #   self.data_grid.visible = False

  #   if len(model_ids) > 0:    
  #     self.no_trained_model.visible = False
  #     self.notification_link.visible = True
      
  #     # get data
  #     # print(f"{datetime.now()}: Observe 2b", flush=True)
  #     observed = json.loads(anvil.server.call('get_observed', 
  #                                             user["user_id"],
  #                                             model_ids,
  #                                             metric,
  #                                             rated,
  #                                             watchlist,
  #                                             min_grow_fit,
  #                                             release_days
  #                                            ))
      
  #     # add numbering & metric
  #     # print(f"{datetime.now()}: Observe 2c", flush=True)
  #     for i, artist in enumerate(observed, start=1):
  #       artist['Number'] = i
  #       artist['Metric'] = metric
      
  #     # hand-over the data
  #     # print(f"{datetime.now()}: Observe 2d", flush=True)
  #     if len(observed) > 0:
  #       self.no_artists.visible = False
  #       self.repeating_panel_table.items = observed
  #       self.data_grid.visible = True
  #     else:
  #       self.data_grid.visible = False
  #       self.no_artists.visible = True
      
  #     # print(f"{datetime.now()}: Observe 2e", flush=True)

  #   else:
  #     self.data_grid.visible = False
  #     self.no_artists.visible = True
  #     # print(f"{datetime.now()}: Observe 2f", flush=True)
  
  # # MODEL BUTTONS
  # def create_activate_model_handler(self, model_id):
  #   def handler(**event_args):
  #     self.activate_model(model_id)
  #   return handler
    
  # # change active status
  # def activate_model(self, model_id):
  #   working_model = False
  #   for component in self.flow_panel_models.get_components():
  #     if isinstance(component, Link):
        
  #       # change activation
  #       if int(component.tag) == model_id:
  #         if component.role == 'genre-box-deactive':
  #           Notification("",
  #             title="Model not fully trained yet - you need at least 50 ratings!",
  #             style="info").show()
  #         else:
  #           if component.role == 'genre-box':
  #             component.role = 'genre-box-deselect'
  #           else:
  #             component.role = 'genre-box'
  #       else:
  #         pass
          
  #       # check for active model
  #       if component.role == 'genre-box':
  #         working_model = True

  #   # update data
  #   if working_model is True:
  #     self.refresh_table()
  #   else:
  #     self.no_artists.visible = True
  #     self.data_grid.visible = False

  # # RATED BUTTON
  # def link_rated_click(self, **event_args):
  #   if self.link_rated.text == 'rated':
  #     self.link_rated.text = 'unrated'
  #     self.link_rated.role = 'genre-box'
  #   elif self.link_rated.text == 'unrated':
  #     self.link_rated.text = 'all'
  #     self.link_rated.role = 'genre-box-deselect'
  #   elif self.link_rated.text == 'all':
  #     self.link_rated.text = 'rated'
  #     self.link_rated.role = 'genre-box'
  #   self.refresh_table()

  # # WATCHLIST BUTTON
  # def link_watchlist_click(self, **event_args):
  #   if self.link_watchlist.text == 'on watchlist':
  #     self.link_watchlist.text = 'not on watchlist'
  #     self.link_watchlist.role = 'genre-box'
  #   elif self.link_watchlist.text == 'not on watchlist':
  #     self.link_watchlist.text = 'all'
  #     self.link_watchlist.role = 'genre-box-deselect'
  #   elif self.link_watchlist.text == 'all':
  #     self.link_watchlist.text = 'on watchlist'
  #     self.link_watchlist.role = 'genre-box'      
  #   self.refresh_table()

  # # NAVIGATION
  # def nav_top_fits_click(self, **event_args):
  #   self.nav_top_fits.role = 'section_buttons_focused'
  #   self.nav_grow_fits.role = 'section_buttons'
  #   self.nav_release_fits.role = 'section_buttons'
  #   self.flow_panel_growth.visible = False
  #   self.flow_panel_release.visible = False
  #   self.refresh_table()

  # def nav_grow_fits_click(self, **event_args):
  #   self.nav_top_fits.role = 'section_buttons'
  #   self.nav_grow_fits.role = 'section_buttons_focused'
  #   self.nav_release_fits.role = 'section_buttons'
  #   self.flow_panel_growth.visible = True
  #   self.flow_panel_release.visible = False
  #   self.refresh_table()

  # def nav_release_fit_click(self, **event_args):
  #   self.nav_top_fits.role = 'section_buttons'
  #   self.nav_grow_fits.role = 'section_buttons'
  #   self.nav_release_fits.role = 'section_buttons_focused'
  #   self.flow_panel_growth.visible = False
  #   self.flow_panel_release.visible = True
  #   self.refresh_table()

  # def notifications_click(self, **event_args):
  #   click_link(self.notification_link, 'notifications', event_args)
