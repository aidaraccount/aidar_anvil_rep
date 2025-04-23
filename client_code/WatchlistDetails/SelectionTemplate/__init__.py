from ._anvil_designer import SelectionTemplateTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from ...MainIn import MainIn
from ...nav import click_link, click_button, click_box, logout, login_check, load_var, save_var


class SelectionTemplate(SelectionTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

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
    self.button_notification.icon = 'fa:circle-o'
    self.update_watchlist_notification(False)
  
  def button_notification_click(self, **event_args):
    print('clicking radio button')
    if self.button_notification.icon == 'fa:circle-o':
      self.button_notification.icon = 'fa:circle'
      self.update_watchlist_notification(True)
    else:
      self.button_notification.icon = 'fa:circle-o'
      self.update_watchlist_notification(False)

  def set_notification_true(self, **event_args):
    self.button_notification.icon = 'fa:circle'
  
  def update_watchlist_notification(self, notification, **event_args):
    cur_ai_artist_id = self.link_selection.url
    
    anvil.server.call('update_watchlist_details',
      user_id=user["user_id"],
      ai_artist_id=cur_ai_artist_id,
      notification=notification
    )
    get_open_form().update_no_notifications()

