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
      window.pyArtistClicked = function(artistId) {
        console.log('[DEBUG] Calling Python artist click handler with ID:', artistId);
        
        // Navigate directly to artist page
        console.log('[DEBUG] Navigating to artist page:', artistId);
        window.location.hash = 'artists?artist_id=' + artistId;
        
        // Also call Python handler for any server-side logic
        window._anvilJSCallableObjects.pyArtistClicked.call(artistId);
        return true;
      }
      
      window.pyRadioClicked = function(artistId, watchlistId, rowId) {
        console.log('[DEBUG] Calling Python radio click handler with ID:', artistId, 'watchlist:', watchlistId);
        window._anvilJSCallableObjects.pyRadioClicked.call(artistId, watchlistId, rowId);
        
        // Handle row removal directly in JS for reliability
        console.log('[DEBUG] Removing row with ID:', rowId);
        var row = document.getElementById(rowId);
        console.log('[DEBUG] Found row element:', row);
        
        if (row) {
          // Set display property directly after a short delay
          try {
            // Apply transition and opacity first
            row.style.transition = 'opacity 0.3s ease';
            row.style.opacity = '0';
            console.log('[DEBUG] Set opacity to 0');
            
            // Then remove after transition completes
            setTimeout(function() {
              try {
                if (row && row.parentNode) {
                  row.parentNode.removeChild(row);
                  console.log('[DEBUG] Row removed successfully');
                } else {
                  console.log('[DEBUG] Row or parent not found in setTimeout');
                }
              } catch (err) {
                console.error('[DEBUG] Error removing row in setTimeout:', err);
              }
            }, 300);
          } catch (err) {
            console.error('[DEBUG] Error handling row removal:', err);
          }
        } else {
          console.error('[DEBUG] Row not found with ID:', rowId);
        }
        
        return true;
      }
      
      window.pyWatchlistClicked = function(artistId, watchlistId) {
        console.log('[DEBUG] Calling Python watchlist click handler with ID:', artistId, 'watchlist:', watchlistId);
        window._anvilJSCallableObjects.pyWatchlistClicked.call(artistId, watchlistId);
        return true;
      }
    """)
    
    # Register the Python functions
    anvil.js.window.pyArtistClicked = self.handle_artist_click
    anvil.js.window.pyRadioClicked = self.handle_radio_click
    anvil.js.window.pyWatchlistClicked = self.handle_watchlist_click
    
    # 2. Create NextUp table
    self.create_nextup_table()
    
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass
    
  def handle_artist_click(self, artist_id):
    """
    JavaScript callback for when an artist name is clicked.
    
    Args:
        artist_id: The ID of the artist to navigate to
    """
    print(f"[DEBUG] Artist clicked: {artist_id}")
    
    # Navigation is now handled directly in JavaScript with hash routing
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
    
  def handle_watchlist_click(self, artist_id, watchlist_id):
    """
    JavaScript callback for when the watchlist icon button is clicked.
    Redirects to the watchlist details page.
    
    Args:
        artist_id: The ID of the artist
        watchlist_id: The ID of the watchlist entry
    """
    print(f"[DEBUG] Watchlist button clicked for artist {artist_id}, watchlist {watchlist_id}")
    
    # Navigation is now handled directly in JavaScript with hash routing
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
      
      # Add the row for this artist - removed the onclick from the row
      html_content += f"""
        <tr id="{row_id}" class="nextup-row" style="transition: opacity 0.3s ease;">
          <td class="nextup-radio-cell">
            <div class="radio-button" onclick="window.radioClicked(event, '{artist_id}', '{watchlist_id}', '{row_id}')">
              <div class="radio-dot"></div>
            </div>
          </td>
          <td class="nextup-pic-cell">
            <img src="{artist_pic_url}" class="nextup-artist-pic" alt="{artist_name}">
          </td>
          <td class="nextup-name-cell" onclick="window.artistClicked(event, '{artist_id}')">
            {artist_name}
          </td>
          <td class="nextup-status-cell">
            {status_display}
          </td>
          <td class="nextup-priority-cell">
            {priority_display}
          </td>
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
    console.log('[DEBUG] NextUp table JavaScript loaded');
    
    // Function to handle artist name cell clicks
    window.artistClicked = function(event, artistId) {
      event.stopPropagation();
      console.log('[DEBUG] Artist name clicked, ID:', artistId);
      
      // Simple direct call instead of promise
      try {
        window.pyArtistClicked(artistId);
      } catch (err) {
        console.error('[DEBUG] Error calling Python artist function:', err);
      }
    };
    
    // Function to handle radio button clicks
    window.radioClicked = function(event, artistId, watchlistId, rowId) {
      event.stopPropagation();
      console.log('[DEBUG] Radio clicked for artist:', artistId, 'watchlist:', watchlistId);
      
      // Simple direct call instead of promise
      try {
        window.pyRadioClicked(artistId, watchlistId, rowId);
      } catch (err) {
        console.error('[DEBUG] Error calling Python radio function:', err);
      }
    };
    
    // Function to handle watchlist icon button clicks
    window.watchlistClicked = function(event, artistId, watchlistId) {
      event.stopPropagation();
      console.log('[DEBUG] Watchlist button clicked for artist:', artistId, 'watchlist:', watchlistId);
      
      // Simple direct call instead of promise
      try {
        window.pyWatchlistClicked(artistId, watchlistId);
      } catch (err) {
        console.error('[DEBUG] Error calling Python watchlist function:', err);
      }
    };
    """
    
    # 6. Set the HTML content and evaluate the JavaScript
    self.html = html_content
    anvil.js.call_js('eval', js_code)