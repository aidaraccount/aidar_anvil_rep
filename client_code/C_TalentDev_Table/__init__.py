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


class C_TalentDev_Table(C_TalentDev_TableTemplate):
  def __init__(self, data=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # 1. Initialize component variables
    self.data = data
    self.is_loading = data is None  # Track loading state
    self.expanded = False
    self.max_visible_rows = 10
    
    # 2. Register JavaScript callbacks
    anvil.js.call_js('eval', """
      window.pyArtistNameClicked = function(artistId) {
        console.log('[DEBUG] Artist name clicked with ID:', artistId);
        location.hash = 'artists?artist_id=' + artistId;
        return true;
      }
      
      // Function to toggle the visibility of rows
      window.toggleRowsVisibility = function(expanded) {
        console.log('[DEBUG] Toggling rows visibility, expanded:', expanded);
        
        var rows = document.querySelectorAll('.talentdev-row');
        var toggleLink = document.getElementById('talentdev-toggle-link');
        
        for (var i = 10; i < rows.length; i++) {
          rows[i].classList.toggle('hidden', !expanded);
        }
        
        if (toggleLink) {
          toggleLink.textContent = expanded ? 'show less' : 'show all';
        }
      }
      
      window.pyToggleRowsClicked = function() {
        console.log('[DEBUG] Toggle rows visibility clicked');
        window._anvilJSCallableObjects.pyToggleRowsClicked.call();
        return true;
      }
    """)
    
    # Register the Python functions
    anvil.js.window.pyToggleRowsClicked = self.handle_toggle_rows_click
    
    # 3. Create Talent Development table
    self.create_table()
    
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass
    
  def handle_toggle_rows_click(self):
    """
    JavaScript callback for when the show all/show less link is clicked.
    Toggles the visibility of rows beyond the maximum visible rows.
    
    Returns:
        bool: True indicating successful completion
    """
    print(f"[DEBUG] Toggle rows visibility clicked, current state: {self.expanded}")
    
    # Toggle expanded state
    self.expanded = not self.expanded
    
    # Call JavaScript function to toggle row visibility
    anvil.js.call_js('window.toggleRowsVisibility', self.expanded)
    
    return True

  def update_data(self, new_data):
    """
    Updates the component with new data and refreshes the display
    
    Parameters:
        new_data (list): The new data to display
    """
    self.data = new_data
    self.is_loading = False
    
    # Recreate the table with the new data
    self.create_table()
    
    return True

  def create_table(self):
    """
    Creates the Talent Development table with artist data
    """
    # 1. Create the main container HTML
    html_content = """
    <div class="talentdev-container">
      <table class="talentdev-table">
        <thead>
          <tr class="talentdev-header-row">
            <th class="talentdev-pic-header"></th>
            <th class="talentdev-name-header">Artist</th>
            <th class="talentdev-date-header">Last Release</th>
          </tr>
        </thead>
        <tbody id="talentdev-table-body">
    """
    
    # 2. Check if data is loading or empty
    if self.is_loading:
      # Loading state message
      html_content += """
        <tr class="talentdev-row talentdev-status-row">
          <td colspan="3" class="talentdev-status-cell">
            <div class="talentdev-status-message talentdev-loading-message">Loading data...</div>
          </td>
        </tr>
      """
    elif not self.data:
      # No data message
      html_content += """
        <tr class="talentdev-row talentdev-status-row">
          <td colspan="3" class="talentdev-status-cell">
            <div class="talentdev-status-message talentdev-empty-message">No artists found</div>
          </td>
        </tr>
      """
    else:
      # 3. Generate table rows for each artist
      for i, item in enumerate(self.data):
        artist_id = item.get('artist_id', '')
        artist_name = item.get('name', 'Unknown')
        artist_pic_url = item.get('artist_picture_url', '')
        last_release_date = item.get('last_release_date', '')
        
        # Create unique row ID
        row_id = f"talentdev-row-{i}"
        
        # Add 'hidden' class for rows beyond the max_visible_rows if not expanded
        hidden_class = "" if i < self.max_visible_rows or self.expanded else " hidden"
        
        # Add the row for this artist
        html_content += f"""
          <tr id="{row_id}" class="talentdev-row{hidden_class}">
            <td class="talentdev-pic-cell">
              <img src="{artist_pic_url}" class="talentdev-artist-pic" alt="{artist_name}">
            </td>
            <td class="talentdev-name-cell">
              <a href="javascript:void(0)" onclick="window.pyArtistNameClicked('{artist_id}')">{artist_name}</a>
            </td>
            <td class="talentdev-date-cell">{last_release_date}</td>
          </tr>
        """
    
    # 4. Complete the HTML for the table
    html_content += """
        </tbody>
      </table>
    """
    
    # 5. Add the toggle link if there are more than max_visible_rows entries and not loading/empty
    if not self.is_loading and self.data and len(self.data) > self.max_visible_rows:
      toggle_text = "show less" if self.expanded else "show all"
      html_content += f"""
      <div class="talentdev-toggle-container">
        <a href="javascript:void(0)" id="talentdev-toggle-link" class="talentdev-toggle-link" onclick="window.pyToggleRowsClicked()">{toggle_text}</a>
      </div>
      """
    
    # 6. Complete the container HTML
    html_content += """
    </div>
    """
    
    # 7. JavaScript for handling clicks
    js_code = """
    console.log('[DEBUG] Talent Development table JavaScript loaded');
    
    // Initialize row visibility
    if (window.toggleRowsVisibility) {
      window.toggleRowsVisibility(""" + str(self.expanded).lower() + """);
    }
    """
    
    # 8. Set the HTML content and evaluate the JavaScript
    self.html = html_content
    anvil.js.call_js('eval', js_code)
