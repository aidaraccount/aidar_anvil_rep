from ._anvil_designer import SelectionTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from ...Main_In import Main_In
from ...nav import click_link, click_button, click_box, logout, login_check, load_var, save_var


class SelectionTemplate(SelectionTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global model_id
    model_id = anvil.server.call('get_model_id',  user["user_id"])
    wl_id_view = load_var("watchlist_id")
    self.wl_id_view = wl_id_view

    if len(self.item['Name']) > 12:
      self.link_selection.text = self.item['Name'][0:12] + '..'
    else:
      self.link_selection.text = self.item['Name']
    
    
  def link_selection_click(self, **event_args):
    # load the data of the newly selected artist
    cur_ai_artist_id = self.link_selection.url
    self.parent.parent.parent.parent.update_cur_ai_artist_id(cur_ai_artist_id)
    self.parent.parent.parent.parent.get_watchlist_details(cur_ai_artist_id)
    self.parent.parent.parent.parent.get_watchlist_notes(cur_ai_artist_id)

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
    details = json.loads(anvil.server.call('get_watchlist_details', self.wl_id_view, cur_ai_artist_id))
    anvil.server.call('update_watchlist_lead',
                      self.wl_id_view,
                      cur_ai_artist_id,
                      watchlist,
                      details[0]["Status"],
                      notification
                      )
    self.parent.parent.parent.parent.parent.parent.update_no_notifications()
