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
    print(f"SLIDER_DEBUG: Data type: {type(data)}")
    
    # Convert string data to list of dictionaries if needed
    if isinstance(data, str):
      try:
        data = json.loads(data)
        print("SLIDER_DEBUG: Successfully parsed data as JSON")
      except json.JSONDecodeError:
        print("SLIDER_DEBUG: Failed to parse data as JSON")
    
    if data and isinstance(data, list):
      print(f"SLIDER_DEBUG: First item type: {type(data[0])}")
      
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
        print("SLIDER_DEBUG: Parsed string data in setup_slider")
      except json.JSONDecodeError:
        print("SLIDER_DEBUG: Could not parse data as JSON in setup_slider")
    
    if isinstance(data, list):
      print(f"SLIDER_DEBUG: Processing {len(data)} models for slider")
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
      print(f"SLIDER_DEBUG: Data is not a list, type: {type(data)}")
      if isinstance(data, str):
        # If it's still a string at this point, show it as a single box
        model_boxes_html = f"""
          <div class="model-box">
            <div class="model-name">Error: Could not parse data</div>
          </div>
        """
    
    print("SLIDER_DEBUG: Generated HTML for slider boxes")
    
    # JavaScript for the slider functionality
    js_code = """
      console.log('SLIDER_DEBUG: JavaScript loaded');
      
      // Add a small delay to make sure DOM is fully processed
      setTimeout(function() {
        console.log('SLIDER_DEBUG: Starting slider initialization');
        
        // Track slider position
        let position = 0;
        const track = document.querySelector('.slider-track');
        console.log('SLIDER_DEBUG: track element found?', !!track);
        
        const boxes = document.querySelectorAll('.model-box');
        console.log('SLIDER_DEBUG: Found ' + boxes.length + ' model boxes');
        
        const leftArrow = document.querySelector('.slider-arrow.left');
        console.log('SLIDER_DEBUG: leftArrow element found?', !!leftArrow);
        
        const rightArrow = document.querySelector('.slider-arrow.right');
        console.log('SLIDER_DEBUG: rightArrow element found?', !!rightArrow);
        
        if (!track || !boxes.length || !leftArrow || !rightArrow) {
          console.error('SLIDER_DEBUG: Some slider elements not found');
          return;
        }
        
        console.log('SLIDER_DEBUG: All elements found, setting up event handlers');
        
        // Calculate how many items can fit in the view
        function calculateVisibleBoxes() {
          const container = document.querySelector('.slider-container');
          if (!container || boxes.length === 0) {
            console.log('SLIDER_DEBUG: Cannot calculate visible boxes - missing elements');
            return 0;
          }
          const boxWidth = boxes[0].offsetWidth + parseInt(getComputedStyle(boxes[0]).marginRight);
          const result = Math.floor(container.offsetWidth / boxWidth);
          console.log('SLIDER_DEBUG: Calculated visible boxes: ' + result);
          return result;
        }
        
        // Handle left arrow click
        function slideLeft() {
          console.log('SLIDER_DEBUG: Slide left clicked, current position: ' + position);
          if (position > 0) {
            position--;
            updateSliderPosition();
          } else {
            console.log('SLIDER_DEBUG: Already at leftmost position');
          }
        }
        
        // Handle right arrow click
        function slideRight() {
          console.log('SLIDER_DEBUG: Slide right clicked, current position: ' + position);
          const visibleBoxes = calculateVisibleBoxes();
          if (position + visibleBoxes < boxes.length) {
            position++;
            updateSliderPosition();
          } else {
            console.log('SLIDER_DEBUG: Already at rightmost position');
          }
        }
        
        // Update the track position
        function updateSliderPosition() {
          if (boxes.length === 0) {
            console.log('SLIDER_DEBUG: No boxes to position');
            return;
          }
          
          const boxWidth = boxes[0].offsetWidth + parseInt(getComputedStyle(boxes[0]).marginRight);
          track.style.transform = `translateX(-${position * boxWidth}px)`;
          console.log('SLIDER_DEBUG: Updated slider position to: ' + position + ' transform: ' + track.style.transform);
        }
        
        // Explicitly log the click events on arrows
        leftArrow.onclick = function() {
          console.log('SLIDER_DEBUG: Left arrow clicked directly');
          slideLeft();
        };
        
        rightArrow.onclick = function() {
          console.log('SLIDER_DEBUG: Right arrow clicked directly');
          slideRight();
        };
        
        // Also add event listeners as a fallback
        leftArrow.addEventListener('click', function() {
          console.log('SLIDER_DEBUG: Left arrow click from event listener');
          slideLeft();
        });
        
        rightArrow.addEventListener('click', function() {
          console.log('SLIDER_DEBUG: Right arrow click from event listener');
          slideRight();
        });
        
        // Initial positioning
        console.log('SLIDER_DEBUG: Setting initial position');
        updateSliderPosition();
        
        // Handle window resize
        window.addEventListener('resize', function() {
          console.log('SLIDER_DEBUG: Window resized');
          // Reset position if we've moved too far to the right
          const visibleBoxes = calculateVisibleBoxes();
          if (position + visibleBoxes > boxes.length) {
            position = Math.max(0, boxes.length - visibleBoxes);
            updateSliderPosition();
          }
        });
        
        console.log('SLIDER_DEBUG: Slider fully initialized');
      }, 500);
    """
    
    # Add HTML debugging to check structure
    print("SLIDER_DEBUG: Creating final HTML structure")
    
    # Combine everything into the final HTML
    self.html = f"""
    <div class="agents-slider">
      <div class="slider-container">
        <div class="slider-arrow left" onclick="console.log('SLIDER_DEBUG: Left arrow HTML onclick triggered');">&#10094;</div>
        <div class="slider-track">
          {model_boxes_html}
        </div>
        <div class="slider-arrow right" onclick="console.log('SLIDER_DEBUG: Right arrow HTML onclick triggered');">&#10095;</div>
      </div>
      
      <script>{js_code}</script>
    </div>
    """
    
    print("SLIDER_DEBUG: Slider HTML assigned to component")