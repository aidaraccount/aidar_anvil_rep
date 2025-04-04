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
    self.max_visible_rows = 7
    self.expanded = False
    
    # 1. Register JavaScript callbacks for direct call (not promises)
    anvil.js.call_js('eval', """
      window.pyArtistNameClicked = function(artistId) {
        console.log('[DEBUG] Artist name clicked with ID:', artistId);
        location.hash = 'artists?artist_id=' + artistId;
        return true;
      }
      
      window.pyRadioClicked = function(artistId, watchlistId, rowId) {
        console.log('[DEBUG] Calling Python radio click handler for removal with ID:', artistId, 'watchlist:', watchlistId);
        // Extract the row index from the ID
        var rowIndex = rowId.split('-').pop();
        window._anvilJSCallableObjects.pyRadioClicked.call(artistId, watchlistId, rowIndex);
        return true;
      }
      
      window.pyWatchlistClicked = function(artistId, watchlistId) {
        console.log('[DEBUG] Calling Python watchlist click handler with ID:', artistId, 'watchlist:', watchlistId);
        location.hash = 'watchlist_details?watchlist_id=' + watchlistId + '&artist_id=' + artistId;
        return true;
      }
      
      window.pyToggleRowsClicked = function() {
        console.log('[DEBUG] Toggle rows visibility clicked');
        window._anvilJSCallableObjects.pyToggleRowsClicked.call();
        return true;
      }
      
      // Function to toggle the visibility of rows
      window.toggleRowsVisibility = function(expanded) {
        console.log('[DEBUG] Toggling rows visibility, expanded:', expanded);
        
        var rows = document.querySelectorAll('.nextup-row');
        var toggleLink = document.getElementById('nextup-toggle-link');
        
        for (var i = 7; i < rows.length; i++) {
          rows[i].classList.toggle('hidden', !expanded);
        }
        
        if (toggleLink) {
          toggleLink.textContent = expanded ? 'show less' : 'show all';
        }
      }
    """)
    
    # Register the Python functions
    anvil.js.window.pyRadioClicked = self.handle_radio_click
    anvil.js.window.pyToggleRowsClicked = self.handle_toggle_rows_click
    
    # 2. Create NextUp table
    self.create_nextup_table()
    
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass
  
  def handle_toggle_rows_click(self):
    """
    JavaScript callback for when the show all/show less link is clicked.
    Toggles the visibility of rows beyond the first three.
    
    Returns:
        bool: True indicating successful completion
    """
    print(f"[DEBUG] Toggle rows visibility clicked, current state: {self.expanded}")
    
    # Toggle expanded state
    self.expanded = not self.expanded
    
    # Call JavaScript function to toggle row visibility
    anvil.js.call_js('window.toggleRowsVisibility', self.expanded)
    
    return True
    
  def handle_radio_click(self, artist_id, watchlist_id, row_index):
    """
    JavaScript callback for when a radio button is clicked.
    The row will be removed from the data and the table will be refreshed.
    
    Args:
        artist_id: The ID of the artist
        watchlist_id: The ID of the watchlist entry
        row_index: The index of the row in the data array
    
    Returns:
        bool: True indicating successful completion
    """
    print(f"[DEBUG] Radio clicked for artist {artist_id}, watchlist {watchlist_id}, index {row_index}")
    
    try:
      # Convert row_index to integer
      index = int(row_index)
      
      # Remove the item from the data array if index is valid
      if 0 <= index < len(self.data):
        removed_item = self.data.pop(index)
        print(f"[DEBUG] Removed item from data: {removed_item}")
        
        # Here you would typically update a database or perform a server action
        # anvil.server.call('update_artist_status', artist_id, watchlist_id)
        
        # Regenerate the table with the updated data
        self.create_nextup_table()
        print(f"[DEBUG] Table refreshed with {len(self.data)} items remaining")
      else:
        print(f"[DEBUG] Invalid row index: {index}, data length: {len(self.data)}")
    except Exception as e:
      print(f"[DEBUG] Error removing item: {str(e)}")
    
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
      
      # Add 'hidden' class for rows beyond the max_visible_rows if not expanded
      hidden_class = "" if i < self.max_visible_rows or self.expanded else " hidden"
      
      # Add the row for this artist
      html_content += f"""
        <tr id="{row_id}" class="nextup-row{hidden_class}">
          <td class="nextup-radio-cell">
            <div class="radio-button" onclick="window.pyRadioClicked('{artist_id}', '{watchlist_id}', '{i}')">
              <div class="radio-dot"></div>
            </div>
          </td>
          <td class="nextup-pic-cell">
            <img src="{artist_pic_url}" class="nextup-artist-pic" alt="{artist_name}">
          </td>
          <td class="nextup-name-cell"><a href="javascript:void(0)" onclick="window.pyArtistNameClicked('{artist_id}')">{artist_name}</a></td>
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
    
    # 4. Complete the HTML for the table
    html_content += """
        </tbody>
      </table>
    """
    
    # 5. Add the toggle link if there are more than max_visible_rows entries
    if len(self.data) > self.max_visible_rows:
      toggle_text = "show less" if self.expanded else "show all"
      html_content += f"""
      <div class="nextup-toggle-container">
        <a href="javascript:void(0)" id="nextup-toggle-link" class="nextup-toggle-link" onclick="window.pyToggleRowsClicked()">{toggle_text}</a>
      </div>
      """
    
    # 6. Complete the container HTML
    html_content += """
    </div>
    """
    
    # 7. JavaScript for handling clicks
    js_code = """
    console.log('[DEBUG] NextUp table JavaScript loaded');
    
    // Initialize row visibility
    if (window.toggleRowsVisibility) {
      window.toggleRowsVisibility(""" + str(self.expanded).lower() + """);
    }
    """
    
    # 8. Set the HTML content and evaluate the JavaScript
    self.html = html_content
    anvil.js.call_js('eval', js_code)