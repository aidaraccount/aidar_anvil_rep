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
    self.expanded = False
    
    # 1. Register JavaScript callbacks for direct call (not promises)
    anvil.js.call_js(
      "eval",
      """
      window.pyArtistNameClicked = function(artistId) {
        console.log('[DEBUG] Artist name clicked with ID:', artistId);
        location.hash = 'artists?artist_id=' + artistId;
        return true;
      }
      
      window.pyHotToggleRowsClicked = function() {
        console.log('[DEBUG] Hot toggle rows visibility clicked');
        window._anvilJSCallableObjects.pyHotToggleRowsClicked.call();
        return true;
      }
      
      // Function to toggle the visibility of rows in Hot table
      window.toggleHotRowsVisibility = function(expanded) {
        console.log('[DEBUG] Toggling Hot rows visibility, expanded:', expanded);
        
        // Specifically target rows within the hot-container
        var hotContainer = document.querySelector('.hot-container');
        if (hotContainer) {
          var rows = hotContainer.querySelectorAll('.hot-row');
          var toggleLink = hotContainer.querySelector('.hot-toggle-link');
          
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
    anvil.js.window.pyHotToggleRowsClicked = self.handle_toggle_rows_click
    
    # 2. Create Hot table
    self.create_hot_table()

  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass
  
  def handle_toggle_rows_click(self):
    """
    JavaScript callback for when the show more/show less link is clicked.
    Toggles the visibility of rows beyond the maximum visible rows, up to max_expanded_rows.
    
    Returns:
        bool: True indicating successful completion
    """
    print(f"[DEBUG] Hot toggle rows visibility clicked, current state: {self.expanded}")
    
    # Toggle expanded state
    self.expanded = not self.expanded
    
    # Call JavaScript function to toggle row visibility
    anvil.js.call_js('window.toggleHotRowsVisibility', self.expanded)
    
    return True

  def create_hot_table(self):
    """
    Creates the Hot table with artist data
    """
    # 1. Create the main container HTML with the header
    html_content = """
    <div class="hot-container">
      <div class="hot-header">
        <h3>My Watchlists</h3>
      </div>
      <table class="hot-table">
        <tbody id="hot-table-body">
    """
    
    # 2. Generate table rows for each artist
    for i, item in enumerate(self.data):
      artist_id = item.get('artist_id', '')
      artist_name = item.get('name', 'Unknown')
      artist_pic_url = item.get('artist_picture_url', '')
      watchlist_name = item.get('watchlist_name', 'Unknown')
      tag = item.get('tag', '')  # New field containing metric information
      
      # Create unique row ID
      row_id = f"hot-row-{i}"
      
      # Add 'hidden' class for rows beyond the max_visible_rows
      # If i is greater than max_visible_rows (7) and either
      # 1. We are not expanded OR
      # 2. It's beyond max_expanded_rows (18)
      hidden_class = " hidden" if (i >= self.max_visible_rows and 
                                   (not self.expanded or i >= self.max_expanded_rows)) else ""
      
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
    if len(self.data) > self.max_visible_rows:
      toggle_text = "show less" if self.expanded else "show more"
      html_content += f"""
      <div class="hot-toggle-container">
        <a href="javascript:void(0)" id="hot-toggle-link" class="hot-toggle-link" onclick="window.pyHotToggleRowsClicked()">{toggle_text}</a>
      </div>
      """
    
    # 5. Complete the container HTML
    html_content += """
    </div>
    """
    
    # 6. JavaScript for handling clicks and visibility
    js_code = """
    console.log('[DEBUG] Hot table JavaScript loaded');
    
    // Initialize row visibility
    if (window.toggleHotRowsVisibility) {
      window.toggleHotRowsVisibility(""" + str(self.expanded).lower() + """);
    }
    """
    
    # 7. Set the HTML content and evaluate the JavaScript
    self.html = html_content
    anvil.js.call_js('eval', js_code)