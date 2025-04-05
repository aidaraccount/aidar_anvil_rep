from ._anvil_designer import C_Home_AgentsTemplate
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

# Global user variable
user = None


class C_Home_Agents(C_Home_AgentsTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    # Convert string data to list of dictionaries if needed
    if isinstance(data, str):
      try:
        data = json.loads(data)
      except json.JSONDecodeError:
        print("SLIDER_DEBUG: Failed to parse data as JSON")
          
    # Store models data for access by JavaScript callbacks
    self.models_data = data if isinstance(data, list) else []
    
    # Register JavaScript callback for the discover button - MUST be before setup_slider
    print("Registering JavaScript callback in __init__")
    try:
      anvil.js.window.pyDiscoverClicked = self.handle_discover_click
      print("JavaScript callback registered successfully as window.pyDiscoverClicked")
    except Exception as e:
      print(f"ERROR registering callback: {str(e)}")
      
    # Set up the slider after registering callbacks
    self.setup_slider(data)

  
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    # Log initial state
    current_model = get_open_form().get_model_id() if hasattr(get_open_form(), 'get_model_id') else 'unknown'
    
  def handle_discover_click(self, artist_id, model_id, ctrl_key=False):
    """
    JavaScript callback for when the discover button is clicked.
    
    Args:
        artist_id: The ID of the artist to navigate to
        model_id: The ID of the model to activate
        ctrl_key: Whether the ctrl key was pressed (to open in new tab)
    """
    timestamp = time.time()
    
    try:
      # Store model_id for Discover page
      save_var('model_id', model_id)
      
      # Update model usage on server
      anvil.server.call('update_model_usage', user["user_id"], model_id)
      get_open_form().refresh_models_underline()
      get_open_form().reset_nav_backgrounds()
      
      # Log final status
      print(f"DISCOVER_CLICK [{timestamp}]: Handler completed successfully")
      
      # Return navigation info to JavaScript
      return {
        "success": True,
        "artist_id": artist_id,
        "model_id": model_id,
        "ctrl_key": ctrl_key
      }
    except Exception as e:
      print(f"MODEL_ACTIVATION [{timestamp}]: ERROR in handler: {str(e)}")
      import traceback
      print(f"MODEL_ACTIVATION [{timestamp}]: Traceback: {traceback.format_exc()}")
      return {"success": False, "error": str(e)}

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
          model_level = model.get('model_level', 'Unknown')
          no_stars = model.get('no_stars', 0)
          next_artist_id = model.get('next_artist_id', '')
          next_artist_pic_url = model.get('next_artist_pic_url', '')
          no_ratings = model.get('no_ratings', 0)
          no_missing_ratings = model.get('no_missing_ratings', 0)
          
          # Calculate progress percentage
          total_ratings = no_ratings + no_missing_ratings
          progress_percent = (no_ratings / total_ratings * 100) if total_ratings > 0 else 0
          
          # Determine next level and ratings to go
          next_level_text = ""
          progress_bar_class = ""
          
          if model_level == "Rookie":
            next_level_text = f"{no_missing_ratings} ratings to Junior"
          elif model_level == "Junior":
            next_level_text = f"{no_missing_ratings} ratings to Senior"
          elif model_level == "Senior":
            next_level_text = f"{no_missing_ratings} ratings to Pro"
          elif model_level == "Pro":
            next_level_text = "You're a Pro"
            progress_bar_class = "progress-bar-pro"
          
          # Generate the stars HTML - always 3 stars, with 'no_stars' colored orange
          stars_html = ""
          for i in range(3):
            if i < no_stars:
              # Orange star
              stars_html += '<span class="model-star active">★</span>'
            else:
              # Gray star
              stars_html += '<span class="model-star">★</span>'
              
          model_boxes_html += f"""
            <div class="model-box" data-model-id="{model_id}">
              <div class="model-box-top-row">
                <div class="model-info">
                  <div class="model-name">
                    <a href="#" onclick="window.modelNameClick(event, '{model_id}'); return false;" class="model-name-link">{model_name}</a>
                  </div>
                  <div class="model-stars">{stars_html}</div>
                  <div class="model-level">{model_level}</div>
                </div>
                <div class="artist-image-container">
                  <a href="#" onclick="window.artistDiscoverClick(event, '{next_artist_id}', '{model_id}'); return false;" class="artist-image-link">
                    <img src="{next_artist_pic_url}" class="artist-image" alt="Artist" />
                  </a>
                  <button class="discover-button" onclick="window.artistDiscoverClick(event, '{next_artist_id}', '{model_id}')">Discover</button>
                </div>
              </div>
              <div class="model-progress-container">
                <div class="model-progress-text">{next_level_text}</div>
                <div class="model-progress-bar-container">
                  <div class="model-progress-bar {progress_bar_class}" style="width: {progress_percent}%;"></div>
                </div>
              </div>
            </div>
          """
        else:
          # Handle string or other non-dict items if needed
          model_boxes_html += f"""
            <div class="model-box">
              <div class="model-box-top-row">
                <div class="model-info">
                  <div class="model-name">{str(model)}</div>
                  <div class="model-stars">★★★</div>
                  <div class="model-level">Unknown</div>
                </div>
                <div class="artist-image-container">
                  <img src="" class="artist-image" alt="Artist" />
                  <button class="discover-button">Discover</button>
                </div>
              </div>
              <div class="model-progress-container">
                <div class="model-progress-text">0 ratings to go</div>
                <div class="model-progress-bar-container">
                  <div class="model-progress-bar" style="width: 0%;"></div>
                </div>
              </div>
            </div>
          """
    else:
      print(f"SLIDER_DEBUG: Data is not a list, type: {type(data)}")
      if isinstance(data, str):
        # If it's still a string at this point, show it as a single box
        model_boxes_html = f"""
          <div class="model-box">
            <div class="model-box-top-row">
              <div class="model-info">
                <div class="model-name">Error: Could not parse data</div>
                <div class="model-stars">★★★</div>
                <div class="model-level">Unknown</div>
              </div>
              <div class="artist-image-container">
                <img src="" class="artist-image" alt="Artist" />
                <button class="discover-button">Discover</button>
              </div>
            </div>
            <div class="model-progress-container">
              <div class="model-progress-text">0 ratings to go</div>
              <div class="model-progress-bar-container">
                <div class="model-progress-bar" style="width: 0%;"></div>
              </div>
            </div>
          </div>
        """
    
    print("SLIDER_DEBUG: Generated HTML for slider boxes")
    
    # JavaScript for the slider functionality
    js_code = """
      console.log('MODEL_ACTIVATION_JS: JavaScript loaded');
      
      // Function to handle the discover button click (artist page navigation)
      window.artistDiscoverClick = function(event, artistId, modelId) {
        event.stopPropagation();
        console.log('MODEL_ACTIVATION_JS: Discover clicked for artist ID:', artistId, 'model ID:', modelId);
        
        // Get the current URL and app origin
        const appOrigin = window.location.origin;
        const ctrlKeyPressed = event.ctrlKey;
        
        // First, navigate to the artist page based on ctrl key state
        if (ctrlKeyPressed) {
          console.log('MODEL_ACTIVATION_JS: Opening new tab');
          window.open(appOrigin + '/#artists?artist_id=' + artistId, '_blank');
        } else {
          console.log('MODEL_ACTIVATION_JS: Navigating in current tab');
          window.location.hash = 'artists?artist_id=' + artistId;
        }
        
        // Small delay to ensure URL change completes
        setTimeout(function() {
          // Check if our Python callback is available
          if (typeof window.pyDiscoverClicked === 'function') {
            try {
              console.log('MODEL_ACTIVATION_JS: Calling Python callback function');
              // Call the Python callback after navigation
              window.pyDiscoverClicked(artistId, modelId, ctrlKeyPressed).then(function(result) {
                console.log('MODEL_ACTIVATION_JS: Python callback completed:', result);
              }).catch(function(error) {
                console.error('MODEL_ACTIVATION_JS: Error in Python callback:', error);
              });
            } catch (err) {
              console.error('MODEL_ACTIVATION_JS: Error calling Python function:', err);
              console.log('MODEL_ACTIVATION_JS: URL has already been changed, so navigation is complete');
            }
          } else {
            console.warn('MODEL_ACTIVATION_JS: Python callback not available');
          }
        }, 100); // 100ms delay to ensure URL change is processed
      };
      
      // Function to handle model name click (model profile navigation)
      window.modelNameClick = function(event, modelId) {
        event.stopPropagation();
        console.log('MODEL_ACTIVATION_JS: Model name clicked for model ID:', modelId);
        
        // Get the current URL and app origin
        const appOrigin = window.location.origin;
        const ctrlKeyPressed = event.ctrlKey;
        
        // Create the model profile URL
        const modelProfileUrl = 'model_profile?model_id=' + modelId + '&section=Main';
        
        // Navigate based on ctrl key state
        if (ctrlKeyPressed) {
          console.log('MODEL_ACTIVATION_JS: Opening model profile in new tab');
          window.open(appOrigin + '/#' + modelProfileUrl, '_blank');
        } else {
          console.log('MODEL_ACTIVATION_JS: Navigating to model profile in current tab');
          window.location.hash = modelProfileUrl;
        }
      };
      
      // Add a small delay to make sure DOM is fully processed
      setTimeout(function() {
        console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Starting slider initialization');
        
        // Get DOM elements
        const track = document.querySelector('.slider-track');
        if (!track) {
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Track element not found');
          return;
        }
        console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: track element found?', !!track);
        
        const boxes = track.querySelectorAll('.model-box');
        console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Found ' + boxes.length + ' model boxes');
        
        const leftArrow = document.querySelector('.slider-arrow.left');
        console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: leftArrow element found?', !!leftArrow);
        
        const rightArrow = document.querySelector('.slider-arrow.right');
        console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: rightArrow element found?', !!rightArrow);
        
        if (!track || !boxes.length || !leftArrow || !rightArrow) {
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Missing required elements');
          return;
        }
        
        console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: All elements found, setting up event handlers');
        
        // Initialize state
        let currentPosition = 0;
        const boxWidth = 295; // Width of each model box including margin
        const boxMargin = 20; // Right margin of each box
        
        // Function to calculate how many boxes are visible
        function calculateVisibleBoxes() {
          const container = track.parentElement;
          const containerWidth = container.offsetWidth;
          const visibleBoxes = Math.floor(containerWidth / boxWidth);
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Calculated visible boxes: ' + visibleBoxes + 
                     ' (container width: ' + containerWidth + 'px, box width: ' + boxWidth + 'px)');
          return visibleBoxes;
        }
        
        // Function to calculate the center position
        function calculateCenterPosition() {
          const container = track.parentElement;
          const containerWidth = container.offsetWidth;
          
          // Calculate total content width
          let totalContentWidth = 0;
          boxes.forEach(function(box, index) {
            // Add width of current box
            totalContentWidth += box.offsetWidth;
            
            // Add margin except for last box
            if (index < boxes.length - 1) {
              const style = window.getComputedStyle(box);
              totalContentWidth += parseInt(style.marginRight || 0);
            }
          });
          
          // Calculate center position
          let centerPos = (containerWidth - totalContentWidth) / 2;
          
          // Add a small adjustment to compensate for any measurement inaccuracies
          // This helps ensure perfect visual centering
          centerPos += -50; // Adjust by -50px to the left
          
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Center calculation - container width: ' + 
                    containerWidth + ', content width: ' + totalContentWidth + 
                    ', raw center: ' + ((containerWidth - totalContentWidth) / 2) + 
                    ', adjusted center: ' + centerPos);
          
          // Return the calculated and adjusted center position
          return centerPos;
        }
        
        // Function to update arrow visibility and apply edge transparency
        function updateArrows() {
          // Calculate maxPosition based on how many boxes can be fully visible
          const visibleBoxes = calculateVisibleBoxes();
          const maxPosition = Math.max(0, boxes.length - visibleBoxes);
          
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Updating arrows. Current position: ' + 
                     currentPosition + ', Max position: ' + maxPosition);
          
          // Clear previous edge effects
          track.parentElement.classList.remove('show-left-overlay', 'show-right-overlay');
          
          // Only apply edge effects if arrows are visible
          const leftArrowVisible = currentPosition > 0;
          const rightArrowVisible = currentPosition < maxPosition;
          
          if (boxes.length <= visibleBoxes) {
            // If all boxes fit, hide both arrows
            leftArrow.style.display = 'none';
            rightArrow.style.display = 'none';
          } else {
            // Show/hide arrows based on position
            leftArrow.style.display = leftArrowVisible ? 'flex' : 'none';
            rightArrow.style.display = rightArrowVisible ? 'flex' : 'none';
            
            // Apply overlay effects only where arrows are visible
            if (leftArrowVisible) {
              track.parentElement.classList.add('show-left-overlay');
            }
            
            if (rightArrowVisible) {
              track.parentElement.classList.add('show-right-overlay');
            }
          }
        }
        
        // Function to update slider position
        function updatePosition(position) {
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Updating position to: ' + position);
          currentPosition = position;
          
          // Clamp position so we can't scroll past the first or last item
          const visibleBoxes = calculateVisibleBoxes();
          const maxPosition = Math.max(0, boxes.length - visibleBoxes);
          
          if (currentPosition < 0) currentPosition = 0;
          if (currentPosition > maxPosition) currentPosition = maxPosition;
          
          const newPosition = -currentPosition * boxWidth;
          track.style.transform = 'translateX(' + newPosition + 'px)';
          
          // Check if we should center the slider content when there are few items
          if (boxes.length <= visibleBoxes) {
            centerContent();
          } else {
            // Remove centering class if we need to scroll
            track.parentElement.classList.remove('center-slider-content');
          }
          
          updateArrows();
        }
        
        // Function to center content with animation
        function centerContent() {
          const centerPos = calculateCenterPosition();
          track.style.transform = 'translateX(' + centerPos + 'px)';
        }
        
        // Set up click handlers for arrows
        leftArrow.addEventListener('click', function() {
          updatePosition(currentPosition - 1);
        });
        
        rightArrow.addEventListener('click', function() {
          updatePosition(currentPosition + 1);
        });
        
        // Set initial position and arrow visibility
        console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Setting initial position');
        
        // IMPORTANT: Initialize immediately with proper centering if needed
        // Check if all content fits and center it immediately
        const visibleBoxes = calculateVisibleBoxes();
        const allContentFits = boxes.length <= visibleBoxes;
        
        if (allContentFits) {
          // Hide arrows since all content fits
          leftArrow.style.display = 'none';
          rightArrow.style.display = 'none';
          
          // Two-step animation process:
          // 1. Ensure there's no transition initially and set to left position
          track.style.transition = 'none';
          track.style.transform = 'translateX(0px)';
          
          // Get dimensions before animation starts
          const centerPos = calculateCenterPosition();
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Will animate to: ' + centerPos + 'px');
          
          // 2. After a brief delay, set up the transition and move to center
          // This delay ensures the browser has rendered the initial position
          setTimeout(function() {
            // Add transition
            track.style.transition = 'transform 0.8s cubic-bezier(0.215, 0.61, 0.355, 1)';
            
            // Apply the centered position with animation
            track.style.transform = 'translateX(' + centerPos + 'px)';
            console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Animation started');
          }, 300);
        } else {
          // Regular initialization at left edge
          updatePosition(0);
        }
        
        console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Slider fully initialized');

        // Listen for window resize to adjust visible boxes
        window.addEventListener('resize', function() {
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Window resized');
          // Update arrow visibility on window resize
          updateArrows();
        });
        
        // Initial update
        updateArrows();
      }, 50);
    """
    
    # Add HTML debugging to check structure
    print("SLIDER_DEBUG: Creating final HTML structure")
    
    # Combine everything into the final HTML
    self.html = f"""
    <div class="agents-slider">
      <div class="slider-container">
        <div class="slider-arrow left" onclick="console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Left arrow HTML onclick triggered');">&#10094;</div>
        <div class="slider-track">
          {model_boxes_html}
        </div>
        <div class="slider-arrow right" onclick="console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Right arrow HTML onclick triggered');">&#10095;</div>
      </div>
      
      <script>{js_code}</script>
    </div>
    """
    
    print("SLIDER_DEBUG: Slider HTML assigned to component")
