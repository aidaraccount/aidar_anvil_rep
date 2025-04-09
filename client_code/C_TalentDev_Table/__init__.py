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
    try:
      # Call server function to get talent development data directly in init
      self.data = json.loads(anvil.server.call('get_talent_dev', user['user_id']))
      
      # Debug: Print the first two data entries if available
      if self.data and len(self.data) > 0:
        print(f"[DEBUG] First data entry: {self.data[0]}")
        if len(self.data) > 1:
          print(f"[DEBUG] Second data entry: {self.data[1]}")
      else:
        print(f"[DEBUG] No data received or empty data list: {self.data}")
        
      self.is_loading = False
    except Exception as e:
      print(f"[ERROR] Failed to load talent development data: {str(e)}")
      self.data = []
      self.is_loading = False
    
    # 5. Create the table with the loaded data
    self.create_table()
    
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass

  def update_data(self):
    """
    Refreshes the data from the server and updates the display.
    This method is kept for potential future use when you need to refresh data
    without reconstructing the entire component.
    """
    try:
      # Call server function to get talent development data
      self.data = json.loads(anvil.server.call('get_talent_dev', user['user_id']))
      
      # Debug: Print the first data entry if available
      if self.data and len(self.data) > 0:
        print(f"[DEBUG] (update_data) First data entry: {self.data[0]}")
      else:
        print(f"[DEBUG] (update_data) No data received or empty data list: {self.data}")
        
      self.is_loading = False
    except Exception as e:
      print(f"[ERROR] (update_data) Failed to load talent development data: {str(e)}")
      self.data = []
      self.is_loading = False
    
    # Create the table with the data
    self.create_table()
    
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
            <th class="talentdev-artist-header">Artist</th>
            <th class="talentdev-last-release-header">Last Release</th>
            <th class="talentdev-total-releases-header">Total Releases</th>
            <th class="talentdev-spotify-header">Monthly Listeners</th>
          </tr>
        </thead>
        <tbody id="talentdev-table-body">
    """
    
    # 2. Check if data is loading or empty
    if self.is_loading:
      # Loading state message
      html_content += """
        <tr class="talentdev-row talentdev-status-row">
          <td colspan="4" class="talentdev-status-cell">
            <div class="talentdev-status-message talentdev-loading-message">Loading data...</div>
          </td>
        </tr>
      """
    elif not self.data:
      # No data message
      html_content += """
        <tr class="talentdev-row talentdev-status-row">
          <td colspan="4" class="talentdev-status-cell">
            <div class="talentdev-status-message talentdev-empty-message">No artists found</div>
          </td>
        </tr>
      """
    else:
      # Print total number of rows for debugging
      print(f"[DEBUG] Creating table with {len(self.data)} rows")
      
      # 3. Generate table rows for each artist
      for i, item in enumerate(self.data):
        artist_id = item.get('artist_id', '')
        artist_name = item.get('name', 'Unknown')
        artist_pic_url = item.get('artist_picture_url', '')
        
        # Last release data
        time_since_release = item.get('time_since_release', '')
        last_release_date = item.get('last_release_date', '')
        
        # Total releases data
        total_tracks = item.get('total_tracks', '0')
        new_tracks_last_365_days = item.get('new_tracks_last_365_days', '0')
        
        # Spotify listeners data
        spotify_mtl_listeners = item.get('spotify_mtl_listeners', 0)  
        spotify_mtl_dev_30d = item.get('spotify_mtl_dev_30d', None)
        
        # Create unique row ID
        row_id = f"talentdev-row-{i}"
        
        # Format Spotify development with + sign if positive
        spotify_dev_display = ""
        if spotify_mtl_dev_30d is not None:
            sign = "+" if spotify_mtl_dev_30d > 0 else ""
            spotify_dev_display = f"{sign}{spotify_mtl_dev_30d:.1f}%"
            # Add CSS class for growth coloring
            spotify_dev_class = "positive-growth" if spotify_mtl_dev_30d >= 0 else "negative-growth"
        else:
            spotify_dev_class = ""
        
        # Format total tracks with + sign for new tracks
        new_tracks_display = f"+{new_tracks_last_365_days} last 365 d"
        
        # Format Spotify listeners with comma separators if not None
        if spotify_mtl_listeners is not None:
            spotify_listeners_display = f"{spotify_mtl_listeners:,}"
        else:
            spotify_listeners_display = "0"
        
        # Add the row for this artist
        html_content += f"""
          <tr id="{row_id}" class="talentdev-row">
            <td class="talentdev-artist-cell">
              <div class="talentdev-artist-container">
                <img src="{artist_pic_url}" class="talentdev-artist-pic" alt="{artist_name}">
                <a href="javascript:void(0)" onclick="window.pyArtistNameClicked('{artist_id}')" class="talentdev-artist-name">{artist_name}</a>
              </div>
            </td>
            <td class="talentdev-last-release-cell">
              <div class="talentdev-primary-value">{time_since_release}</div>
              <div class="talentdev-secondary-value">{last_release_date}</div>
            </td>
            <td class="talentdev-total-releases-cell">
              <div class="talentdev-primary-value">{total_tracks}</div>
              <div class="talentdev-secondary-value">{new_tracks_display}</div>
            </td>
            <td class="talentdev-spotify-cell">
              <div class="talentdev-primary-value">{spotify_listeners_display}</div>
              <div class="talentdev-secondary-value {spotify_dev_class}">{spotify_dev_display}</div>
            </td>
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
