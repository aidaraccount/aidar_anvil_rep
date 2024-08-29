from ._anvil_designer import Watchlist_DetailsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var


@routing.route('watchlist_details', url_keys=['artist_id'], title='Watchlist')
class Watchlist_Details(Watchlist_DetailsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    model_id = load_var("model_id")
    print(f"Watchlist_Details model_id: {model_id}")
    temp_artist_id = self.url_dict['artist_id']
    print(f"Watchlist_Details temp_artist_id: {temp_artist_id}")
    
    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    self.model_id = model_id

    self.get_watchlist_selection(temp_artist_id = temp_artist_id)

  def drop_down_selection_change(self, **event_args):
    self.get_watchlist_selection(temp_artist_id=None)
  
  # get information for selection bar on the left
  def get_watchlist_selection(self, temp_artist_id, **event_args):
    # 1. get selection data
    watchlist_selection = json.loads(anvil.server.call('get_watchlist_selection', user["user_id"]))

    # 2. sort it according to the drop_down_selection
    # transform None to 'None'
    for item in watchlist_selection:
        for key, value in item.items():
            if value is None:
                if key == "Notification": item[key] = False
                if key == "Status": item[key] = 'Action required'
                if key == "Priority": item[key] = 'mid'

    # sort selection artists by drop_down_selection
    if self.drop_down_selection.selected_value == 'Notification':
      watchlist_selection = sorted(watchlist_selection, key=lambda x: x.get('Notification', float('inf')), reverse=True)
    if self.drop_down_selection.selected_value == 'Status':
      priority_order = {'Action required': 1,
                        'Requires revision': 2,
                        'Build connection': 3,
                        'Awaiting response': 4,
                        'Waiting for decision': 5,
                        'Exploring opportunities': 6,
                        'Positive response': 7,
                        'In negotiations': 8,
                        'Contract in progress': 9,
                        'Reconnect later': 10,
                        'Not interested': 11,
                        'Success': 12}
      watchlist_selection = sorted(watchlist_selection, key=lambda x: priority_order.get(x['Status'], float('inf')))
    if self.drop_down_selection.selected_value == 'Priority':
      priority_order = {'very high': 1, 'high': 2, 'mid': 3, 'low': 4, 'very low': 5}
      watchlist_selection = sorted(watchlist_selection, key=lambda x: priority_order.get(x['Priority'], float('inf')))

    # 3. present the data if present, else show dummy text
    if len(watchlist_selection) > 0:

      # hide dummy text
      self.label_1.visible = False
      self.label_2.visible = False
      self.spacer_1.visible = False

      # show sorted data in repeating_panel_selection and highlight the first selected artist
      self.repeating_panel_selection.items = watchlist_selection
      
      # a) show details and notes for 1st element of selection list
      if temp_artist_id == 'None':
        cur_ai_artist_id = watchlist_selection[0]['ArtistID']
        self.repeating_panel_selection.get_components()[0].image_1.border = '1px solid #fd652d' # orange

      # b) show details and notes for x-st element of selection list
      else:
        cur_ai_artist_id = temp_artist_id
        x = 0
        for a in range(0, len(watchlist_selection)):
          if watchlist_selection[a]['ArtistID'] == cur_ai_artist_id:
            x = a
        self.repeating_panel_selection.get_components()[x].image_1.border = '1px solid #fd652d' # orange
        
      # get watchlist details and notes
      self.update_cur_ai_artist_id(cur_ai_artist_id)
      self.get_watchlist_details(self.model_id, cur_ai_artist_id)
      self.get_watchlist_notes(self.model_id, cur_ai_artist_id)

      # get notifications
      components = self.repeating_panel_selection.get_components()
      for c in range(0, len(components)):
        if watchlist_selection[c]["Notification"] is True:
          components[c].set_notification_true()
    
    else:
      # hide all watchlist content and only show dummy text
      self.column_panel_5.visible = False
      self.column_panel_4.visible = False
      self.label_description.visible = False

  def update_cur_ai_artist_id(self, new_value):
    global cur_ai_artist_id
    cur_ai_artist_id = new_value
  
  def get_watchlist_details (self, model_id, cur_ai_artist_id, **event_args):
    cur_ai_artist_id = cur_ai_artist_id
    details = json.loads(anvil.server.call('get_watchlist_details', model_id, cur_ai_artist_id))
    
    print(details[1])
    # Image & Name
    self.image_detail.source = details[0]["ArtistPictureURL"]
    self.label_name.text = details[0]["Name"]    

    # Social Media Section
    platform_dict = {
      "Spotify": "fa:spotify",
      "Amazon": "fa:amazon",
      "Soundcloud": "fa:soundcloud",
      "Apple Music": "fa:apple",
      "Facebook": "fa:facebook",
      "Instagram": "fa:instagram",
      "Twitter": "fab:x-twitter",
      "YouTube": "fa:youtube",
      "Deezer": "fab:deezer",
      "TikTok": "fab:tiktok"
    }
      
    if details[1]["ArtistID"] == '':
      self.social_media_link.visible = False
    else:
      social_media_list = details[1]["Platform"]
      social_media_list_url = details[1]["PlatformURL"]
      print(social_media_list)
      print(social_media_list['0'])
      for i in range(0, len(social_media_list)):
        found = False

        if social_media_list[str(i)] in platform_dict:  
          found = True
          social_media_link = Link(icon=platform_dict[social_media_list[str(i)]])
          social_media_link.role = "music-icons-tile"
          
        if found is True:
          # social_media_link.role = 'genre-box'
          social_media_link.url = social_media_list_url[str(i)]
          self.flow_panel_social_media_tile.add_component(social_media_link)

    
    if details[0]["Description"] is None:
      self.text_description.text = '-'
      self.text_area_description.text = None
    else:
      self.text_description.text = details[0]["Description"]
      self.text_area_description.text = details[0]["Description"]
    
    if details[0]["ContactName"] is None:
      self.label_contact.text = '-'
      self.text_box_contact.text = None
    else:
      self.label_contact.text = details[0]["ContactName"]
      self.text_box_contact.text = details[0]["ContactName"]
    if details[0]["Mail"] is None:
      self.label_mail.text = '-'
      self.text_box_mail.text = None
    else:
      self.label_mail.text = details[0]["Mail"]
      self.text_box_mail.text = details[0]["Mail"]
    if details[0]["Phone"] is None:
      self.label_phone.text = '-'
      self.text_box_phone.text = None
    else:
      self.label_phone.text = details[0]["Phone"]
      self.text_box_phone.text = details[0]["Phone"]

    # tags
    if details[0]["Status"] is None: 
      self.drop_down_status.selected_value = 'Action required'
    else: 
      self.drop_down_status.selected_value = details[0]["Status"]
    if details[0]["Priority"] is None: 
      self.drop_down_priority.selected_value = 'mid'
    else: 
      self.drop_down_priority.selected_value = details[0]["Priority"]
    if details[0]["Reminder"] is None: 
      self.date_picker_reminder.date = ''
    else: 
      self.date_picker_reminder.date = details[0]["Reminder"]

    
    
  def get_watchlist_notes (self, model_id, cur_ai_artist_id, **event_args):
    cur_ai_artist_id = cur_ai_artist_id
    self.repeating_panel_detail.items = json.loads(anvil.server.call('get_watchlist_notes', user["user_id"], cur_ai_artist_id))
  
  def button_note_click(self, **event_args):
    anvil.server.call('add_note', user["user_id"], self.model_id, cur_ai_artist_id, "", "", self.text_area_note.text)
    self.text_area_note.text = ""
    self.get_watchlist_notes(self.model_id, cur_ai_artist_id)

  def button_edit_click(self, **event_args):
    details = json.loads(anvil.server.call('get_watchlist_details', self.model_id, cur_ai_artist_id))
    
    if self.button_edit.icon == 'fa:edit':
      self.button_edit.icon = 'fa:save'

      self.text_area_description.visible = True
      self.text_area_description.text = details[0]["Description"]
      self.text_description.visible = False
      
      self.text_box_contact.visible = True
      self.text_box_contact.text = details[0]["ContactName"]
      self.label_contact.visible = False
      
      self.text_box_mail.visible = True
      self.text_box_mail.text = details[0]["Mail"]
      self.label_mail.visible = False
      
      self.text_box_phone.visible = True
      self.text_box_phone.text = details[0]["Phone"]
      self.label_phone.visible = False
    
    else:
      self.button_edit.icon = 'fa:edit'

      self.text_area_description.visible = False
      self.text_description.visible = True
      
      self.text_box_contact.visible = False
      self.label_contact.visible = True
      
      self.text_box_mail.visible = False
      self.label_mail.visible = True
      
      self.text_box_phone.visible = False
      self.label_phone.visible = True

      
      # save text boxes
      self.update_watchlist_details()
  
  def update_watchlist_details(self, **event_args):
    details = json.loads(anvil.server.call('get_watchlist_details', self.model_id, cur_ai_artist_id))
    anvil.server.call('update_watchlist_details',
                      self.model_id,
                      cur_ai_artist_id,
                      True,
                      self.drop_down_status.selected_value,
                      self.drop_down_priority.selected_value,
                      self.date_picker_reminder.date,
                      details[0]["Notification"],
                      self.text_box_contact.text,
                      self.text_box_mail.text,
                      self.text_box_phone.text,
                      self.text_area_description.text
                      )
    
    self.get_watchlist_details(self.model_id, cur_ai_artist_id)
  
  def button_investigate_click(self, **event_args):
    click_button(f'artists?artist_id={cur_ai_artist_id}', event_args)

  def button_delete_click(self, **event_args):
    c = confirm("Do you wish to delete this artist from your watchlist?")
    if c is True:
      anvil.server.call('update_watchlist_lead', self.model_id, cur_ai_artist_id, False, None, False)
      self.get_watchlist_selection(temp_artist_id = None)
      self.parent.parent.update_no_notifications()
