from ._anvil_designer import ItemTemplate2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from anvil_extras import routing
from ...nav import click_link, click_button, logout, login_check, load_var, save_var


class ItemTemplate2(ItemTemplate2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
  
    global user
    user = anvil.users.get_user()
    global model_id
    model_id = anvil.server.call('get_model_id',  user["user_id"])
    
    # Any code you write here will run before the form opens.
    # cut the name
    if len(self.item['Name']) > 13:
      self.link_name.text = self.item['Name'][0:13] + '..'
    else:
      self.link_name.text = self.item['Name']
    
    # hide left/right errors for first and last components    
    if self.item["Status"] in ['Reconnect later', 'Not interested', None]: #BACKLOG
      self.link_left.visible = False
    elif self.item["Status"] in ['Success']: #NEGOTIATION
      self.link_right.visible = False

  
  def link_1_click(self, **event_args):
    click_link(self.link_1, f'watchlist_details?artist_id={self.item["ArtistID"]}', event_args)

  def link_left_click(self, **event_args):
    if self.item["Status"] in ['Action required', 'Requires revision', 'Waiting for decision']: #EVALUATION
      status_left_new = 'Reconnect later'
    elif self.item["Status"] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']: #CONTACTING
      status_left_new = 'Action required'
    elif self.item["Status"] in ['In negotiations', 'Contract in progress']: #NEGOTIATION
      status_left_new = 'Build connection'
    elif self.item["Status"] in ['Success']: #SUCCESS
      status_left_new = 'In negotiations'
      
    anvil.server.call('update_watchlist_lead',
                      user["user_id"],
                      None,
                      self.item["ArtistID"],
                      True,
                      status_left_new,
                      self.item["Notification"]
                      )
    click_link(self.link_left, 'watchlist_funnel', event_args)
    
  def link_right_click(self, **event_args):
    if self.item["Status"] in ['Reconnect later', 'Not interested', None]: #BACKLOG
      status_right_new = 'Action required'
    elif self.item["Status"] in ['Action required', 'Requires revision', 'Waiting for decision']: #EVALUATION
      status_right_new = 'Build connection'
    elif self.item["Status"] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']: #CONTACTING
      status_right_new = 'In negotiations'
    elif self.item["Status"] in ['In negotiations', 'Contract in progress']: #NEGOTIATION
      status_right_new = 'Success'
    
    anvil.server.call('update_watchlist_lead',
                      user["user_id"],
                      None,
                      self.item["ArtistID"],
                      True,
                      status_right_new,
                      self.item["Notification"]
                      )
    click_link(self.link_right, 'watchlist_funnel', event_args)
