from ._anvil_designer import C_RatingTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class C_Rating(C_RatingTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    global cur_model_id
    cur_model_id = anvil.server.call('GetModelID',  user["user_id"])
    