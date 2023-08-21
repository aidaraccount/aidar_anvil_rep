from ._anvil_designer import C_RatingTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

class C_Rating(C_RatingTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    global cur_model_id
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])

    # Ratings Table
    self.data_ratings_data.items = json.loads(anvil.server.call('get_ratings', cur_model_id))

