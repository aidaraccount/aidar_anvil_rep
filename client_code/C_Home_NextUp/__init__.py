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
    
    # 1. Register JavaScript callbacks
    anvil.js.window.pyArtistClicked = self.handle_artist_click
    anvil.js.window.pyToggleClicked = self.handle_toggle_click
    
    # 2. Create NextUp table
    self.create_nextup_table()
    
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass
    
  def handle_artist_click(self, artist_id):
    """
    JavaScript callback for when an artist row is clicked.
    
    Args:
        artist_id: The ID of the artist to navigate to
    """
    # Navigate to the artist's page using the nav.click_button function
    click_button('artist_view', {'artist_id': artist_id})
    return {"success": True, "artist_id": artist_id}
    
  def handle_toggle_click(self, artist_id, watchlist_id, is_checked):
    """
    JavaScript callback for when a toggle switch is clicked.
    
    Args:
        artist_id: The ID of the artist
        watchlist_id: The ID of the watchlist entry
        is_checked: Boolean indicating if the toggle is checked
    """
    print(f"Toggle clicked for artist {artist_id}, watchlist {watchlist_id}, state: {is_checked}")
    # Here you would typically update a database or perform an action
    # anvil.server.call('update_artist_status', artist_id, watchlist_id, is_checked)
    return {"success": True, "artist_id": artist_id, "watchlist_id": watchlist_id, "is_checked": is_checked}

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
    for item in self.data:
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
      
      # Default toggle state based on priority (example logic)
      is_checked = 'checked' if priority == 'high' or priority == 'very high' else ''
      
      # Add the row for this artist
      html_content += f"""
        <tr class="nextup-row" onclick="window.artistClicked(event, '{artist_id}')">
          <td class="nextup-toggle-cell">
            <label class="toggle-switch">
              <input type="checkbox" {is_checked} onclick="window.toggleClicked(event, '{artist_id}', '{watchlist_id}', this.checked)">
              <span class="toggle-slider"></span>
            </label>
          </td>
          <td class="nextup-pic-cell">
            <img src="{artist_pic_url}" class="nextup-artist-pic" alt="{artist_name}">
          </td>
          <td class="nextup-name-cell">{artist_name}</td>
          <td class="nextup-status-cell">{status_display}</td>
          <td class="nextup-priority-cell">{priority_display}</td>
          <td class="nextup-button-cell">
            <button class="icon-button-disabled-small" data-watchlist-id="{watchlist_id}">
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
    console.log('NextUp table JavaScript loaded');
    
    // Function to handle artist row clicks
    window.artistClicked = function(event, artistId) {
      event.stopPropagation();
      console.log('Artist clicked, ID:', artistId);
      
      // Ignore clicks on the button or toggle
      if (event.target.closest('.icon-button-disabled-small') || 
          event.target.closest('i.fa') ||
          event.target.closest('.toggle-switch')) {
        console.log('Button or toggle clicked, stopping propagation');
        return;
      }
      
      // Call the Python callback
      if (typeof window.pyArtistClicked === 'function') {
        try {
          window.pyArtistClicked(artistId).then(function(result) {
            console.log('Python callback completed:', result);
          }).catch(function(error) {
            console.error('Error in Python callback:', error);
          });
        } catch (err) {
          console.error('Error calling Python function:', err);
        }
      } else {
        console.warn('Python callback not available');
      }
    };
    
    // Function to handle toggle switch clicks
    window.toggleClicked = function(event, artistId, watchlistId, isChecked) {
      event.stopPropagation();
      console.log('Toggle clicked for artist:', artistId, 'watchlist:', watchlistId, 'state:', isChecked);
      
      // Add shimmering effect animation
      const toggleSlider = event.target.nextElementSibling;
      toggleSlider.style.transition = '.5s';
      
      // Call the Python callback
      if (typeof window.pyToggleClicked === 'function') {
        try {
          window.pyToggleClicked(artistId, watchlistId, isChecked).then(function(result) {
            console.log('Python toggle callback completed:', result);
          }).catch(function(error) {
            console.error('Error in Python toggle callback:', error);
          });
        } catch (err) {
          console.error('Error calling Python toggle function:', err);
        }
      } else {
        console.warn('Python toggle callback not available');
      }
    };
    """
    
    # 6. Set the HTML content and evaluate the JavaScript
    self.html = html_content
    anvil.js.call_js('eval', js_code)