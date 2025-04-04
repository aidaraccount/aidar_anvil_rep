from ._anvil_designer import C_Home_NextUpTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import anvil.js
from anvil import get_open_form
from ..nav import click_button, save_var
import time
from anvil.js.window import location
import traceback


class C_Home_NextUp(C_Home_NextUpTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.data = data
    
    # 1. Register JavaScript callbacks
    print("NEXTUP_DEBUG: Registering JavaScript callbacks")
    try:
      anvil.js.window.pyArtistClicked = self.handle_artist_click
      anvil.js.window.pyRadioClicked = self.handle_radio_click
      anvil.js.window.pyWatchlistClicked = self.handle_watchlist_click
      print("NEXTUP_DEBUG: Callbacks registered successfully")
    except Exception as e:
      print(f"NEXTUP_ERROR: Failed to register callbacks: {str(e)}")
    
    # 2. Create NextUp table
    self.create_nextup_table()
    
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass
    
  def handle_artist_click(self, artist_id, **kwargs):
    """
    JavaScript callback for when an artist row is clicked.
    
    Args:
        artist_id: The ID of the artist to navigate to
    """
    print(f"NEXTUP_DEBUG: Artist clicked, ID: {artist_id}")
    try:
      # Navigate to the artist's page using the nav.click_button function
      click_button('artist_view', {'artist_id': artist_id})
      return {"success": True, "artist_id": artist_id}
    except Exception as e:
      print(f"NEXTUP_ERROR: Error in artist click handler: {str(e)}")
      print(f"NEXTUP_ERROR: {traceback.format_exc()}")
      return {"success": False, "error": str(e)}
    
  def handle_radio_click(self, artist_id, watchlist_id, row_id, **kwargs):
    """
    JavaScript callback for when a radio button is clicked.
    The row will be removed from the table.
    
    Args:
        artist_id: The ID of the artist
        watchlist_id: The ID of the watchlist entry
        row_id: The HTML ID of the row to remove
    """
    try:
      # Print information about the clicked radio button
      print(f"NEXTUP_DEBUG: Radio clicked for artist {artist_id}, watchlist {watchlist_id}, row {row_id}")
      
      # Here you would typically update a database or perform an action
      # anvil.server.call('update_artist_status', artist_id, watchlist_id)
      
      # Use anvil.js.call to execute JavaScript to remove the row
      print(f"NEXTUP_DEBUG: Removing row {row_id} from DOM")
      js_code = f"""
      (function() {{
        const row = document.getElementById('{row_id}');
        if (row) {{
          row.style.transition = 'opacity 0.3s ease';
          row.style.opacity = '0';
          setTimeout(function() {{
            if (row.parentNode) {{
              row.parentNode.removeChild(row);
              console.log('NEXTUP_DEBUG: Row {row_id} removed');
            }}
          }}, 300);
          return true;
        }} else {{
          console.warn('NEXTUP_DEBUG: Row {row_id} not found');
          return false;
        }}
      }})();
      """
      result = anvil.js.call_js('eval', js_code)
      print(f"NEXTUP_DEBUG: Row removal result: {result}")
      
      return {"success": True, "artist_id": artist_id, "watchlist_id": watchlist_id, "row_id": row_id}
    except Exception as e:
      print(f"NEXTUP_ERROR: Error in radio click handler: {str(e)}")
      print(f"NEXTUP_ERROR: {traceback.format_exc()}")
      return {"success": False, "error": str(e)}
    
  def handle_watchlist_click(self, artist_id, watchlist_id, **kwargs):
    """
    JavaScript callback for when the watchlist icon button is clicked.
    Redirects to the watchlist details page.
    
    Args:
        artist_id: The ID of the artist
        watchlist_id: The ID of the watchlist entry
    """
    try:
      print(f"NEXTUP_DEBUG: Watchlist button clicked for artist {artist_id}, watchlist {watchlist_id}")
      
      # Navigate to the watchlist details page
      click_button('watchlist_details', {'watchlist_id': watchlist_id, 'artist_id': artist_id})
      return {"success": True, "artist_id": artist_id, "watchlist_id": watchlist_id}
    except Exception as e:
      print(f"NEXTUP_ERROR: Error in watchlist click handler: {str(e)}")
      print(f"NEXTUP_ERROR: {traceback.format_exc()}")
      return {"success": False, "error": str(e)}

  def create_nextup_table(self):
    """
    Creates the NextUp table with artist data
    """
    # 1. Dictionary of status abbreviations
    status_abbr = {
      'Action required': 'Act. req.',
      'Requires revision': 'Rev. req.',
      'Waiting for decision': 'Wait. dec.',
      'Build connection': 'Build con.',
      'Awaiting response': 'Await. resp.',
      'Exploring opportunities': 'Expl. op.',
      'Positive response': 'Pos. resp.',
      'In negotiations': 'In neg.',
      'Contract in progress': 'Contr. prog.',
      'Reconnect later': 'Recon. later',
      'Not interested': 'Not int.',
      'Success': 'Success'
    }
    
    # 2. Create the main container HTML
    html_content = """
    <div class="nextup-container">
      <table class="nextup-table">
        <tbody id="nextup-table-body">
    """
    
    # 3. Generate table rows for each artist
    for i, item in enumerate(self.data):
      artist_id = item.get('artist_id', '')
      artist_name = item.get('name', 'Unknown')
      artist_pic_url = item.get('artist_picture_url', '')
      status = item.get('status', '')
      priority = item.get('priority', '')
      watchlist_id = item.get('watchlist_id', '')
      
      # Get status abbreviation from dictionary
      status_display = status_abbr.get(status, status)
      
      # Format priority with first letter capitalized
      priority_display = priority.capitalize() if priority else ''
      
      # Create unique row ID
      row_id = f"nextup-row-{i}"
      
      # Add the row for this artist
      html_content += f"""
        <tr id="{row_id}" class="nextup-row" onclick="window.artistClicked(event, '{artist_id}')">
          <td class="nextup-radio-cell">
            <div class="radio-button" onclick="window.radioClicked(event, '{artist_id}', '{watchlist_id}', '{row_id}')">
              <div class="radio-dot"></div>
            </div>
          </td>
          <td class="nextup-pic-cell">
            <img src="{artist_pic_url}" class="nextup-artist-pic" alt="{artist_name}">
          </td>
          <td class="nextup-name-cell">{artist_name}</td>
          <td class="nextup-status-cell">{status_display}</td>
          <td class="nextup-priority-cell">{priority_display}</td>
          <td class="nextup-button-cell">
            <button class="icon-button-disabled-small" 
                    data-watchlist-id="{watchlist_id}" 
                    data-artist-id="{artist_id}" 
                    onclick="window.watchlistClicked(event, '{artist_id}', '{watchlist_id}')">
              <i class="fa fa-vcard-o"></i>
            </button>
          </td>
        </tr>
      """
    
    # 4. Complete the HTML
    html_content += """
        </tbody>
      </table>
    </div>
    """
    
    # 5. JavaScript for handling clicks
    js_code = """
    console.log('NEXTUP_DEBUG: NextUp table JavaScript loaded');
    
    // Function to handle artist row clicks
    window.artistClicked = function(event, artistId) {
      event.stopPropagation();
      console.log('NEXTUP_DEBUG: Artist clicked, ID:', artistId);
      
      // Ignore clicks on the button or radio
      if (event.target.closest('.icon-button-disabled-small') || 
          event.target.closest('i.fa') ||
          event.target.closest('.radio-button') ||
          event.target.closest('.radio-dot')) {
        console.log('NEXTUP_DEBUG: Button or radio clicked, stopping propagation');
        return;
      }
      
      // Call the Python callback
      if (typeof window.pyArtistClicked === 'function') {
        try {
          // Call without promises
          console.log('NEXTUP_DEBUG: Calling Python artist callback');
          var result = window.pyArtistClicked(artistId);
          console.log('NEXTUP_DEBUG: Python callback completed:', result);
        } catch (err) {
          console.error('NEXTUP_ERROR: Error calling Python function:', err);
        }
      } else {
        console.warn('NEXTUP_DEBUG: Python artist callback not available');
      }
    };
    
    // Function to handle radio button clicks
    window.radioClicked = function(event, artistId, watchlistId, rowId) {
      event.stopPropagation();
      console.log('NEXTUP_DEBUG: Radio clicked for artist:', artistId, 'watchlist:', watchlistId);
      
      // Call the Python callback
      if (typeof window.pyRadioClicked === 'function') {
        try {
          // Call without promises
          console.log('NEXTUP_DEBUG: Calling Python radio callback');
          var result = window.pyRadioClicked(artistId, watchlistId, rowId);
          console.log('NEXTUP_DEBUG: Python radio callback completed:', result);
        } catch (err) {
          console.error('NEXTUP_ERROR: Error calling Python radio function:', err);
        }
      } else {
        console.warn('NEXTUP_DEBUG: Python radio callback not available');
      }
    };
    
    // Function to handle watchlist icon button clicks
    window.watchlistClicked = function(event, artistId, watchlistId) {
      event.stopPropagation();
      console.log('NEXTUP_DEBUG: Watchlist button clicked for artist:', artistId, 'watchlist:', watchlistId);
      
      // Call the Python callback
      if (typeof window.pyWatchlistClicked === 'function') {
        try {
          // Call without promises
          console.log('NEXTUP_DEBUG: Calling Python watchlist callback');
          var result = window.pyWatchlistClicked(artistId, watchlistId);
          console.log('NEXTUP_DEBUG: Python watchlist callback completed:', result);
        } catch (err) {
          console.error('NEXTUP_ERROR: Error calling Python watchlist function:', err);
        }
      } else {
        console.warn('NEXTUP_DEBUG: Python watchlist callback not available');
      }
    };
    """
    
    # 6. Set the HTML content and evaluate the JavaScript
    self.html = html_content
    anvil.js.call_js('eval', js_code)