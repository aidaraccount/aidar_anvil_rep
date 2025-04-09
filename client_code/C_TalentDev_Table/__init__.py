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
import datetime


class C_TalentDev_Table(C_TalentDev_TableTemplate):
  def __init__(self, **properties):
    """
    Initialize the Talent Development Table component
    
    Parameters:
        properties: Additional properties to pass to the parent class
    """
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # 1. Initialize user and fetch data
    global user
    user = anvil.users.get_user()
    
    # 2. Initialize component variables
    self.is_loading = True
    self.sort_column = "last_release"  # Default sort column
    self.sort_direction = "desc"  # Default sort direction (descending)
    
    # 3. Register JavaScript callbacks and make this component's client_sort_column callable
    self.client_sort_column_js = self.client_sort_column  # Create a reference
    anvil.js.window.pyClientSortColumn = self.client_sort_column_js  # Expose to JS window
    
    # Create JavaScript code that uses the exposed Python function
    anvil.js.call_js('eval', """
      window.pyArtistNameClicked = function(artistId) {
        console.log('TALENTDEV-LOG: Artist name clicked with ID:', artistId);
        location.hash = 'artists?artist_id=' + artistId;
        return true;
      }
      
      window.pySortColumn = function(columnName) {
        console.log('TALENTDEV-LOG: Sort requested for column:', columnName);
        try {
          console.log('TALENTDEV-LOG: Calling pyClientSortColumn with', columnName);
          if (typeof window.pyClientSortColumn !== 'function') {
            console.error('TALENTDEV-ERROR: pyClientSortColumn is not a function');
            return false;
          }
          const result = window.pyClientSortColumn(columnName);
          console.log('TALENTDEV-LOG: Sort result:', result);
          return result;
        } catch (error) {
          console.error('TALENTDEV-ERROR: Failed to call sort function:', error);
          return false;
        }
      }
    """)
    
    print("TALENTDEV-LOG: JavaScript callbacks registered")
    
    # 4. Load data and create table
    try:
      # Call server function to get talent development data directly in init
      print("TALENTDEV-LOG: Fetching initial data from server")
      self.data = json.loads(anvil.server.call('get_talent_dev', user['user_id']))
      
      # Debug: Print the first two data entries if available
      if self.data and len(self.data) > 0:
        print(f"TALENTDEV-LOG: First data entry: {self.data[0].get('name', 'Unknown')}")
        if len(self.data) > 1:
          print(f"TALENTDEV-LOG: Second data entry: {self.data[1].get('name', 'Unknown')}")
      else:
        print(f"TALENTDEV-LOG: No data received or empty data list")
        
      self.is_loading = False
    except Exception as e:
      print(f"TALENTDEV-ERROR: Failed to load talent development data: {str(e)}")
      self.data = []
      self.is_loading = False
    
    # 5. Initial sort by last release
    if self.data:
      print("TALENTDEV-LOG: About to perform initial sort")
      # Preprocess last_release dates for initial sort
      self._preprocess_dates_for_sort()
      self._sort_data()
      print(f"TALENTDEV-LOG: Initial data sorted by {self.sort_column} ({self.sort_direction})")
    
    # 6. Create the table with the loaded data
    self.create_table()
    
  def form_show(self, **event_args):
    """
    This method is called when the HTML panel is shown on the screen
    
    Parameters:
        event_args: Event arguments
    """
    pass

  def update_data(self):
    """
    Refreshes the data from the server and updates the display
    
    Returns:
        bool: True indicating successful completion
    """
    try:
      # Call server function to get talent development data
      print("TALENTDEV-LOG: Updating data from server")
      self.data = json.loads(anvil.server.call('get_talent_dev', user['user_id']))
      
      # Debug: Print the first data entry if available
      if self.data and len(self.data) > 0:
        print(f"TALENTDEV-LOG: (update_data) First data entry: {self.data[0].get('name', 'Unknown')}")
      else:
        print(f"TALENTDEV-LOG: (update_data) No data received or empty data list")
        
      self.is_loading = False
    except Exception as e:
      print(f"TALENTDEV-ERROR: (update_data) Failed to load talent development data: {str(e)}")
      self.data = []
      self.is_loading = False
    
    # Preprocess dates before sorting
    self._preprocess_dates_for_sort()
    
    # Sort data as currently selected
    if self.data and self.sort_column:
      self._sort_data()
      
    # Create the table with the data
    self.create_table()
    
    return True

  def format_number(self, number):
    """
    Format a number with K, M, B abbreviations
    
    Parameters:
        number: The number to format
        
    Returns:
        str: Formatted number string or "-" if no data
    """
    if number is None or number == 0:
      return "-"
    
    if number < 1000:
      return str(int(number)) if number == int(number) else str(number)
    elif number < 1000000:
      return f"{number/1000:.1f}K".replace('.0K', 'K')
    elif number < 1000000000:
      return f"{number/1000000:.1f}M".replace('.0M', 'M')
    else:
      return f"{number/1000000000:.1f}B".replace('.0B', 'B')

  def get_growth_class(self, value):
    """
    Determine CSS class for growth values
    
    Parameters:
        value: Growth percentage value
        
    Returns:
        str: CSS class name for styling
    """
    if value is None:
      return ""
    
    # Use neutral color for values close to zero (-0.5% to +0.5%)
    if -0.5 <= value <= 0.5:
      return "neutral-growth"
    elif value > 0:
      return "positive-growth"
    else:
      return "negative-growth"
      
  def format_growth(self, value):
    """
    Format growth percentage values
    
    Parameters:
        value: Growth percentage value
        
    Returns:
        str: Formatted growth string with sign
    """
    if value is None:
      return ""
    
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}%"
  
  def _preprocess_dates_for_sort(self):
    """
    Preprocess date strings in the data to avoid suspension during sorting.
    Adds a sort_date field to each item in the data.
    """
    print("TALENTDEV-LOG: Preprocessing dates for sorting")
    for item in self.data:
      date_str = item.get('last_release', '')
      
      # Store a sort value that avoids datetime conversion during sort
      if not date_str:
        item['sort_date'] = '0001-01-01'  # Minimum date for empty values
        continue
        
      try:
        # Simple string operations to ensure YYYY-MM-DD format for easy string sorting
        if '-' in date_str:  # Already in YYYY-MM-DD format
          item['sort_date'] = date_str
        elif '/' in date_str:  # MM/DD/YYYY format
          parts = date_str.split('/')
          if len(parts) == 3:
            # Convert MM/DD/YYYY to YYYY-MM-DD for string sorting
            item['sort_date'] = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
          else:
            item['sort_date'] = '0001-01-01'
        else:
          print(f"TALENTDEV-ERROR: Unknown date format: {date_str}")
          item['sort_date'] = '0001-01-01'
      except Exception as e:
        print(f"TALENTDEV-ERROR: Date preprocessing error for {date_str}: {str(e)}")
        item['sort_date'] = '0001-01-01'
    
    print("TALENTDEV-LOG: Date preprocessing complete")
  
  def _sort_data(self):
    """
    Helper method to sort data based on current sort column and direction
    
    Returns:
        None
    """
    print(f"TALENTDEV-LOG: Sorting data by {self.sort_column} ({self.sort_direction})")
    if not self.data:
      print("TALENTDEV-LOG: No data to sort")
      return
    
    reverse_sort = (self.sort_direction == "desc")
    
    # Sort the data based on the selected column
    if self.sort_column == "last_release":
      # Use the preprocessed sort_date field for sorting
      print("TALENTDEV-LOG: Sorting by last_release date using preprocessed sort_date field")
      self.data = sorted(
        self.data, 
        key=lambda x: x.get('sort_date', '0001-01-01'), 
        reverse=reverse_sort
      )
      print(f"TALENTDEV-LOG: First item after sort: {self.data[0].get('name', 'Unknown')} - {self.data[0].get('sort_date', 'None')}")
    elif self.sort_column == "total_releases":
      print("TALENTDEV-LOG: Sorting by total_tracks")
      self.data = sorted(
        self.data, 
        key=lambda x: x.get('total_tracks', 0), 
        reverse=reverse_sort
      )
    elif self.sort_column == "spotify":
      print("TALENTDEV-LOG: Sorting by spotify_mtl_listeners")
      self.data = sorted(
        self.data, 
        key=lambda x: x.get('spotify_mtl_listeners', 0), 
        reverse=reverse_sort
      )
    elif self.sort_column == "instagram":
      print("TALENTDEV-LOG: Sorting by instagram_followers")
      self.data = sorted(
        self.data, 
        key=lambda x: x.get('instagram_followers', 0), 
        reverse=reverse_sort
      )
    elif self.sort_column == "tiktok":
      print("TALENTDEV-LOG: Sorting by tiktok_followers")
      self.data = sorted(
        self.data, 
        key=lambda x: x.get('tiktok_followers', 0), 
        reverse=reverse_sort
      )
    elif self.sort_column == "youtube":
      print("TALENTDEV-LOG: Sorting by youtube_followers")
      self.data = sorted(
        self.data, 
        key=lambda x: x.get('youtube_followers', 0), 
        reverse=reverse_sort
      )
    elif self.sort_column == "soundcloud":
      print("TALENTDEV-LOG: Sorting by soundcloud_followers")
      self.data = sorted(
        self.data, 
        key=lambda x: x.get('soundcloud_followers', 0), 
        reverse=reverse_sort
      )
    
    print("TALENTDEV-LOG: Sorting complete")
  
  def client_sort_column(self, column_name):
    """
    Client-side callback function for column sorting.
    This method is designed to be called from JavaScript
    and avoids any operations that would block or suspend.
    
    Parameters:
        column_name: The name of the column to sort by
        
    Returns:
        bool: True indicating successful handling of sort request
    """
    print(f"TALENTDEV-LOG: Client sort callback triggered for column: {column_name}")
    
    # Toggle sort direction if the same column is clicked again
    if self.sort_column == column_name:
      self.sort_direction = "asc" if self.sort_direction == "desc" else "desc"
      print(f"TALENTDEV-LOG: Toggled sort direction to {self.sort_direction}")
    else:
      self.sort_column = column_name
      self.sort_direction = "desc"  # Default sort direction for new column
      print(f"TALENTDEV-LOG: Changed sort column to {self.sort_column}")
    
    # Sort the data - this must not call any server functions
    self._sort_data()
    
    # Create the table without any server calls
    self.create_table()
    
    print("TALENTDEV-LOG: Client sort completed")
    return True

  def _get_sort_indicator(self, column_name):
    """
    Helper method to get the appropriate sort indicator class
    
    Parameters:
        column_name: The name of the column
        
    Returns:
        str: CSS class for sort indicator
    """
    if self.sort_column == column_name:
      return f"talentdev-sort-indicator talentdev-sort-{self.sort_direction}"
    return "talentdev-sort-indicator"

  def create_table(self):
    """
    Creates the Talent Development table with artist data
    """
    print("TALENTDEV-LOG: Creating table")
    # 1. Create the main container HTML
    html_content = f"""
    <div class="talentdev-container">
      <table class="talentdev-table">
        <thead>
          <tr class="talentdev-header-row">
            <th class="talentdev-artist-header">Artist</th>
            <th class="talentdev-last-release-header" onclick="window.pySortColumn('last_release')">Last Release <span class="{self._get_sort_indicator('last_release')}"></span></th>
            <th class="talentdev-total-releases-header" onclick="window.pySortColumn('total_releases')">Total Releases <span class="{self._get_sort_indicator('total_releases')}"></span></th>
            <th class="talentdev-spotify-header" onclick="window.pySortColumn('spotify')"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/168px-Spotify_logo_without_text.svg.png" class="talentdev-header-icon" alt="Spotify">Monthly Listeners <span class="{self._get_sort_indicator('spotify')}"></span></th>
            <th class="talentdev-instagram-header" onclick="window.pySortColumn('instagram')"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/600px-Instagram_icon.png" class="talentdev-header-icon" alt="Instagram">Followers <span class="{self._get_sort_indicator('instagram')}"></span></th>
            <th class="talentdev-tiktok-header" onclick="window.pySortColumn('tiktok')"><img src="https://sf-tb-sg.ibytedtos.com/obj/eden-sg/uhtyvueh7nulogpogiyf/tiktok-icon2.png" class="talentdev-header-icon" alt="TikTok">Followers <span class="{self._get_sort_indicator('tiktok')}"></span></th>
            <th class="talentdev-youtube-header" onclick="window.pySortColumn('youtube')"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/800px-YouTube_full-color_icon_%282017%29.svg.png" class="talentdev-header-icon" alt="YouTube">Followers <span class="{self._get_sort_indicator('youtube')}"></span></th>
            <th class="talentdev-soundcloud-header" onclick="window.pySortColumn('soundcloud')">SoundCloud Followers <span class="{self._get_sort_indicator('soundcloud')}"></span></th>
          </tr>
        </thead>
        <tbody id="talentdev-table-body">
    """
    
    # 2. Check if data is loading or empty
    if self.is_loading:
      # Loading state message
      html_content += """
        <tr class="talentdev-row talentdev-status-row">
          <td colspan="8" class="talentdev-status-cell">
            <div class="talentdev-status-message talentdev-loading-message">Loading data...</div>
          </td>
        </tr>
      """
    elif not self.data:
      # No data message
      html_content += """
        <tr class="talentdev-row talentdev-status-row">
          <td colspan="8" class="talentdev-status-cell">
            <div class="talentdev-status-message talentdev-empty-message">No artists found</div>
          </td>
        </tr>
      """
    else:
      # Print total number of rows for debugging
      print(f"TALENTDEV-LOG: Creating table with {len(self.data)} rows")
      
      # 3. Generate table rows for each artist
      for i, item in enumerate(self.data):
        # Basic artist information
        artist_id = item.get('artist_id', '')
        artist_name = item.get('name', 'Unknown')
        artist_pic_url = item.get('artist_picture_url', '')
        
        # Last release data
        time_since_release = item.get('time_since_release', '')
        last_release_date = item.get('last_release_date', '')
        
        # Total releases data
        total_tracks = item.get('total_tracks', 0)
        new_tracks_last_365_days = item.get('new_tracks_last_365_days', 0)
        
        # Spotify data
        spotify_mtl_listeners = item.get('spotify_mtl_listeners', 0)
        spotify_mtl_dev_30d = item.get('spotify_mtl_dev_30d', None)
        
        # Instagram data
        instagram_followers = item.get('instagram_followers', 0)
        instagram_dev_30d = item.get('instagram_dev_30d', None)
        
        # TikTok data
        tiktok_followers = item.get('tiktok_followers', 0)
        tiktok_dev_30d = item.get('tiktok_dev_30d', None)
        
        # YouTube data
        youtube_followers = item.get('youtube_followers', 0)
        youtube_dev_30d = item.get('youtube_dev_30d', None)
        
        # SoundCloud data
        soundcloud_followers = item.get('soundcloud_followers', 0)
        soundcloud_dev_30d = item.get('soundcloud_dev_30d', None)
        
        # Create unique row ID
        row_id = f"talentdev-row-{i}"
        
        # Format new tracks
        new_tracks_display = f"+{new_tracks_last_365_days} last 365 d"
        
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
              <div class="talentdev-primary-value">{self.format_number(spotify_mtl_listeners)}</div>
              <div class="talentdev-secondary-value {self.get_growth_class(spotify_mtl_dev_30d)}">{self.format_growth(spotify_mtl_dev_30d)}</div>
            </td>
            <td class="talentdev-instagram-cell">
              <div class="talentdev-primary-value">{self.format_number(instagram_followers)}</div>
              <div class="talentdev-secondary-value {self.get_growth_class(instagram_dev_30d)}">{self.format_growth(instagram_dev_30d)}</div>
            </td>
            <td class="talentdev-tiktok-cell">
              <div class="talentdev-primary-value">{self.format_number(tiktok_followers)}</div>
              <div class="talentdev-secondary-value {self.get_growth_class(tiktok_dev_30d)}">{self.format_growth(tiktok_dev_30d)}</div>
            </td>
            <td class="talentdev-youtube-cell">
              <div class="talentdev-primary-value">{self.format_number(youtube_followers)}</div>
              <div class="talentdev-secondary-value {self.get_growth_class(youtube_dev_30d)}">{self.format_growth(youtube_dev_30d)}</div>
            </td>
            <td class="talentdev-soundcloud-cell">
              <div class="talentdev-primary-value">{self.format_number(soundcloud_followers)}</div>
              <div class="talentdev-secondary-value {self.get_growth_class(soundcloud_dev_30d)}">{self.format_growth(soundcloud_dev_30d)}</div>
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
    print("TALENTDEV-LOG: Table created and rendered")
