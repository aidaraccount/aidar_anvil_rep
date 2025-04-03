from ._anvil_designer import C_Home_AgentsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


class C_Home_Agents(C_Home_AgentsTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # Print data type for debugging
    print(f"Data type: {type(data)}")
    
    # Convert string data to list of dictionaries if needed
    if isinstance(data, str):
      try:
        data = json.loads(data)
        print("Successfully parsed data as JSON")
      except json.JSONDecodeError:
        print("Failed to parse data as JSON")
    
    if data and isinstance(data, list):
      print(f"First item type: {type(data[0])}")
      
    self.setup_slider(data)
    
  def setup_slider(self, data):
    """
    Sets up the slider component with model boxes.
    
    Args:
        data: List of model data to display in the slider. Can be a list of dictionaries
             or a JSON string representation of such a list.
    """
    # Generate HTML for each model box
    model_boxes_html = ""
    
    # Ensure data is properly formatted
    if isinstance(data, str):
      try:
        data = json.loads(data)
      except json.JSONDecodeError:
        print("Could not parse data as JSON in setup_slider")
    
    if isinstance(data, list):
      print(f"Processing {len(data)} models for slider")
      for model in data:
        if isinstance(model, dict):
          model_id = model.get('model_id', '')
          model_name = model.get('model_name', 'Unknown Model')
          
          model_boxes_html += f"""
            <div class="model-box" data-model-id="{model_id}">
              <div class="model-name">{model_name}</div>
            </div>
          """
        else:
          # Handle string or other non-dict items if needed
          model_boxes_html += f"""
            <div class="model-box">
              <div class="model-name">{str(model)}</div>
            </div>
          """
    else:
      print(f"Data is not a list, type: {type(data)}")
      if isinstance(data, str):
        # If it's still a string at this point, show it as a single box
        model_boxes_html = f"""
          <div class="model-box">
            <div class="model-name">Error: Could not parse data</div>
          </div>
        """
    
    # JavaScript for the slider functionality
    js_code = """
      document.addEventListener('DOMContentLoaded', function() {
        // Track slider position
        let position = 0;
        const track = document.querySelector('.slider-track');
        const boxes = document.querySelectorAll('.model-box');
        const leftArrow = document.querySelector('.slider-arrow.left');
        const rightArrow = document.querySelector('.slider-arrow.right');
        
        if (!track || !boxes.length || !leftArrow || !rightArrow) {
          console.error('Slider elements not found');
          return;
        }
        
        console.log('Slider initialized with ' + boxes.length + ' boxes');
        
        // Calculate how many items can fit in the view
        function calculateVisibleBoxes() {
          const container = document.querySelector('.slider-container');
          if (!container || boxes.length === 0) return 0;
          const boxWidth = boxes[0].offsetWidth + parseInt(getComputedStyle(boxes[0]).marginRight);
          return Math.floor(container.offsetWidth / boxWidth);
        }
        
        // Handle left arrow click
        function slideLeft() {
          console.log('Slide left clicked, current position: ' + position);
          if (position > 0) {
            position--;
            updateSliderPosition();
          }
        }
        
        // Handle right arrow click
        function slideRight() {
          console.log('Slide right clicked, current position: ' + position);
          const visibleBoxes = calculateVisibleBoxes();
          if (position + visibleBoxes < boxes.length) {
            position++;
            updateSliderPosition();
          }
        }
        
        // Update the track position
        function updateSliderPosition() {
          if (boxes.length === 0) return;
          const boxWidth = boxes[0].offsetWidth + parseInt(getComputedStyle(boxes[0]).marginRight);
          track.style.transform = `translateX(-${position * boxWidth}px)`;
          console.log('Updated slider position to: ' + position);
        }
        
        // Add event listeners to arrows
        leftArrow.addEventListener('click', slideLeft);
        rightArrow.addEventListener('click', slideRight);
        
        // Initial positioning
        updateSliderPosition();
        
        // Handle window resize
        window.addEventListener('resize', function() {
          // Reset position if we've moved too far to the right
          const visibleBoxes = calculateVisibleBoxes();
          if (position + visibleBoxes > boxes.length) {
            position = Math.max(0, boxes.length - visibleBoxes);
            updateSliderPosition();
          }
        });
      });
    """
    
    # Combine everything into the final HTML
    self.html = f"""
    <div class="agents-slider">
      <div class="slider-container">
        <div class="slider-arrow left">&#10094;</div>
        <div class="slider-track">
          {model_boxes_html}
        </div>
        <div class="slider-arrow right">&#10095;</div>
      </div>
      
      <script>{js_code}</script>
    </div>
    """