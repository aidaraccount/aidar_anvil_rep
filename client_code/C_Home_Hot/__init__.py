from ._anvil_designer import C_Home_HotTemplate
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


class C_Home_Hot(C_Home_HotTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    self.data = data
    self.max_visible_rows = 7
    self.max_expanded_rows = 18  # Maximum number of rows when expanded
    self.expanded_watchlist = False
    self.expanded_observations = False
    
    # 1. Register JavaScript callbacks for direct call (not promises)
    anvil.js.call_js(
      "eval",
      """
      window.pyArtistNameClicked = function(artistId) {
        console.log('[DEBUG] Artist name clicked with ID:', artistId);
        location.hash = 'artists?artist_id=' + artistId;
        return true;
      }
      
      window.pyWatchlistToggleRowsClicked = function() {
        console.log('[DEBUG] Watchlist toggle rows visibility clicked');
        window._anvilJSCallableObjects.pyWatchlistToggleRowsClicked.call();
        return true;
      }
      
      window.pyObservationsToggleRowsClicked = function() {
        console.log('[DEBUG] Observations toggle rows visibility clicked');
        window._anvilJSCallableObjects.pyObservationsToggleRowsClicked.call();
        return true;
      }
      
      // Function to toggle the visibility of rows in Watchlist table
      window.toggleWatchlistRowsVisibility = function(expanded) {
        console.log('[DEBUG] Toggling Watchlist rows visibility, expanded:', expanded);
        
        // Specifically target rows within the watchlist-container
        var container = document.querySelector('.watchlist-container');
        if (container) {
          var rows = container.querySelectorAll('.hot-row');
          var toggleLink = container.querySelector('.hot-toggle-link');
          
          // Show rows 7-18 when expanded, hide when collapsed
          for (var i = 7; i < rows.length; i++) {
            // If expanded, show rows up to max_expanded_rows (18)
            // If collapsed, hide all rows beyond max_visible_rows (7)
            var shouldHide = !expanded || (i >= 18);
            rows[i].classList.toggle('hidden', shouldHide);
          }
          
          if (toggleLink) {
            toggleLink.textContent = expanded ? 'show less' : 'show more';
          }
        }
      }
      
      // Function to toggle the visibility of rows in Observations table
      window.toggleObservationsRowsVisibility = function(expanded) {
        console.log('[DEBUG] Toggling Observations rows visibility, expanded:', expanded);
        
        // Specifically target rows within the observations-container
        var container = document.querySelector('.observations-container');
        if (container) {
          var rows = container.querySelectorAll('.hot-row');
          var toggleLink = container.querySelector('.hot-toggle-link');
          
          // Show rows 7-18 when expanded, hide when collapsed
          for (var i = 7; i < rows.length; i++) {
            // If expanded, show rows up to max_expanded_rows (18)
            // If collapsed, hide all rows beyond max_visible_rows (7)
            var shouldHide = !expanded || (i >= 18);
            rows[i].classList.toggle('hidden', shouldHide);
          }
          
          if (toggleLink) {
            toggleLink.textContent = expanded ? 'show less' : 'show more';
          }
        }
      }
      """,
    )

    # Register the Python functions
    anvil.js.window.pyWatchlistToggleRowsClicked = self.handle_watchlist_toggle_rows_click
    anvil.js.window.pyObservationsToggleRowsClicked = self.handle_observations_toggle_rows_click
    
    # 2. Create tables
    self.create_hot_tables()

  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass
  
  def handle_watchlist_toggle_rows_click(self):
    """
    JavaScript callback for when the show more/show less link is clicked in the watchlist section.
    Toggles the visibility of rows beyond the maximum visible rows, up to max_expanded_rows.
    
    Returns:
        bool: True indicating successful completion
    """
    print(f"[DEBUG] Watchlist toggle rows visibility clicked, current state: {self.expanded_watchlist}")
    
    # Toggle expanded state
    self.expanded_watchlist = not self.expanded_watchlist
    
    # Call JavaScript function to toggle row visibility
    anvil.js.call_js('window.toggleWatchlistRowsVisibility', self.expanded_watchlist)
    
    return True

  def handle_observations_toggle_rows_click(self):
    """
    JavaScript callback for when the show more/show less link is clicked in the observations section.
    Toggles the visibility of rows beyond the maximum visible rows, up to max_expanded_rows.
    
    Returns:
        bool: True indicating successful completion
    """
    print(f"[DEBUG] Observations toggle rows visibility clicked, current state: {self.expanded_observations}")
    
    # Toggle expanded state
    self.expanded_observations = not self.expanded_observations
    
    # Call JavaScript function to toggle row visibility
    anvil.js.call_js('window.toggleObservationsRowsVisibility', self.expanded_observations)
    
    return True

  def create_hot_tables(self):
    """
    Creates the Hot tables with artist data for Watchlists and Observations
    """
    # Filter data by source
    watchlist_data = [item for item in self.data if item.get('source', '') == 'watchlist']
    observations_data = [item for item in self.data if item.get('source', '') == 'notification']
    
    # Create HTML content for both tables
    html_content = self.create_watchlist_table(watchlist_data)
    html_content += self.create_observations_table(observations_data)
    
    # Set the HTML content
    self.html = html_content
    
    # Initialize row visibility
    js_code = """
    console.log('[DEBUG] Hot tables JavaScript loaded');
    
    // Initialize row visibility for Watchlist
    if (window.toggleWatchlistRowsVisibility) {
      window.toggleWatchlistRowsVisibility(""" + str(self.expanded_watchlist).lower() + """);
    }
    
    // Initialize row visibility for Observations
    if (window.toggleObservationsRowsVisibility) {
      window.toggleObservationsRowsVisibility(""" + str(self.expanded_observations).lower() + """);
    }
    """
    
    # Evaluate the JavaScript
    anvil.js.call_js('eval', js_code)

  def create_watchlist_table(self, data):
    """
    Creates the Watchlist table HTML
    
    Args:
        data: List of artist data from watchlists
        
    Returns:
        str: HTML content for the watchlist table
    """
    # 1. Create the main container HTML with the header
    html_content = """
    <div class="hot-container watchlist-container">
      <div class="hot-header">
        <h3>My Watchlists</h3>
      </div>
      <table class="hot-table">
        <tbody id="watchlist-table-body">
    """
    
    # 2. Generate table rows for each artist
    for i, item in enumerate(data):
      artist_id = item.get('artist_id', '')
      artist_name = item.get('name', 'Unknown')
      artist_pic_url = item.get('artist_picture_url', '')
      list_name = item.get('list_name', 'Unknown')
      tag = item.get('tag', '')  # Metric information
      
      # Create unique row ID
      row_id = f"watchlist-row-{i}"
      
      # Add 'hidden' class for rows beyond the max_visible_rows
      hidden_class = " hidden" if (i >= self.max_visible_rows and 
                                   (not self.expanded_watchlist or i >= self.max_expanded_rows)) else ""
      
      # Add the row for this artist
      html_content += f"""
        <tr id="{row_id}" class="hot-row{hidden_class}">
          <td class="hot-pic-cell">
            <img src="{artist_pic_url}" class="hot-artist-pic" alt="{artist_name}">
          </td>
          <td class="hot-name-cell"><a href="javascript:void(0)" onclick="window.pyArtistNameClicked('{artist_id}')">{artist_name}</a></td>
          <td class="hot-watchlist-cell">on {list_name}</td>
          <td class="hot-release-cell">
            <div class="hot-release-box">
              <span class="hot-release-time">{tag}</span>
            </div>
          </td>
        </tr>
      """
    
    # 3. Complete the HTML for the table
    html_content += """
        </tbody>
      </table>
    """
    
    # 4. Add the toggle link if there are more than max_visible_rows entries
    if len(data) > self.max_visible_rows:
      toggle_text = "show less" if self.expanded_watchlist else "show more"
      html_content += f"""
      <div class="hot-toggle-container">
        <a href="javascript:void(0)" id="watchlist-toggle-link" class="hot-toggle-link" onclick="window.pyWatchlistToggleRowsClicked()">{toggle_text}</a>
      </div>
      """
    
    # 5. Complete the container HTML
    html_content += """
    </div>
    """
    
    return html_content

  def create_observations_table(self, data):
    """
    Creates the Observations table HTML
    
    Args:
        data: List of artist data from notifications
        
    Returns:
        str: HTML content for the observations table
    """
    # 1. Create the main container HTML with the header
    html_content = """
    <div class="hot-container observations-container">
      <div class="hot-header">
        <h3>My Observations</h3>
      </div>
      <table class="hot-table">
        <tbody id="observations-table-body">
    """
    
    # 2. Generate table rows for each artist
    for i, item in enumerate(data):
      artist_id = item.get('artist_id', '')
      artist_name = item.get('name', 'Unknown')
      artist_pic_url = item.get('artist_picture_url', '')
      list_name = item.get('list_name', 'Unknown')
      tag = item.get('tag', '')  # Metric information
      
      # Create unique row ID
      row_id = f"observations-row-{i}"
      
      # Add 'hidden' class for rows beyond the max_visible_rows
      hidden_class = " hidden" if (i >= self.max_visible_rows and 
                                   (not self.expanded_observations or i >= self.max_expanded_rows)) else ""
      
      # Add the row for this artist
      html_content += f"""
        <tr id="{row_id}" class="hot-row{hidden_class}">
          <td class="hot-pic-cell">
            <img src="{artist_pic_url}" class="hot-artist-pic" alt="{artist_name}">
          </td>
          <td class="hot-name-cell"><a href="javascript:void(0)" onclick="window.pyArtistNameClicked('{artist_id}')">{artist_name}</a></td>
          <td class="hot-watchlist-cell">on {list_name}</td>
          <td class="hot-release-cell">
            <div class="hot-release-box">
              <span class="hot-release-time">{tag}</span>
            </div>
          </td>
        </tr>
      """
    
    # 3. Complete the HTML for the table
    html_content += """
        </tbody>
      </table>
    """
    
    # 4. Add the toggle link if there are more than max_visible_rows entries
    if len(data) > self.max_visible_rows:
      toggle_text = "show less" if self.expanded_observations else "show more"
      html_content += f"""
      <div class="hot-toggle-container">
        <a href="javascript:void(0)" id="observations-toggle-link" class="hot-toggle-link" onclick="window.pyObservationsToggleRowsClicked()">{toggle_text}</a>
      </div>
      """
    
    # 5. Complete the container HTML
    html_content += """
    </div>
    """
    
    return html_content