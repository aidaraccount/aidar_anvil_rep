from ._anvil_designer import SelectionTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from ...Main_In import Main_In


class SelectionTemplate(SelectionTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global cur_model_id
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    
  def link_selection_click(self, **event_args):
    # load the data of the newly selected artist
    cur_ai_artist_id = self.link_selection.url
    self.parent.parent.parent.parent.update_cur_ai_artist_id(cur_ai_artist_id)
    self.parent.parent.parent.parent.get_watchlist_details(cur_model_id, cur_ai_artist_id)
    self.parent.parent.parent.parent.get_watchlist_notes(cur_model_id, cur_ai_artist_id)

    # change the border color to the new selected artist
    components = self.parent.get_components()
    for comp in components:
      comp.image_1.border = 'none'
    self.image_1.border = '1px solid #fd652d' # orange

    # update notification status
    self.radio_button_notification.selected = False
    self.update_watchlist_notification(True, False)
  
  def link_notification_click(self, **event_args):
    if self.radio_button_notification.selected == True:
      self.radio_button_notification.selected = False
      self.update_watchlist_notification(True, False)
    else:
      self.radio_button_notification.selected = True
      self.update_watchlist_notification(True, True)

  def set_notification_true(self, **event_args):
    self.radio_button_notification.selected = True
  
  def update_watchlist_notification(self, watchlist, notification, **event_args):
    cur_ai_artist_id = self.link_selection.url
    details = json.loads(anvil.server.call('get_watchlist_details', cur_model_id, cur_ai_artist_id))
    anvil.server.call('update_watchlist_notification',
                      cur_model_id,
                      cur_ai_artist_id,
                      watchlist,
                      notification
                      )
    self.parent.parent.parent.parent.parent.parent.update_no_notifications()
