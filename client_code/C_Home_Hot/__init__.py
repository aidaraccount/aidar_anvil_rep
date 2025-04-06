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
    
    # Split data based on source
    self.watchlist_data = [item for item in data if item.get('source', '') == 'watchlist']
    self.notification_data = [item for item in data if item.get('source', '') == 'notification']
    
    self.max_visible_rows = 7
    self.max_expanded_rows = 18  # Maximum number of rows when expanded
    self.watchlist_expanded = False
    self.notification_expanded = False
    
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
      
      window.pyObservesToggleRowsClicked = function() {
        console.log('[DEBUG] Observes toggle rows visibility clicked');
        window._anvilJSCallableObjects.pyObservesToggleRowsClicked.call();
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
      
      // Function to toggle the visibility of rows in Observes table
      window.toggleObservesRowsVisibility = function(expanded) {
        console.log('[DEBUG] Toggling Observes rows visibility, expanded:', expanded);
        
        // Specifically target rows within the observes-container
        var container = document.querySelector('.observes-container');
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
    anvil.js.window.pyObservesToggleRowsClicked = self.handle_observes_toggle_rows_click
    
    # 2. Create tables
    self.create_hot_tables()

  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass
  
  def handle_watchlist_toggle_rows_click(self):
    """
    JavaScript callback for when the show more/show less link is clicked for watchlist table.
    Toggles the visibility of rows beyond the maximum visible rows, up to max_expanded_rows.
    
    Returns:
        bool: True indicating successful completion
    """
    print(f"[DEBUG] Watchlist toggle rows visibility clicked, current state: {self.watchlist_expanded}")
    
    # Toggle expanded state
    self.watchlist_expanded = not self.watchlist_expanded
    
    # Call JavaScript function to toggle row visibility
    anvil.js.call_js('window.toggleWatchlistRowsVisibility', self.watchlist_expanded)
    
    return True
    
  def handle_observes_toggle_rows_click(self):
    """
    JavaScript callback for when the show more/show less link is clicked for observes table.
    Toggles the visibility of rows beyond the maximum visible rows, up to max_expanded_rows.
    
    Returns:
        bool: True indicating successful completion
    """
    print(f"[DEBUG] Observes toggle rows visibility clicked, current state: {self.notification_expanded}")
    
    # Toggle expanded state
    self.notification_expanded = not self.notification_expanded
    
    # Call JavaScript function to toggle row visibility
    anvil.js.call_js('window.toggleObservesRowsVisibility', self.notification_expanded)
    
    return True

  def create_hot_tables(self):
    """
    Creates both the Watchlist and Observes tables with artist data
    """
    # Generate the main container with both tables
    html_content = ""
    
    # Add watchlist table if we have watchlist data
    if self.watchlist_data:
      watchlist_html = self.create_table_html(
        self.watchlist_data, 
        "My Watchlists", 
        "watchlist", 
        self.watchlist_expanded,
        "pyWatchlistToggleRowsClicked"
      )
      html_content += watchlist_html
    
    # Add observes table if we have notification data
    if self.notification_data:
      observes_html = self.create_table_html(
        self.notification_data, 
        "My Observations", 
        "observes", 
        self.notification_expanded,
        "pyObservesToggleRowsClicked"
      )
      html_content += observes_html
      
    # JavaScript for handling clicks and visibility
    js_code = """
    console.log('[DEBUG] Hot tables JavaScript loaded');
    
    // Initialize row visibility for both tables
    if (window.toggleWatchlistRowsVisibility) {
      window.toggleWatchlistRowsVisibility(""" + str(self.watchlist_expanded).lower() + """);
    }
    
    if (window.toggleObservesRowsVisibility) {
      window.toggleObservesRowsVisibility(""" + str(self.notification_expanded).lower() + """);
    }
    """
    
    # Set the HTML content and evaluate the JavaScript
    self.html = html_content
    anvil.js.call_js('eval', js_code)
    
  def create_table_html(self, data, title, container_class, expanded, toggle_function):
    """
    Creates the HTML for a table (either watchlist or observes)
    
    Args:
        data (list): List of artist data dictionaries
        title (str): Title to display in the header
        container_class (str): CSS class for the container
        expanded (bool): Whether the table is expanded
        toggle_function (str): Name of the JavaScript toggle function
        
    Returns:
        str: HTML content for the table
    """
    # 1. Create the main container HTML with the header
    html_content = f"""
    <div class="{container_class}-container hot-container">
      <div class="hot-header">
        <h3>{title}</h3>
      </div>
      <table class="hot-table">
        <tbody id="{container_class}-table-body">
    """
    
    # 2. Generate table rows for each artist
    for i, item in enumerate(data):
      artist_id = item.get('artist_id', '')
      artist_name = item.get('name', 'Unknown')
      artist_pic_url = item.get('artist_picture_url', '')
      watchlist_name = item.get('watchlist_name', 'Unknown')
      tag = item.get('tag', '')  # Metric information
      
      # Create unique row ID
      row_id = f"{container_class}-row-{i}"
      
      # Add 'hidden' class for rows beyond the max_visible_rows
      # If i is greater than max_visible_rows (7) and either
      # 1. We are not expanded OR
      # 2. It's beyond max_expanded_rows (18)
      hidden_class = " hidden" if (i >= self.max_visible_rows and 
                                   (not expanded or i >= self.max_expanded_rows)) else ""
      
      # Add the row for this artist
      html_content += f"""
        <tr id="{row_id}" class="hot-row{hidden_class}">
          <td class="hot-pic-cell">
            <img src="{artist_pic_url}" class="hot-artist-pic" alt="{artist_name}">
          </td>
          <td class="hot-name-cell"><a href="javascript:void(0)" onclick="window.pyArtistNameClicked('{artist_id}')">{artist_name}</a></td>
          <td class="hot-watchlist-cell">on {watchlist_name}</td>
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
      toggle_text = "show less" if expanded else "show more"
      html_content += f"""
      <div class="hot-toggle-container">
        <a href="javascript:void(0)" id="{container_class}-toggle-link" class="hot-toggle-link" onclick="window.{toggle_function}()">{toggle_text}</a>
      </div>
      """
    
    # 5. Complete the container HTML
    html_content += """
    </div>
    <div style="height: 15px;"></div>
    """
    
    return html_content