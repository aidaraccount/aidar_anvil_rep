from ._anvil_designer import C_TalentDev_TableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import anvil.js
from anvil import get_open_form
import time
from anvil.js.window import location


class C_TalentDev_Table(C_TalentDev_TableTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # 1. Initialize user and fetch data
    global user
    user = anvil.users.get_user()
    
    # 2. Initialize component variables
    self.is_loading = True
    
    # 3. Register JavaScript callbacks
    anvil.js.call_js('eval', """
      window.pyArtistNameClicked = function(artistId) {
        console.log('[DEBUG] Artist name clicked with ID:', artistId);
        location.hash = 'artists?artist_id=' + artistId;
        return true;
      }
    """)
    
    # 4. Load data and create table
    self.load_data()
    
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass

  def load_data(self):
    """
    Loads data from the server and refreshes the display
    """
    try:
      # Call server function to get talent development data
      self.data = json.loads(anvil.server.call('get_talent_dev', user['user_id']))
      self.is_loading = False
    except Exception as e:
      print(f"[ERROR] Failed to load talent development data: {str(e)}")
      self.data = []
      self.is_loading = False
    
    # Create the table with the data
    self.create_table()
    
    return True

  def update_data(self):
    """
    Refreshes the data from the server and updates the display
    """
    self.is_loading = True
    self.create_table()  # Show loading state
    self.load_data()
    
    return True

  def create_table(self):
    """
    Creates the Talent Development table with artist data
    """
    # 1. Create the main container HTML
    html_content = """
    <div class="talentdev-container">
      <table class="talentdev-table">
        <thead>
          <tr class="talentdev-header-row">
            <th class="talentdev-pic-header"></th>
            <th class="talentdev-name-header">Artist</th>
            <th class="talentdev-date-header">Last Release</th>
          </tr>
        </thead>
        <tbody id="talentdev-table-body">
    """
    
    # 2. Check if data is loading or empty
    if self.is_loading:
      # Loading state message
      html_content += """
        <tr class="talentdev-row talentdev-status-row">
          <td colspan="3" class="talentdev-status-cell">
            <div class="talentdev-status-message talentdev-loading-message">Loading data...</div>
          </td>
        </tr>
      """
    elif not self.data:
      # No data message
      html_content += """
        <tr class="talentdev-row talentdev-status-row">
          <td colspan="3" class="talentdev-status-cell">
            <div class="talentdev-status-message talentdev-empty-message">No artists found</div>
          </td>
        </tr>
      """
    else:
      # 3. Generate table rows for each artist
      for i, item in enumerate(self.data):
        artist_id = item.get('artist_id', '')
        artist_name = item.get('name', 'Unknown')
        artist_pic_url = item.get('artist_picture_url', '')
        last_release_date = item.get('last_release_date', '')
        
        # Create unique row ID
        row_id = f"talentdev-row-{i}"
        
        # Add the row for this artist
        html_content += f"""
          <tr id="{row_id}" class="talentdev-row">
            <td class="talentdev-pic-cell">
              <img src="{artist_pic_url}" class="talentdev-artist-pic" alt="{artist_name}">
            </td>
            <td class="talentdev-name-cell">
              <a href="javascript:void(0)" onclick="window.pyArtistNameClicked('{artist_id}')">{artist_name}</a>
            </td>
            <td class="talentdev-date-cell">{last_release_date}</td>
          </tr>
        """
    
    # 4. Complete the HTML for the table
    html_content += """
        </tbody>
      </table>
    </div>
    """
    
    # 5. Set the HTML content
    self.html = html_content
