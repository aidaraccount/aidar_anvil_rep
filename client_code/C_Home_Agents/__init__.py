from ._anvil_designer import C_Home_AgentsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class C_Home_Agents(C_Home_AgentsTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.setup_slider(data)
    
  def setup_slider(self, data):
    """
    Sets up the slider component with model boxes.
    
    Args:
        data: List of model data to display in the slider.
    """
    # Generate HTML for each model box
    model_boxes_html = ""
    for model in data:
      model_boxes_html += f"""
        <div class="model-box" data-model-id="{model['model_id']}">
          <div class="model-name">{model['model_name']}</div>
        </div>
      """
    
    # CSS for styling the slider and model boxes
    css = """
      /* 
      1. SLIDER CONTAINER STYLES
      */
      .slider-container {
        position: relative;
        overflow: hidden;
        padding: 10px 50px;
        width: 100%;
      }
      
      /* 
      2. SLIDER TRACK STYLES
      */
      .slider-track {
        display: flex;
        transition: transform 0.5s ease;
      }
      
      /* 
      3. MODEL BOX STYLES
      */
      .model-box {
        flex: 0 0 auto;
        min-width: 200px;
        height: 150px;
        margin-right: 15px;
        background-color: #2D2D3A;
        border-radius: 12px;
        padding: 15px;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
      }
      
      .model-name {
        font-size: 18px;
        font-weight: bold;
        text-align: center;
      }
      
      /* 
      4. NAVIGATION ARROW STYLES
      */
      .slider-arrow {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        width: 40px;
        height: 40px;
        background-color: rgba(255, 76, 43, 0.8);
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        font-size: 20px;
        cursor: pointer;
        z-index: 10;
      }
      
      .slider-arrow.left {
        left: 10px;
      }
      
      .slider-arrow.right {
        right: 10px;
      }
      
      .slider-arrow:hover {
        background-color: rgba(255, 76, 43, 1);
      }
    """
    
    # JavaScript for the slider functionality
    js_code = """
      // Track slider position
      let position = 0;
      const track = document.querySelector('.slider-track');
      const boxes = document.querySelectorAll('.model-box');
      
      // Calculate how many items can fit in the view
      function calculateVisibleBoxes() {
        const container = document.querySelector('.slider-container');
        const boxWidth = boxes[0].offsetWidth + parseInt(getComputedStyle(boxes[0]).marginRight);
        return Math.floor(container.offsetWidth / boxWidth);
      }
      
      // Handle left arrow click
      function slideLeft() {
        if (position > 0) {
          position--;
          updateSliderPosition();
        }
      }
      
      // Handle right arrow click
      function slideRight() {
        const visibleBoxes = calculateVisibleBoxes();
        if (position + visibleBoxes < boxes.length) {
          position++;
          updateSliderPosition();
        }
      }
      
      // Update the track position
      function updateSliderPosition() {
        const boxWidth = boxes[0].offsetWidth + parseInt(getComputedStyle(boxes[0]).marginRight);
        track.style.transform = `translateX(-${position * boxWidth}px)`;
      }
      
      // Initialize slider
      function initSlider() {
        // Add event listeners to arrows
        document.querySelector('.slider-arrow.left').addEventListener('click', slideLeft);
        document.querySelector('.slider-arrow.right').addEventListener('click', slideRight);
        
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
      }
      
      // Initialize when page loads
      window.addEventListener('load', initSlider);
    """
    
    # Combine everything into the final HTML
    self.html = f"""
    <div class="agents-slider">
      <style>{css}</style>
      
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