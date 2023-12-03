from ._anvil_designer import C_EditRefArtistsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


class C_EditRefArtists(C_EditRefArtistsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global cur_model_id
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])

    references = json.loads(anvil.server.call('get_references', cur_model_id))
    self.repeating_panel_reference.items = references

    # exclude 2. and 3.
    #if references[len(references)-1][1]["ArtistID"] == None:
    # xy
    # xy
    # exclude 3.
    # elif references[len(references)-1][2]["ArtistID"] == None:
    # xy

    #components = self.repeating_panel_reference.get_components()
    #print(components[1])
    #print(self.repeating_panel_reference.item_template)
    #template = self.repeating_panel_reference.item_template
    
    #template.xy_panel_3.visible = False
    