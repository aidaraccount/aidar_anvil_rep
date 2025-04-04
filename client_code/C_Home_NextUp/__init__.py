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
    
    # 1. Register JavaScript callback for the artist click
    anvil.js.window.pyArtistClicked = self.handle_artist_click
    
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

  def create_nextup_table(self):
    """
    Creates the NextUp table with artist data
    """
    # 1. Create the main container HTML
    html_content = """
    <div class="nextup-container">
      <table class="nextup-table">
        <tbody id="nextup-table-body">
    """
    
    # 2. Generate table rows for each artist
    for item in self.data:
      artist_id = item.get('artist_id', '')
      artist_name = item.get('name', 'Unknown')
      artist_pic_url = item.get('artist_picture_url', '')
      status = item.get('status', '')
      priority = item.get('priority', '')
      watchlist_id = item.get('watchlist_id', '')
      
      # Status mapping based on the image
      status_display = 'Expl. op.' if status == 'Action required' else 'Build con.' if status == 'Awaiting response' else 'Contact'
      
      # Format priority with first letter capitalized
      priority_display = priority.capitalize() if priority else ''
      
      # Add the row for this artist
      html_content += f"""
        <tr class="nextup-row" onclick="window.artistClicked(event, '{artist_id}')">
          <td class="nextup-pic-cell">
            <img src="{artist_pic_url}" class="nextup-artist-pic" alt="{artist_name}">
          </td>
          <td class="nextup-name-cell">{artist_name}</td>
          <td class="nextup-status-cell">{status_display}</td>
          <td class="nextup-priority-cell">{priority_display}</td>
          <td class="nextup-id-cell">{watchlist_id}</td>
        </tr>
      """
    
    # 3. Complete the HTML
    html_content += """
        </tbody>
      </table>
    </div>
    """
    
    # 4. JavaScript for handling clicks
    js_code = """
    console.log('NextUp table JavaScript loaded');
    
    // Function to handle artist row clicks
    window.artistClicked = function(event, artistId) {
      event.stopPropagation();
      console.log('Artist clicked, ID:', artistId);
      
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
    """
    
    # 5. Set the HTML content and evaluate the JavaScript
    self.html = html_content
    anvil.js.call_js('eval', js_code)