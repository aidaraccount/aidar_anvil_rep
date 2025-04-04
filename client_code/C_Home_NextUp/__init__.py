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
    
    # 1. Create custom HTML table to display next up items
    self.create_nextup_table()
    
  def create_nextup_table(self):
    """
    Creates a custom HTML table to display the next up artists with their pictures and names.
    """
    # 1.1 Clear any existing content
    self.nextup_panel.clear()
    
    # 1.2 Create the HTML component with the table
    html_template = """
    <div class="nextup-container">
      <table class="nextup-table">
        <tbody id="nextup-table-body">
        </tbody>
      </table>
    </div>
    """
    
    # 1.3 Add the HTML component to the panel
    html_component = HTML(html=html_template)
    self.nextup_panel.add_component(html_component)
    
    # 1.4 Create JavaScript to populate the table
    js_code = """
    function populateNextUpTable(data) {
      const tableBody = document.getElementById('nextup-table-body');
      
      // Clear existing content
      tableBody.innerHTML = '';
      
      // Add rows for each artist
      data.forEach(item => {
        const row = document.createElement('tr');
        row.className = 'nextup-row';
        row.setAttribute('data-artist-id', item.artist_id);
        
        // Artist picture cell
        const picCell = document.createElement('td');
        picCell.className = 'nextup-pic-cell';
        const img = document.createElement('img');
        img.src = item.artist_picture_url;
        img.alt = item.name;
        img.className = 'nextup-artist-pic';
        picCell.appendChild(img);
        
        // Artist name cell
        const nameCell = document.createElement('td');
        nameCell.className = 'nextup-name-cell';
        nameCell.textContent = item.name;
        
        // Status cell
        const statusCell = document.createElement('td');
        statusCell.className = 'nextup-status-cell';
        statusCell.textContent = item.status === 'Action required' ? 'Expl. op.' : 
                               (item.status === 'Awaiting response' ? 'Build con.' : 'Contact');
        
        // Priority cell
        const priorityCell = document.createElement('td');
        priorityCell.className = 'nextup-priority-cell';
        priorityCell.textContent = item.priority.charAt(0).toUpperCase() + item.priority.slice(1);
        
        // ID cell
        const idCell = document.createElement('td');
        idCell.className = 'nextup-id-cell';
        idCell.textContent = item.watchlist_id;
        
        // Add cells to row
        row.appendChild(picCell);
        row.appendChild(nameCell);
        row.appendChild(statusCell);
        row.appendChild(priorityCell);
        row.appendChild(idCell);
        
        // Add click handler
        row.addEventListener('click', function() {
          console.log('Clicked on artist:', item.name, 'ID:', item.artist_id);
          // Call Python click handler
          _anvil.call('nextup_row_click', item);
        });
        
        // Add row to table
        tableBody.appendChild(row);
      });
    }
    """
    
    # 1.5 Execute the JavaScript and populate the table
    anvil.js.call_js('eval', js_code)
    anvil.js.call_js('populateNextUpTable', self.data)
    
  def nextup_row_click(self, item, **event_args):
    """
    Handle clicks on the table rows
    """
    # Navigate to the artist's page using the nav.click_button function
    click_button('artist_view', {'artist_id': item['artist_id']})