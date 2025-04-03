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
      
    # Store models data for access by JavaScript callbacks
    self.models_data = data if isinstance(data, list) else []
    self.setup_slider(data)
  
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    # Register JavaScript callback for the discover button
    anvil.js.window.pyDiscoverClicked = self.handle_discover_click

  def activate_model(self, model_id, **event_args):
    """
    Activates the model before navigating to artist page.
    
    Args:
        model_id: The ID of the model to activate
    """
    print(f"Activating model: {model_id}")
    user = anvil.users.get_user()
    
    if user and model_id:
      # Update model usage on server
      anvil.server.call('update_model_usage', user["user_id"], model_id)
      
      # Save model ID in client storage
      save_var('model_id', model_id)
      
      # Refresh models underline in MainIn form
      main_form = get_open_form()
      if hasattr(main_form, 'refresh_models_underline'):
        main_form.refresh_models_underline()
      else:
        print("Warning: Main form does not have refresh_models_underline method")
    
    return True
    
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
          is_senior = False
          progress_bar_class = ""
          
          if model_level == "Senior":
            next_level_text = "You're a pro"
            is_senior = True
            progress_bar_class = "progress-bar-senior"
          elif model_level == "Junior":
            next_level_text = f"{no_missing_ratings} ratings to Senior"
          elif model_level == "Rockie" or model_level == "Rookie":
            next_level_text = f"{no_missing_ratings} ratings to Junior"
          elif model_level == "Trainee":
            next_level_text = f"{no_missing_ratings} ratings to Rookie"
          else:
            next_level_text = f"{no_missing_ratings} ratings to go"
          
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
                  <div class="model-name">{model_name}</div>
                  <div class="model-stars">{stars_html}</div>
                  <div class="model-level">{model_level}</div>
                </div>
                <div class="artist-image-container">
                  <img src="{next_artist_pic_url}" class="artist-image" alt="Artist" />
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
      console.log('SLIDER_DEBUG: JavaScript loaded');
      
      // Function to handle the discover button click
      window.artistDiscoverClick = function(event, artistId, modelId) {
        event.stopPropagation();
        console.log('Discover clicked for artist ID:', artistId, 'model ID:', modelId);
        
        // Get the current URL and app origin
        const appOrigin = window.location.origin;
        const ctrlKeyPressed = event.ctrlKey;
        
        // Check if our Python callback is available
        if (typeof window.pyDiscoverClicked === 'function') {
          try {
            console.log('Calling Python callback function');
            // Call the Python callback and then navigate
            window.pyDiscoverClicked(artistId, modelId, ctrlKeyPressed).then(function(result) {
              console.log('Python callback completed:', result);
              
              // Navigate based on ctrl key state
              if (ctrlKeyPressed) {
                window.open(appOrigin + '/#artists?artist_id=' + artistId, '_blank');
              } else {
                window.location.hash = 'artists?artist_id=' + artistId;
              }
            }).catch(function(error) {
              console.error('Error in Python callback:', error);
              // Navigate anyway if there was an error
              if (ctrlKeyPressed) {
                window.open(appOrigin + '/#artists?artist_id=' + artistId, '_blank');
              } else {
                window.location.hash = 'artists?artist_id=' + artistId;
              }
            });
          } catch (err) {
            console.error('Error calling Python function:', err);
            // Fallback - just navigate directly
            if (ctrlKeyPressed) {
              window.open(appOrigin + '/#artists?artist_id=' + artistId, '_blank');
            } else {
              window.location.hash = 'artists?artist_id=' + artistId;
            }
          }
        } else {
          console.warn('Python callback not available, navigating directly');
          // Fallback - just navigate directly
          if (ctrlKeyPressed) {
            window.open(appOrigin + '/#artists?artist_id=' + artistId, '_blank');
          } else {
            window.location.hash = 'artists?artist_id=' + artistId;
          }
        }
      };
      
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
        
        const container = document.querySelector('.slider-container');
        
        if (!track || !boxes.length || !leftArrow || !rightArrow || !container) {
          console.error('SLIDER_DEBUG: Some slider elements not found');
          return;
        }
        
        console.log('SLIDER_DEBUG: All elements found, setting up event handlers');
        
        // Calculate how many items can fit in the view
        function calculateVisibleBoxes() {
          if (!container || boxes.length === 0) {
            console.log('SLIDER_DEBUG: Cannot calculate visible boxes - missing elements');
            return 0;
          }
          
          // Account for container padding
          const containerStyle = getComputedStyle(container);
          const paddingLeft = parseInt(containerStyle.paddingLeft) || 0;
          const paddingRight = parseInt(containerStyle.paddingRight) || 0;
          const containerWidth = container.offsetWidth - paddingLeft - paddingRight;
          
          // Calculate box width including margin
          const boxWidth = boxes[0].offsetWidth + parseInt(getComputedStyle(boxes[0]).marginRight);
          const result = Math.floor(containerWidth / boxWidth);
          
          console.log('SLIDER_DEBUG: Calculated visible boxes: ' + result + ' (container width: ' + containerWidth + 'px, box width: ' + boxWidth + 'px)');
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
        
        // Center boxes when possible
        function centerBoxesIfNeeded() {
          const visibleBoxes = calculateVisibleBoxes();
          
          console.log('SLIDER_DEBUG: Centering check - visible boxes: ' + visibleBoxes + ', total boxes: ' + boxes.length);
          
          // Get the container dimensions
          const containerStyle = getComputedStyle(container);
          const paddingLeft = parseInt(containerStyle.paddingLeft) || 0;
          const paddingRight = parseInt(containerStyle.paddingRight) || 0;
          const containerWidth = container.offsetWidth - paddingLeft - paddingRight;
          
          // Calculate box width including margin
          const boxStyle = getComputedStyle(boxes[0]);
          const marginRight = parseInt(boxStyle.marginRight) || 0;
          const boxWidth = boxes[0].offsetWidth + marginRight;
          
          // Calculate total width of all boxes
          const totalBoxesWidth = boxWidth * boxes.length;
          
          // Determine if boxes fit within container
          const allBoxesFit = totalBoxesWidth <= containerWidth;
          
          // Show or hide arrows based on whether all boxes fit
          leftArrow.style.display = allBoxesFit ? 'none' : 'flex';
          rightArrow.style.display = allBoxesFit ? 'none' : 'flex';
          
          // Only center if boxes fit
          if (allBoxesFit) {
            const emptySpace = containerWidth - totalBoxesWidth;
            if (emptySpace > 0) {
              // Center the boxes
              const leftOffset = Math.floor(emptySpace / 2);
              track.style.marginLeft = leftOffset + 'px';
              console.log('SLIDER_DEBUG: Centering boxes with margin-left: ' + leftOffset + 'px (container: ' + containerWidth + 'px, boxes: ' + totalBoxesWidth + 'px)');
            } else {
              track.style.marginLeft = '0px';
            }
            // Reset position to 0 when all boxes fit
            position = 0;
            updateSliderPosition();
          } else {
            // If boxes don't fit, reset margin and apply normal slider behavior
            track.style.marginLeft = '0px';
            // Make sure arrows are visible
            leftArrow.style.display = 'flex';
            rightArrow.style.display = 'flex';
            
            // Disable left arrow if at beginning
            leftArrow.style.opacity = position === 0 ? '0.5' : '1';
            
            // Disable right arrow if at end
            const lastVisibleBox = position + visibleBoxes;
            rightArrow.style.opacity = lastVisibleBox >= boxes.length ? '0.5' : '1';
          }
        }
        
        // Explicitly log the click events on arrows
        leftArrow.onclick = function() {
          console.log('SLIDER_DEBUG: Left arrow clicked directly');
          slideLeft();
          // Update arrow states after sliding
          const visibleBoxes = calculateVisibleBoxes();
          leftArrow.style.opacity = position === 0 ? '0.5' : '1';
          rightArrow.style.opacity = position + visibleBoxes >= boxes.length ? '0.5' : '1';
        };
        
        rightArrow.onclick = function() {
          console.log('SLIDER_DEBUG: Right arrow clicked directly');
          slideRight();
          // Update arrow states after sliding
          const visibleBoxes = calculateVisibleBoxes();
          leftArrow.style.opacity = position === 0 ? '0.5' : '1';
          rightArrow.style.opacity = position + visibleBoxes >= boxes.length ? '0.5' : '1';
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
        centerBoxesIfNeeded();
        
        // Handle window resize
        window.addEventListener('resize', function() {
          console.log('SLIDER_DEBUG: Window resized');
          
          // Reset position if we've moved too far to the right
          const visibleBoxes = calculateVisibleBoxes();
          if (position + visibleBoxes > boxes.length) {
            position = Math.max(0, boxes.length - visibleBoxes);
            updateSliderPosition();
          }
          
          // Recenter boxes if needed
          centerBoxesIfNeeded();
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

  def handle_discover_click(self, artist_id, model_id, ctrl_key=False):
    """
    JavaScript callback for when the discover button is clicked.
    
    Args:
        artist_id: The ID of the artist to navigate to
        model_id: The ID of the model to activate
        ctrl_key: Whether the ctrl key was pressed (to open in new tab)
    """
    print(f"Python handling discover click: artist={artist_id}, model={model_id}, ctrl={ctrl_key}")
    
    # Activate the model
    self.activate_model(model_id)
    
    # Return navigation info to JavaScript
    return {
      "success": True,
      "artist_id": artist_id,
      "ctrl_key": ctrl_key
    }