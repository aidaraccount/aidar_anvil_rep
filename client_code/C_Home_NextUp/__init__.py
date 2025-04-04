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


class C_Home_NextUp(C_Home_NextUpTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.data = data
    
    # 1. Register JavaScript callbacks for direct call (not promises)
    anvil.js.call_js('eval', """
      // Handle row removal with pure DOM manipulation to ensure reliability
      window.removeTableRow = function(rowId) {
        console.log('[DEBUG] Pure DOM: Removing row with ID:', rowId);
        var row = document.getElementById(rowId);
        if (row) {
          row.style.transition = 'opacity 0.3s ease';
          row.style.opacity = '0';
          
          setTimeout(function() {
            if (row && row.parentNode) {
              row.parentNode.removeChild(row);
              console.log('[DEBUG] Pure DOM: Row removed successfully');
            }
          }, 300);
        } else {
          console.error('[DEBUG] Pure DOM: Row element not found with ID:', rowId);
        }
      };
    
      window.pyArtistNameClicked = function(artistId) {
        console.log('[DEBUG] Artist name clicked with ID:', artistId);
        location.hash = 'artists?artist_id=' + artistId;
        return true;
      }
      
      window.pyRadioClicked = function(artistId, watchlistId, rowId) {
        console.log('[DEBUG] Calling Python radio click handler with ID:', artistId, 'watchlist:', watchlistId);
        window._anvilJSCallableObjects.pyRadioClicked.call(artistId, watchlistId, rowId);
        
        // Directly trigger row removal through pure DOM manipulation
        window.removeTableRow(rowId);
        return true;
      }
      
      window.pyWatchlistClicked = function(artistId, watchlistId) {
        console.log('[DEBUG] Calling Python watchlist click handler with ID:', artistId, 'watchlist:', watchlistId);
        location.hash = 'watchlist_details?watchlist_id=' + watchlistId + '&artist_id=' + artistId;
        return true;
      }
    """)
    
    # Register the Python functions
    anvil.js.window.pyArtistNameClicked = self.handle_artist_name_click
    anvil.js.window.pyRadioClicked = self.handle_radio_click
    
    # 2. Create NextUp table
    self.create_nextup_table()
    
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass
    
  def handle_artist_name_click(self, artist_id):
    """
    JavaScript callback for when an artist name is clicked.
    Navigates to the artist detail page.
    
    Args:
        artist_id: The ID of the artist to navigate to
    """
    print(f"[DEBUG] Artist name clicked: {artist_id}")
    
    # Navigation is handled in JavaScript by setting location.hash
    return True
    
  def handle_radio_click(self, artist_id, watchlist_id, row_id):
    """
    JavaScript callback for when a radio button is clicked.
    The row will be removed from the table.
    
    Args:
        artist_id: The ID of the artist
        watchlist_id: The ID of the watchlist entry
        row_id: The HTML ID of the row to remove
    """
    print(f"[DEBUG] Radio clicked for artist {artist_id}, watchlist {watchlist_id}, row {row_id}")
    
    # Here you would typically update a database or perform an action
    # anvil.server.call('update_artist_status', artist_id, watchlist_id)
    
    # Row removal is now handled directly in JavaScript
    return True

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
      
      # Add the row for this artist - removing the onclick from the tr element
      html_content += f"""
        <tr id="{row_id}" class="nextup-row">
          <td class="nextup-radio-cell">
            <div class="radio-button" onclick="window.pyRadioClicked('{artist_id}', '{watchlist_id}', '{row_id}')">
              <div class="radio-dot"></div>
            </div>
          </td>
          <td class="nextup-pic-cell">
            <img src="{artist_pic_url}" class="nextup-artist-pic" alt="{artist_name}">
          </td>
          <td class="nextup-name-cell" onclick="window.pyArtistNameClicked('{artist_id}')">{artist_name}</td>
          <td class="nextup-status-cell">{status_display}</td>
          <td class="nextup-priority-cell">{priority_display}</td>
          <td class="nextup-button-cell">
            <button class="icon-button-disabled-small" 
                    data-watchlist-id="{watchlist_id}" 
                    data-artist-id="{artist_id}" 
                    onclick="window.pyWatchlistClicked('{artist_id}', '{watchlist_id}')">
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
    
    # 5. JavaScript for handling clicks - simplified with direct DOM manipulation
    js_code = """
    console.log('[DEBUG] NextUp table JavaScript loaded');
    """
    
    # 6. Set the HTML content and evaluate the JavaScript
    self.html = html_content
    anvil.js.call_js('eval', js_code)