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
    
    # model_ids = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))
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
      model_link.set_event_handler('click', self.create_activate_model_handler(models[i]["model_id"]))
      self.flow_panel_models.add_component(model_link)
    
    # table
    self.refresh_table(model_id)
    # self.activate_model(None)

  # refresh the table
  def refresh_table(self, model_id):
    observed = json.loads(anvil.server.call('get_observed', model_id, False))
    for i, artist in enumerate(observed, start=1):
      artist['Number'] = i

    self.repeating_panel_table.items = observed

  # activate model
  def create_activate_model_handler(self, model_id):
    def handler(**event_args):
      self.activate_model(model_id)
    return handler
    
  def activate_model(self, model_id):
    print(model_id)
    for component in self.flow_panel_models.get_components():
      if isinstance(component, Link):
        if int(component.tag) == model_id:
          if component.role == 'genre-box':
            component.role = 'genre-box-deselect'
          else:
            component.role = 'genre-box'
          self.refresh_table(model_id)
        else:
          pass
