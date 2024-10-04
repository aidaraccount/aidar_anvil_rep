from ._anvil_designer import ObserveTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var


@routing.route("observe", title="Observe")
class Observe(ObserveTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)


    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    model_id = load_var("model_id")
    self.model_id = model_id
    print(f"Observe model_id: {model_id}")

    # GENERAL
    # model_selection
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
      
    # table
    if working_model is True:
      self.refresh_table()
    else:
      self.no_trained_model.visible = True
      self.flow_panel_ratings.visible = False
      self.flow_panel_models.visible = False
      self.data_grid.visible = False
    

  # refresh the table
  def refresh_table(self):    
    # get list of activated models
    model_ids = []
    for component in self.flow_panel_models.get_components():
      if isinstance(component, Link):
        if component.role == 'genre-box':
          model_ids.append(component.tag)

    # get un/-rated status
    if self.link_rated.role == 'genre-box-deselect':
      rated = False
    elif self.link_unrated.role == 'genre-box-deselect':
      rated = True
    else:
      rated = None

    if len(model_ids) > 0:
      # get data
      observed = json.loads(anvil.server.call('get_observed', model_ids, rated))
      
      # add numbering
      for i, artist in enumerate(observed, start=1):
        artist['Number'] = i
  
      # hand-over the data
      self.repeating_panel_table.items = observed
      
      self.no_trained_model.visible = False
      self.data_grid.visible = True
  
  # activate model
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
      self.data_grid.visible = False

  def link_unrated_click(self, **event_args):
    if self.link_unrated.role == 'genre-box':
      self.link_unrated.role = 'genre-box-deselect'
      self.link_rated.role = 'genre-box'
    else:
      self.link_unrated.role = 'genre-box'
    self.refresh_table()

  def link_rated_click(self, **event_args):
    if self.link_rated.role == 'genre-box':
      self.link_rated.role = 'genre-box-deselect'
      self.link_unrated.role = 'genre-box'
    else:
      self.link_rated.role = 'genre-box'
    self.refresh_table()
      