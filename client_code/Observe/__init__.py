from ._anvil_designer import ObserveTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import datetime

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var


@routing.route("observe", title="Observe")
class Observe(ObserveTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # print(f"{datetime.now()}: Observe 0", flush=True)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    model_id = load_var("model_id")
    self.model_id = model_id
    print(f"Observe model_id: {model_id}")

    # GENERAL
    self.nav_top_fits.role = 'section_buttons_focused'
    self.flow_panel_growth.visible = False
    self.flow_panel_release.visible = False
    
    # model_selection
    # print(f"{datetime.now()}: Observe 1", flush=True)
    models = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))

    working_model = False
    is_last_used_is_not_trained = False
    for i in range(0, len(models)):
      if models[i]["is_last_used"] is True:        
        model_link = Link(
          text=models[i]["model_name"],
          tag=models[i]["model_id"],
          role='genre-box'
          )
        if models[i]["fully_trained"] is False:
          is_last_used_is_not_trained = True
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
      else:        
        working_model = True
        
      model_link.set_event_handler('click', self.create_activate_model_handler(models[i]["model_id"]))
      self.flow_panel_models.add_component(model_link)

    # if is_last_used is not fully trained, activate first trained:
    if is_last_used_is_not_trained is True:
      for component in self.flow_panel_models.get_components():
        if isinstance(component, Link):
          if component.role == 'genre-box-deselect':
            component.role = 'genre-box'
            break
      
    # print(f"{datetime.now()}: Observe 2", flush=True)
    # table
    if working_model is True:
      self.refresh_table()
    else:
      self.no_trained_model.visible = True
      self.no_artists.visible = False
      self.flow_panel_ratings.visible = False
      self.flow_panel_models.visible = False
      self.flow_panel_wl.visible = False
      self.flow_panel_sections.visible = False
      self.data_grid.visible = False
    
    # print(f"{datetime.now()}: Observe 3", flush=True)

  
  # GET TABLE DATA
  def refresh_table(self, **event_args):    
    # print(f"{datetime.now()}: Observe 2a", flush=True)
    # get list of activated models
    model_ids = []
    for component in self.flow_panel_models.get_components():
      if isinstance(component, Link):
        if component.role == 'genre-box':
          model_ids.append(component.tag)

    # get metric status
    if self.nav_top_fits.role == 'section_buttons_focused':
      metric = 'Top Fits'
      min_grow_fit = None
      release_days = None
    elif self.nav_grow_fits.role == 'section_buttons_focused':
      metric = 'Growing Fits'
      min_grow_fit = self.min_growth_pred.text/100
      release_days = None
    elif self.nav_release_fits.role == 'section_buttons_focused':
      metric = 'Releasing Fits'
      min_grow_fit = None
      release_days = self.max_release_days.text
    
    # get rated status
    if self.link_rated.text == 'rated':
      rated = True
    elif self.link_rated.text == 'unrated':
      rated = False
    else:
      rated = None

    # get watchlist status
    if self.link_watchlist.text == 'on watchlist':
      watchlist = True
    elif self.link_watchlist.text == 'not on watchlist':
      watchlist = False
    else:
      watchlist = None

    self.data_grid.visible = False

    if len(model_ids) > 0:    
      self.no_trained_model.visible = False
      
      # get data
      # print(f"{datetime.now()}: Observe 2b", flush=True)
      observed = json.loads(anvil.server.call('get_observed', 
                                              user["user_id"],
                                              model_ids,
                                              metric,
                                              rated,
                                              watchlist,
                                              min_grow_fit,
                                              release_days
                                             ))
      
      # add numbering & metric
      # print(f"{datetime.now()}: Observe 2c", flush=True)
      for i, artist in enumerate(observed, start=1):
        artist['Number'] = i
        artist['Metric'] = metric
      
      # hand-over the data
      # print(f"{datetime.now()}: Observe 2d", flush=True)
      if len(observed) > 0:
        self.no_artists.visible = False
        self.repeating_panel_table.items = observed
        self.data_grid.visible = True
      else:
        self.data_grid.visible = False
        self.no_artists.visible = True
      
      # print(f"{datetime.now()}: Observe 2e", flush=True)

    else:
      self.data_grid.visible = False
      self.no_artists.visible = True
      # print(f"{datetime.now()}: Observe 2f", flush=True)
  
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

    # update data
    if working_model is True:
      self.refresh_table()
    else:
      self.no_artists.visible = True
      self.data_grid.visible = False

  # RATED BUTTON
  def link_rated_click(self, **event_args):
    if self.link_rated.text == 'rated':
      self.link_rated.text = 'unrated'
      self.link_rated.role = 'genre-box'
    elif self.link_rated.text == 'unrated':
      self.link_rated.text = 'all'
      self.link_rated.role = 'genre-box-deselect'
    elif self.link_rated.text == 'all':
      self.link_rated.text = 'rated'
      self.link_rated.role = 'genre-box'
    self.refresh_table()

  # WATCHLIST BUTTON
  def link_watchlist_click(self, **event_args):
    if self.link_watchlist.text == 'on watchlist':
      self.link_watchlist.text = 'not on watchlist'
      self.link_watchlist.role = 'genre-box'
    elif self.link_watchlist.text == 'not on watchlist':
      self.link_watchlist.text = 'all'
      self.link_watchlist.role = 'genre-box-deselect'
    elif self.link_watchlist.text == 'all':
      self.link_watchlist.text = 'on watchlist'
      self.link_watchlist.role = 'genre-box'      
    self.refresh_table()

  # NAVIGATION
  def nav_top_fits_click(self, **event_args):
    self.nav_top_fits.role = 'section_buttons_focused'
    self.nav_grow_fits.role = 'section_buttons'
    self.nav_release_fits.role = 'section_buttons'
    self.flow_panel_growth.visible = False
    self.flow_panel_release.visible = False
    self.refresh_table()

  def nav_grow_fits_click(self, **event_args):
    self.nav_top_fits.role = 'section_buttons'
    self.nav_grow_fits.role = 'section_buttons_focused'
    self.nav_release_fits.role = 'section_buttons'
    self.flow_panel_growth.visible = True
    self.flow_panel_release.visible = False
    self.refresh_table()

  def nav_release_fit_click(self, **event_args):
    self.nav_top_fits.role = 'section_buttons'
    self.nav_grow_fits.role = 'section_buttons'
    self.nav_release_fits.role = 'section_buttons_focused'
    self.flow_panel_growth.visible = False
    self.flow_panel_release.visible = True
    self.refresh_table()

  def notifications_click(self, **event_args):
    click_link(self.notification_link, 'notifications', event_args)
