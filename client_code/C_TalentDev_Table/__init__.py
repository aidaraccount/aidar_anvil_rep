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
from ..C_TalentDev_Toggle import C_TalentDev_Toggle


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
    self.active_period = "30d"  # Default period for stats display (7d, 30d)
    self.active_format = "abs"  # Default format for stats display (abs, pct)
    self.active_sort_by = "current"  # Default sort by (current, growth)
    self.search_filter = ""  # Initialize empty search filter
    self.original_data = []  # Store original data for filtering
    self.active_watchlist_ids = []  # Store active watchlist IDs for filtering
    
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
    
    # 5. Load data and create table
    try:
      # Call server function to get talent development data directly in init
      print("TALENTDEV-LOG: Fetching initial data from server")
      self.data = json.loads(anvil.server.call('get_talent_dev', user['user_id']))
      
      # Store original data for filtering
      self.original_data = self.data.copy()
      
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
    
    # 6. Initial sort by last release
    if self.data:
      print("TALENTDEV-LOG: About to perform initial sort")
      # Preprocess dates for initial sort
      self._preprocess_dates_for_sort()
      self._sort_data()
      print(f"TALENTDEV-LOG: Initial data sorted by {self.sort_column} ({self.sort_direction})")
    
    # 7. Create the table with the loaded data
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
      
      # Store original data for filtering
      self.original_data = self.data.copy()
      
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
    
    # Store sign for later and work with absolute value
    is_negative = number < 0
    abs_number = abs(number)
    
    # Format the absolute value
    if abs_number < 1000:
      formatted = str(int(abs_number)) if abs_number == int(abs_number) else str(abs_number)
    elif abs_number < 1000000:
      formatted = f"{abs_number/1000:.1f}K".replace('.0K', 'K')
    elif abs_number < 1000000000:
      formatted = f"{abs_number/1000000:.1f}M".replace('.0M', 'M')
    else:
      formatted = f"{abs_number/1000000000:.1f}B".replace('.0B', 'B')
    
    # Add negative sign if needed
    return f"-{formatted}" if is_negative else formatted

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
    Format growth percentage or absolute values
    
    Parameters:
        value: Growth value (percentage or absolute)
        
    Returns:
        str: Formatted growth string with sign
    """
    if value is None:
      return "-"
    
    # Determine if we're showing percentage or absolute value
    if self.active_format == "pct":
      # Format as percentage
      sign = "+" if value > 0 else ""
      return f"{sign}{value:.1f}%"
    else:
      # Format as absolute value
      sign = "+" if value > 0 else ""
      return f"{sign}{self.format_number(value)}"

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
    print(f"TALENTDEV-LOG: Sorting by {self.sort_column} ({self.sort_direction}) - sort_by: {self.active_sort_by}")
    
    reverse_sort = self.sort_direction == "desc"
    
    # 1. For non-toggleable columns, sort normally regardless of toggle state
    if self.sort_column == "artist_name":
      # Sort by artist name
      self.data = sorted(self.data, key=lambda x: x.get('name', '').lower(), reverse=reverse_sort)
      return
    elif self.sort_column == "last_release":
      # Always sort by the release date
      self.data = sorted(self.data, key=lambda x: x.get('sort_date', '0001-01-01'), reverse=reverse_sort)
      return
      
    # 2. For toggleable columns, apply different sort logic based on active_sort_by
    if self.sort_column == "total_releases":
      # Sort by either total tracks or new tracks based on active_sort_by
      if self.active_sort_by == "current":
        # Sort by total tracks (first line)
        self.data = sorted(self.data, key=lambda x: x.get('total_tracks', 0) or 0, reverse=reverse_sort)
      else:  # active_sort_by == "growth"
        # Sort by new tracks in last 365 days (second line)
        self.data = sorted(self.data, key=lambda x: x.get('new_tracks_last_365_days', 0) or 0, reverse=reverse_sort)
    else:
      # 3. For follower/listener columns, use both active_sort_by and active_format toggles
      if self.active_sort_by == "current":
        # Sort by current values (first line)
        if self.sort_column == "spotify":
          self.data = sorted(self.data, key=lambda x: x.get('spotify_mtl_listeners', 0) or 0, reverse=reverse_sort)
        elif self.sort_column == "instagram":
          self.data = sorted(self.data, key=lambda x: x.get('instagram_followers', 0) or 0, reverse=reverse_sort)
        elif self.sort_column == "tiktok":
          self.data = sorted(self.data, key=lambda x: x.get('tiktok_followers', 0) or 0, reverse=reverse_sort)
        elif self.sort_column == "youtube":
          self.data = sorted(self.data, key=lambda x: x.get('youtube_followers', 0) or 0, reverse=reverse_sort)
        elif self.sort_column == "soundcloud":
          self.data = sorted(self.data, key=lambda x: x.get('soundcloud_followers', 0) or 0, reverse=reverse_sort)
      else:  # active_sort_by == "growth"
        # Sort by growth values (second line)
        # Both active_period and active_format affect the key selection
        change_period = self.active_period
        change_type = self.active_format
        
        # Build the correct key based on all relevant toggle states
        if self.sort_column == "spotify":
          # Try both naming schemes (growth/change) for compatibility
          growth_key = f"spotify_mtl_{change_type}_growth_{change_period}"
          change_key = f"spotify_mtl_{change_type}_change_{change_period}"
          self.data = sorted(self.data, key=lambda x: x.get(growth_key, x.get(change_key, 0)) or 0, reverse=reverse_sort)
        elif self.sort_column == "instagram":
          growth_key = f"instagram_{change_type}_growth_{change_period}"
          change_key = f"instagram_{change_type}_change_{change_period}"
          self.data = sorted(self.data, key=lambda x: x.get(growth_key, x.get(change_key, 0)) or 0, reverse=reverse_sort)
        elif self.sort_column == "tiktok":
          growth_key = f"tiktok_{change_type}_growth_{change_period}"
          change_key = f"tiktok_{change_type}_change_{change_period}"
          self.data = sorted(self.data, key=lambda x: x.get(growth_key, x.get(change_key, 0)) or 0, reverse=reverse_sort)
        elif self.sort_column == "youtube":
          growth_key = f"youtube_{change_type}_growth_{change_period}"
          change_key = f"youtube_{change_type}_change_{change_period}"
          self.data = sorted(self.data, key=lambda x: x.get(growth_key, x.get(change_key, 0)) or 0, reverse=reverse_sort)
        elif self.sort_column == "soundcloud":
          growth_key = f"soundcloud_{change_type}_growth_{change_period}"
          change_key = f"soundcloud_{change_type}_change_{change_period}"
          self.data = sorted(self.data, key=lambda x: x.get(growth_key, x.get(change_key, 0)) or 0, reverse=reverse_sort)
  
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
    
    # Apply fixed layout to prevent column width changes during sorting
    anvil.js.call_js('eval', """
      document.querySelector('.talentdev-table').style.tableLayout = 'fixed';
    """)
    
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

  def _create_table_headers(self):
    """
    Create the HTML for the table headers
    
    Returns:
        str: HTML for the table headers
    """
    return f"""
      <thead>
        <tr class="talentdev-header-row">
          <th class="talentdev-artist-header">Artist</th>
          <th class="talentdev-last-release-header" onclick="window.pySortColumn('last_release')">Last Release <span class="{self._get_sort_indicator('last_release')}"></span></th>
          <th class="talentdev-total-releases-header" onclick="window.pySortColumn('total_releases')">Total Releases <span class="{self._get_sort_indicator('total_releases')}"></span></th>
          <th class="talentdev-spotify-header" onclick="window.pySortColumn('spotify')"><i class="fa-brands fa-spotify talentdev-header-icon"></i>Mtl. Listeners <span class="{self._get_sort_indicator('spotify')}"></span></th>
          <th class="talentdev-instagram-header" onclick="window.pySortColumn('instagram')"><i class="fa-brands fa-instagram talentdev-header-icon"></i>Followers <span class="{self._get_sort_indicator('instagram')}"></span></th>
          <th class="talentdev-tiktok-header" onclick="window.pySortColumn('tiktok')"><i class="fa-brands fa-tiktok talentdev-header-icon"></i>Followers <span class="{self._get_sort_indicator('tiktok')}"></span></th>
          <th class="talentdev-youtube-header" onclick="window.pySortColumn('youtube')"><i class="fa-brands fa-youtube talentdev-header-icon"></i>Followers <span class="{self._get_sort_indicator('youtube')}"></span></th>
          <th class="talentdev-soundcloud-header" onclick="window.pySortColumn('soundcloud')"><i class="fa-brands fa-soundcloud talentdev-header-icon"></i>Followers <span class="{self._get_sort_indicator('soundcloud')}"></span></th>
        </tr>
      </thead>
    """

  def create_table(self):
    """
    Create the HTML for the table based on current data and state
    
    Returns:
        None
    """
    # Initialize table HTML
    html_content = f"""
      <div class="talentdev-container">
        <table class="talentdev-table">
    """
    
    # Create table headers
    html_content += self._create_table_headers()
    
    # Create table body
    html_content += "<tbody>"
    
    # Check if we have data to show
    if not self.data:
      # Show empty watchlist message if no data or no active watchlists
      empty_message = "No artists found matching your current filters."
        
      html_content += f"""
        <tr>
          <td colspan="8" class="talentdev-empty-message-container">
            <div class="talentdev-empty-message">{empty_message}</div>
          </td>
        </tr>
      """
    else:
      # We have data, create normal table rows
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
        
        # Try both growth and change fields to ensure backward compatibility
        spotify_growth = None
        if self.active_period == "7d":
            # Try growth field first, then fall back to change field
            growth_field = f"spotify_mtl_{self.active_format}_growth_7d"
            change_field = f"spotify_mtl_{self.active_format}_change_7d"
            spotify_growth = item.get(growth_field) if item.get(growth_field) is not None else item.get(change_field)
        else:  # 30d
            growth_field = f"spotify_mtl_{self.active_format}_growth_30d"
            change_field = f"spotify_mtl_{self.active_format}_change_30d"
            spotify_growth = item.get(growth_field) if item.get(growth_field) is not None else item.get(change_field)
        
        # Instagram data
        instagram_followers = item.get('instagram_followers', 0)
        
        # Try both growth and change fields
        instagram_growth = None
        if self.active_period == "7d":
            growth_field = f"instagram_{self.active_format}_growth_7d"
            change_field = f"instagram_{self.active_format}_change_7d"
            instagram_growth = item.get(growth_field) if item.get(growth_field) is not None else item.get(change_field)
        else:  # 30d
            growth_field = f"instagram_{self.active_format}_growth_30d"
            change_field = f"instagram_{self.active_format}_change_30d"
            instagram_growth = item.get(growth_field) if item.get(growth_field) is not None else item.get(change_field)
        
        # TikTok data
        tiktok_followers = item.get('tiktok_followers', 0)
        
        # Try both growth and change fields
        tiktok_growth = None
        if self.active_period == "7d":
            growth_field = f"tiktok_{self.active_format}_growth_7d"
            change_field = f"tiktok_{self.active_format}_change_7d"
            tiktok_growth = item.get(growth_field) if item.get(growth_field) is not None else item.get(change_field)
        else:  # 30d
            growth_field = f"tiktok_{self.active_format}_growth_30d"
            change_field = f"tiktok_{self.active_format}_change_30d"
            tiktok_growth = item.get(growth_field) if item.get(growth_field) is not None else item.get(change_field)
        
        # YouTube data
        youtube_followers = item.get('youtube_followers', 0)
        
        # Try both growth and change fields
        youtube_growth = None
        if self.active_period == "7d":
            growth_field = f"youtube_{self.active_format}_growth_7d"
            change_field = f"youtube_{self.active_format}_change_7d"
            youtube_growth = item.get(growth_field) if item.get(growth_field) is not None else item.get(change_field)
        else:  # 30d
            growth_field = f"youtube_{self.active_format}_growth_30d"
            change_field = f"youtube_{self.active_format}_change_30d"
            youtube_growth = item.get(growth_field) if item.get(growth_field) is not None else item.get(change_field)
        
        # SoundCloud data
        soundcloud_followers = item.get('soundcloud_followers', 0)
        
        # Try both growth and change fields
        soundcloud_growth = None
        if self.active_period == "7d":
            growth_field = f"soundcloud_{self.active_format}_growth_7d"
            change_field = f"soundcloud_{self.active_format}_change_7d"
            soundcloud_growth = item.get(growth_field) if item.get(growth_field) is not None else item.get(change_field)
        else:  # 30d
            growth_field = f"soundcloud_{self.active_format}_growth_30d"
            change_field = f"soundcloud_{self.active_format}_change_30d"
            soundcloud_growth = item.get(growth_field) if item.get(growth_field) is not None else item.get(change_field)
        
        # Format new tracks last 365 days
        if new_tracks_last_365_days:
          formatted_new_tracks = f"{new_tracks_last_365_days} last 365 d"
        else:
          formatted_new_tracks = "0 last 365 d"
        
        # Create row HTML for this artist
        html_content += f"""
          <tr class="talentdev-row">
            <td class="talentdev-artist-cell">
              <div class="talentdev-artist-container">
                <img src="{artist_pic_url}" class="talentdev-artist-pic" onerror="this.src='https://via.placeholder.com/40'">
                <a href="javascript:void(0)" onclick="window.pyArtistNameClicked('{artist_id}')" class="talentdev-artist-name">{artist_name}</a>
              </div>
            </td>
            <td class="talentdev-last-release-cell">
              <div class="talentdev-primary-value">{time_since_release}</div>
              <div class="talentdev-secondary-value">{last_release_date}</div>
            </td>
            <td class="talentdev-total-releases-cell">
              <div class="talentdev-primary-value">{total_tracks}</div>
              <div class="talentdev-secondary-value">{formatted_new_tracks}</div>
            </td>
            <td class="talentdev-spotify-cell">
              <div class="talentdev-primary-value">{self.format_number(spotify_mtl_listeners)}</div>
              <div class="talentdev-secondary-value {self.get_growth_class(spotify_growth) if spotify_mtl_listeners != None and spotify_mtl_listeners != 0 else ''}">{self.format_growth(spotify_growth) if spotify_mtl_listeners != None and spotify_mtl_listeners != 0 else '&nbsp;'}</div>
            </td>
            <td class="talentdev-instagram-cell">
              <div class="talentdev-primary-value">{self.format_number(instagram_followers)}</div>
              <div class="talentdev-secondary-value {self.get_growth_class(instagram_growth) if instagram_followers != None and instagram_followers != 0 else ''}">{self.format_growth(instagram_growth) if instagram_followers != None and instagram_followers != 0 else '&nbsp;'}</div>
            </td>
            <td class="talentdev-tiktok-cell">
              <div class="talentdev-primary-value">{self.format_number(tiktok_followers)}</div>
              <div class="talentdev-secondary-value {self.get_growth_class(tiktok_growth) if tiktok_followers != None and tiktok_followers != 0 else ''}">{self.format_growth(tiktok_growth) if tiktok_followers != None and tiktok_followers != 0 else '&nbsp;'}</div>
            </td>
            <td class="talentdev-youtube-cell">
              <div class="talentdev-primary-value">{self.format_number(youtube_followers)}</div>
              <div class="talentdev-secondary-value {self.get_growth_class(youtube_growth) if youtube_followers != None and youtube_followers != 0 else ''}">{self.format_growth(youtube_growth) if youtube_followers != None and youtube_followers != 0 else '&nbsp;'}</div>
            </td>
            <td class="talentdev-soundcloud-cell">
              <div class="talentdev-primary-value">{self.format_number(soundcloud_followers)}</div>
              <div class="talentdev-secondary-value {self.get_growth_class(soundcloud_growth) if soundcloud_followers != None and soundcloud_followers != 0 else ''}">{self.format_growth(soundcloud_growth) if soundcloud_followers != None and soundcloud_followers != 0 else '&nbsp;'}</div>
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

  def filter_by_artist_name(self, search_term):
    """
    Filter the table data by artist name
    
    Parameters:
        search_term: The search term to filter by (case-insensitive partial match)
    """
    print(f"TALENTDEV-LOG: Filtering by artist name: '{search_term}'")
    
    # Store search filter
    self.search_filter = search_term.lower()
    
    # If we have original data and a search term
    if hasattr(self, 'original_data') and self.original_data:
      if search_term:
        # Filter the data by artist name (case insensitive)
        self.data = [
          artist for artist in self.original_data 
          if search_term.lower() in artist.get('name', '').lower()
        ]
      else:
        # If no search term, restore original data
        self.data = self.original_data.copy()
      
      # Re-sort the filtered data if a sort is active
      if hasattr(self, 'sort_column') and self.sort_column:
        self._sort_data()
      
      # Recreate the table with filtered data
      self.create_table()
  
  def filter_by_watchlists(self, active_watchlist_ids):
    """
    Filter the table data by watchlist IDs
    
    Parameters:
        active_watchlist_ids: List of active watchlist IDs to filter by
    """
    print(f"TALENTDEV-LOG: Filtering by watchlist IDs: {active_watchlist_ids}")
    
    # Store active watchlist IDs
    self.active_watchlist_ids = [int(wl_id) for wl_id in active_watchlist_ids]
    
    # Start with the original data (may be already filtered by search)
    filtered_data = self.original_data.copy()
    
    # Apply search filter if it exists
    if self.search_filter:
      filtered_data = [
        artist for artist in filtered_data 
        if self.search_filter.lower() in artist.get('name', '').lower()
      ]
    
    # Apply watchlist filtering
    if active_watchlist_ids:
      # Filter artists that are in any of the active watchlists
      self.data = [
        artist for artist in filtered_data 
        if any(
          int(wl_id) in artist.get('watchlist_ids', []) 
          for wl_id in active_watchlist_ids
        )
      ]
    else:
      # If no active watchlists, don't show any artists
      self.data = []
      
    # Re-sort the filtered data if a sort is active and data exists
    if self.data and hasattr(self, 'sort_column') and self.sort_column:
      self._sort_data()
      
    # Recreate the table with filtered data
    self.create_table()
  
  def handle_period_toggle(self, period):
    """
    Callback for when the period toggle changes
    
    Parameters:
        period: The new period selected (7-Day or 30-Day)
        
    Returns:
        bool: True indicating successful handling of toggle request
    """
    print(f"TALENTDEV-LOG: Handling period toggle to {period}")
    self.active_period = period
    
    # Update the table with the new period
    self.create_table()
    
    return True

  def fetch_data(self):
    """
    Fetch data from the server and prepare for display
    
    Returns:
        None
    """
    try:
      # 1. Fetch artists
      print(f"TALENTDEV-LOG: Fetching data from server...")
      artists = anvil.server.call('get_user_artists', user["user_id"])
      self.data = artists
      
      # 2. Store original data for filtering
      self.original_data = artists.copy()
      
      # 3. Sort data by default
      self._sort_data()
    except Exception as e:
      print(f"TALENTDEV-ERROR: Failed to load talent development data: {str(e)}")
      self.data = []
      self.is_loading = False
