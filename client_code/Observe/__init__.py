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
    print(models)
    for i in range(0, len(models)):
      if models[i]["is_last_used"] is True:        
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
      if models[i]["ramp_up"] is True:        
        model_link = Link(
          text=models[i]["model_name"],
          tag=models[i]["model_id"],
          role='genre-box-deactive'
          )
      model_link.set_event_handler('click', self.create_activate_model_handler(models[i]["model_id"]))
      self.flow_panel_models.add_component(model_link)
    
    # table
    self.refresh_table()
    

  # refresh the table
  def refresh_table(self):
    # get list of activated models
    model_ids = []
    for component in self.flow_panel_models.get_components():
      print('component.tag', component.tag)
      if isinstance(component, Link):
        if component.role == 'genre-box':
          model_ids.append(component.tag)
    print(model_ids)

    # get un/-rated status
    if self.link_rated.role == 'genre-box-deselect':
      rated = False
    elif self.link_unrated.role == 'genre-box-deselect':
      rated = True
    else:
      rated = None
    
    # get data
    observed = json.loads(anvil.server.call('get_observed', model_ids[0], rated))
    
    # add numbering
    for i, artist in enumerate(observed, start=1):
      artist['Number'] = i
    # print(observed)

    # hand-over the data
    self.repeating_panel_table.items = observed

  # activate model
  def create_activate_model_handler(self, model_id):
    def handler(**event_args):
      self.activate_model(model_id)
    return handler
    
  # change active status
  def activate_model(self, model_id):
    print('activate_model: ', model_id)
    for component in self.flow_panel_models.get_components():
      print('component.tag', component.tag)
      if isinstance(component, Link):
        if int(component.tag) == model_id:
          if component.role == 'genre-box-deactive':
            Notification("",
              title="Model not fully trained yet!",
              style="info").show()
          else:
            if component.role == 'genre-box':
              component.role = 'genre-box-deselect'
            else:
              component.role = 'genre-box'
            print('REFRESH TABLE!')
            self.refresh_table()
        else:
          pass

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
      