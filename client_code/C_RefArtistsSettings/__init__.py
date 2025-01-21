from ._anvil_designer import C_RefArtistsSettingsTemplate
from ..C_RefPopupTable import C_RefPopupTable
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

import anvil.js.window
from ..nav import click_link, click_button, logout, save_var, load_var


class C_RefArtistsSettings(C_RefArtistsSettingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    self.model_id_view = load_var("model_id_view")
    print("C_RefArtistsSettings model_id_view:", self.model_id_view)

    self.get_references()
  
  def get_references(self, **event_args):
    references = json.loads(anvil.server.call('get_references', self.model_id_view))
    self.repeating_panel_reference.items = references
    
    if references != []:
      no_refs =  sum(1 for artist in references[0] if artist['ArtistID'] is not None)
    else:
      no_refs = 0
    self.no_refs.text = f"{no_refs} of 3+ references added"
  
  def text_box_search_pressed_enter(self, **event_args):
    ref_data = json.loads(anvil.server.call("search_artist", user["user_id"], self.text_box_search.text.strip()))
    print('ref_data:', ref_data)
    
    if not ref_data:
      alert(title="Artist not found or missing",
        content="If you can't find the artist you're looking for, just enter their Spotify ID in the overall top search bar, and we'll add them to our catalog.",
        buttons=[("OK", "OK")],
        role=["alert-notification","remove-focus"]
      )
            
    else:    
      alert(
        content=C_RefPopupTable(ref_data),
        large=True,
        buttons=[]
      )
      
      self.get_references()
  
      # SOURCE INDIVIDUAL CODE
      if anvil.js.window.location.hash.lstrip('#').split('?')[0] == 'model_setup':
        # Update Next-Button in RampUp
        artist_id = anvil.server.call('get_next_artist_id', self.model_id_view)
        if artist_id is not None:
          self.parent.parent.get_components()[-1].get_components()[1].role = ['call-to-action-button','header-6','opacity-100']
        else:
          self.parent.parent.get_components()[-1].get_components()[1].role = ['call-to-action-button', 'header-6', 'opacity-25']
          
      elif anvil.js.window.location.hash.lstrip('#').split('?')[0] == 'model_profile':
        pass

    # reset search field and button
    self.text_box_search.text = ''
    self.search_button.role = ['call-to-action-button-disabled', 'header-6']

  def text_box_search_change(self, **event_args):
    if self.text_box_search.text != '':
      self.search_button.role = ['call-to-action-button', 'header-6']
    else:
      self.search_button.role = ['call-to-action-button-disabled', 'header-6']
