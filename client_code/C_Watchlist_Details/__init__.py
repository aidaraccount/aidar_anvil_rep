from ._anvil_designer import C_Watchlist_DetailsTemplate
from ._anvil_designer import C_Watchlist_DetailsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


class C_Watchlist_Details(C_Watchlist_DetailsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global cur_model_id
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])

    self.get_watchlist_selection()

  
  # get information for selection bar on the left
  def get_watchlist_selection(self, **event_args):
    # 1. get selection data
    watchlist_selection = json.loads(anvil.server.call('get_watchlist_selection', cur_model_id))

    # 2. sort it according to the drop_down_selection
    # transform None to 'None'
    for item in watchlist_selection:
        for key, value in item.items():
            if value is None:
                if key == "Notification": item[key] = False
                if key == "Status": item[key] = 'Action required'
                if key == "Priority": item[key] = 'mid'
    
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
                        'Not interested': 11}
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
      self.repeating_panel_selection.get_components()[0].image_1.border = '1px solid #fd652d' # orange

      # show details and notes for first element of selection list
      #global cur_ai_artist_id
      cur_ai_artist_id = watchlist_selection[0]['ArtistID']
      self.update_cur_ai_artist_id(cur_ai_artist_id)
      print(f"get_watchlist_selection: {cur_ai_artist_id}")
      self.get_watchlist_details(cur_model_id, cur_ai_artist_id)
      self.get_watchlist_notes(cur_model_id, cur_ai_artist_id)

      # get notifications
      components = self.repeating_panel_selection.get_components()
      for c in range(0, len(components)):
        if watchlist_selection[c]["Notification"] == True:
          components[c].set_notification_true()
    
    else:
      # hide all watchlist content and only show dummy text
      self.column_panel_5.visible = False
      self.column_panel_4.visible = False
      self.label_description.visible = False

  def update_cur_ai_artist_id(self, new_value):
    global cur_ai_artist_id
    cur_ai_artist_id = new_value
    print(f"update_cur_ai_artist_id: {cur_ai_artist_id}")
  
  def get_watchlist_details (self, cur_model_id, cur_ai_artist_id, **event_args):
    #global cur_ai_artist_id
    cur_ai_artist_id = cur_ai_artist_id
    print(f"get_watchlist_details: {cur_ai_artist_id}")
    details = json.loads(anvil.server.call('get_watchlist_details', cur_model_id, cur_ai_artist_id))
    print(f"get_watchlist_details - details: {details}")

    # Image & Name
    self.image_detail.source = details[0]["ArtistPictureURL"]
    self.label_name.text = details[0]["Name"]    

    # Links & Contact Information
    if details[0]["SpotifyLink"] is None:
      self.link_spotify.text = 'Profile'
      self.link_spotify.url = details[0]["ArtistURL"]
      self.text_box_spotify.text = details[0]["ArtistURL"]
    else:
      self.link_spotify.text = 'Profile'
      self.link_spotify.url = details[0]["SpotifyLink"]
      self.text_box_spotify.text = details[0]["SpotifyLink"]
    
    if details[0]["InstaLink"] is None:
      self.link_insta.text = '-'
      self.text_box_insta.text = None
    else:
      self.link_insta.text = details[0]["InstaLink"]
      self.text_box_insta.text = details[0]["InstaLink"]
      
    if details[0]["ContactName"] is None:
      self.link_name.text = '-'
      self.text_box_name.text = None
    else:
      self.link_name.text = details[0]["ContactName"]
      self.text_box_name.text = details[0]["ContactName"]
    if details[0]["Mail"] is None:
      self.link_mail.text = '-'
      self.text_box_mail.text = None
    else:
      self.link_mail.text = details[0]["Mail"]
      self.text_box_mail.text = details[0]["Mail"]
    if details[0]["Phone"] is None:
      self.link_phone.text = '-'
      self.text_box_phone.text = None
    else:
      self.link_phone.text = details[0]["Phone"]
      self.text_box_phone.text = details[0]["Phone"]

    # tags
    if details[0]["Status"] is None: self.drop_down_status.selected_value = 'Action required'
    else: self.drop_down_status.selected_value = details[0]["Status"]
    if details[0]["Priority"] is None: self.drop_down_priority.selected_value = 'mid'
    else: self.drop_down_priority.selected_value = details[0]["Priority"]
    if details[0]["Reminder"] is None: self.date_picker_reminder.date = ''
    else: self.date_picker_reminder.date = details[0]["Reminder"]
  
  def get_watchlist_notes (self, cur_model_id, cur_ai_artist_id, **event_args):
    cur_ai_artist_id = cur_ai_artist_id
    print(f"get_watchlist_notes: {cur_ai_artist_id}")
    self.repeating_panel_detail.items = json.loads(anvil.server.call('get_watchlist_notes', cur_model_id, cur_ai_artist_id))
  
  def button_note_click(self, **event_args):
    print(f"button_note_click: {cur_ai_artist_id}")
    anvil.server.call('add_note', user["user_id"], cur_model_id, cur_ai_artist_id, "", "", self.text_area_note.text)
    self.text_area_note.text = ""
    self.get_watchlist_notes(cur_model_id, cur_ai_artist_id)

  def button_edit_click(self, **event_args):
    print(f"button_edit_click: {cur_ai_artist_id}")
    details = json.loads(anvil.server.call('get_watchlist_details', cur_model_id, cur_ai_artist_id))
    print(f"button_edit_click - details: {details}")
    
    if self.button_edit.icon == 'fa:edit':
      self.button_edit.icon = 'fa:save'
      self.text_box_spotify.visible = True
      self.text_box_insta.visible = True
      self.text_box_name.visible = True
      self.text_box_mail.visible = True
      self.text_box_phone.visible = True
      
      # fill text boxes
      if details[0]["SpotifyLink"] == None: self.text_box_spotify.text = details[0]["ArtistURL"]
      else: self.text_box_spotify.text = details[0]["SpotifyLink"]
      self.text_box_insta.text = details[0]["InstaLink"]
      self.text_box_name.text = details[0]["ContactName"]
      self.text_box_mail.text = details[0]["Mail"]
      self.text_box_phone.text = details[0]["Phone"]
    
    else:
      self.button_edit.icon = 'fa:edit'
      self.text_box_spotify.visible = False
      self.text_box_insta.visible = False
      self.text_box_name.visible = False
      self.text_box_mail.visible = False
      self.text_box_phone.visible = False
      
      # save text boxes
      self.update_watchlist_details()
  
  def update_watchlist_details(self, **event_args):
    print(f"update_watchlist_details: {cur_ai_artist_id}")
    details = json.loads(anvil.server.call('get_watchlist_details', cur_model_id, cur_ai_artist_id))
    print(f"update_watchlist_details - self.text_box_insta.text: {self.text_box_insta.text}")
    anvil.server.call('update_watchlist_details',
                      cur_model_id,
                      cur_ai_artist_id,
                      True,
                      self.drop_down_status.selected_value,
                      self.drop_down_priority.selected_value,
                      self.date_picker_reminder.date,
                      details[0]["Notification"],
                      self.text_box_spotify.text,
                      self.text_box_insta.text,
                      self.text_box_name.text,
                      self.text_box_mail.text,
                      self.text_box_phone.text
                      )
    
    self.get_watchlist_details(cur_model_id, cur_ai_artist_id)
  
  def button_investigate_click(self, **event_args):
    print(f"button_investigate_click: {cur_ai_artist_id}")
    open_form('Main_In', temp_artist_id = cur_ai_artist_id)

  def button_delete_click(self, **event_args):
    anvil.server.call('update_watchlist_notification', cur_model_id, cur_ai_artist_id, False, False)
    self.get_watchlist_selection()
    self.parent.parent.update_no_notifications()
    