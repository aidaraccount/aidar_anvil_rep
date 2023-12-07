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
    cur_ai_artist_id = self.link_selection.url
    self.parent.parent.parent.parent.update_cur_ai_artist_id(self.link_selection.url)
    self.parent.parent.parent.parent.refresh_watchlist_details(cur_model_id, cur_ai_artist_id)
    self.parent.parent.parent.parent.refresh_watchlist_notes(cur_model_id, cur_ai_artist_id)
    
    components = self.parent.get_components()
    for comp in components:
      comp.image_1.border = 'none'
    self.image_1.border = '1px solid #fd652d' # orange

    self.radio_button_notification.selected = False
    self.update_watchlist_details_notification_false()
  
  def link_notification_click(self, **event_args):
    if self.radio_button_notification.selected == True:
      self.radio_button_notification.selected = False
      self.update_watchlist_details_notification_false()
    else:
      self.radio_button_notification.selected = True
      self.update_watchlist_details_notification_true()

  def set_notification_true(self, **event_args):
    self.radio_button_notification.selected = True
  
  # those two functions are doubles as I was not able to transfer the notification bool to C_Wachtlist_Details
  def update_watchlist_details_notification_true(self, **event_args):
    cur_ai_artist_id = self.link_selection.url
    details = json.loads(anvil.server.call('get_watchlist_details', cur_model_id, cur_ai_artist_id))
    anvil.server.call('update_watchlist_details',
                      details[0]["LeadID"],
                      cur_model_id,
                      cur_ai_artist_id,
                      self.parent.parent.parent.parent.drop_down_status.selected_value,
                      self.parent.parent.parent.parent.drop_down_priority.selected_value,
                      self.parent.parent.parent.parent.date_picker_reminder.date,
                      True,
                      self.parent.parent.parent.parent.text_box_spotify.text,
                      self.parent.parent.parent.parent.text_box_insta.text,
                      self.parent.parent.parent.parent.text_box_mail.text,
                      self.parent.parent.parent.parent.text_box_phone.text
                      )

    self.parent.parent.parent.parent.parent.parent.update_no_notifications()

  
  def update_watchlist_details_notification_false(self, **event_args):
    cur_ai_artist_id = self.link_selection.url
    details = json.loads(anvil.server.call('get_watchlist_details', cur_model_id, cur_ai_artist_id))
    anvil.server.call('update_watchlist_details',
                      details[0]["LeadID"],
                      cur_model_id,
                      cur_ai_artist_id,
                      self.parent.parent.parent.parent.drop_down_status.selected_value,
                      self.parent.parent.parent.parent.drop_down_priority.selected_value,
                      self.parent.parent.parent.parent.date_picker_reminder.date,
                      False,
                      self.parent.parent.parent.parent.text_box_spotify.text,
                      self.parent.parent.parent.parent.text_box_insta.text,
                      self.parent.parent.parent.parent.text_box_mail.text,
                      self.parent.parent.parent.parent.text_box_phone.text
                      )
    
    self.parent.parent.parent.parent.parent.parent.update_no_notifications()
    