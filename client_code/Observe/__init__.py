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

    # model_selection
    models = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))
    print(models)
    # if self.item["genres_list"] is None:
    #   pass
    # else:
    #   genres_list = self.item["genres_list"]
    #   for g in (range(0, min(len(genres_list), 4))):
    #     genre_label = Label(text=genres_list[g])
    #     genre_label.role = 'genre-box'
    #     self.flow_panel_genre_tile.add_component(genre_label)
    #   if len(genres_list) > 4:
    #     genre_label = Label(text='...')
    #     genre_label.role = 'genre-box'
    #     self.flow_panel_genre_tile.add_component(genre_label)


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
          role='genre-box'
          )
      model_link.set_event_handler('click', self.activate_model())
      self.flow_panel_models.add_component(model_link)
  

    
    # get data
    observed = json.loads(anvil.server.call('get_observed', model_id, False))
    # add running Number
    for i, artist in enumerate(observed, start=1):
      artist['Number'] = i

    # table
    self.repeating_panel_table.items = observed


  # activate model
  def activate_model(self):
    print('activated')