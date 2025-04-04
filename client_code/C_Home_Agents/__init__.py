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


class C_Home_Agents(C_Home_AgentsTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # Print data type for debugging
    print(f"MODEL_ACTIVATION: SLIDER_DEBUG: Data type: {type(data)}")
    
    # Convert string data to list of dictionaries if needed
    if isinstance(data, str):
      try:
        data = json.loads(data)
        print("MODEL_ACTIVATION: SLIDER_DEBUG: Successfully parsed data as JSON")
      except json.JSONDecodeError:
        print("MODEL_ACTIVATION: SLIDER_DEBUG: Failed to parse data as JSON")
    
    if data and isinstance(data, list):
      print(f"MODEL_ACTIVATION: SLIDER_DEBUG: First item type: {type(data[0])}")
      
    # Store models data for access by JavaScript callbacks
    self.models_data = data if isinstance(data, list) else []
    
    # Register JavaScript callback for the discover button - MUST be before setup_slider
    print("MODEL_ACTIVATION: Registering JavaScript callback in __init__")
    try:
      anvil.js.window.pyDiscoverClicked = self.handle_discover_click
      print("MODEL_ACTIVATION: JavaScript callback registered successfully as window.pyDiscoverClicked")
    except Exception as e:
      print(f"MODEL_ACTIVATION: ERROR registering callback: {str(e)}")
      
    # Set up the slider after registering callbacks
    self.setup_slider(data)
  
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    print("MODEL_ACTIVATION: form_show called")
    # Log initial state
    user = anvil.users.get_user()
    print(f"MODEL_ACTIVATION: Current user: {user['user_id'] if user else 'None'}")
    current_model = get_open_form().get_model_id() if hasattr(get_open_form(), 'get_model_id') else 'unknown'
    print(f"MODEL_ACTIVATION: Current model_id (before any clicks): {current_model}")

  def activate_model(self, model_id, **event_args):
    """
    Activates the model before navigating to artist page.
    
    Args:
        model_id: The ID of the model to activate
    """
    print(f"MODEL_ACTIVATION: Starting activation for model_id: {model_id}, type: {type(model_id)}")
    # Store model_id for reference
    self.model_id_view = model_id
    
    user = anvil.users.get_user()
    print(f"MODEL_ACTIVATION: Current user: {user}")
    
    if user and model_id:
      # Log each step for debugging
      print(f"MODEL_ACTIVATION: Step 1: Updating model usage for user {user['user_id']} and model {model_id}")
      try:
        # Update model usage on server
        result = anvil.server.call('update_model_usage', user["user_id"], model_id)
        print(f"MODEL_ACTIVATION: Step 1 complete: Server call result: {result}")
      except Exception as e:
        print(f"MODEL_ACTIVATION: ERROR in server call: {str(e)}")
      
      print(f"MODEL_ACTIVATION: Step 2: Saving model_id {model_id} to client storage")
      try:
        # Save model ID in client storage
        save_var('model_id', model_id)
        # Verify it was saved
        saved_model = anvil.js.window.localStorage.getItem('model_id')
        print(f"MODEL_ACTIVATION: Step 2 complete: Variable saved, localStorage value: {saved_model}")
      except Exception as e:
        print(f"MODEL_ACTIVATION: ERROR saving variable: {str(e)}")
      
      print("MODEL_ACTIVATION: Step 3: Getting main form and refreshing models underline")
      try:
        # Refresh models underline in MainIn form
        main_form = get_open_form()
        print(f"MODEL_ACTIVATION: Main form type: {type(main_form).__name__}")
        if hasattr(main_form, 'refresh_models_underline'):
          print("MODEL_ACTIVATION: Main form has refresh_models_underline method")
          main_form.refresh_models_underline()
          print("MODEL_ACTIVATION: Step 3 complete: Models underline refreshed")
        else:
          print(f"MODEL_ACTIVATION: WARNING: Main form does not have refresh_models_underline method. Available methods: {[m for m in dir(main_form) if not m.startswith('_') and callable(getattr(main_form, m))]}")
      except Exception as e:
        print(f"MODEL_ACTIVATION: ERROR refreshing models: {str(e)}")
    else:
      print(f"MODEL_ACTIVATION: Cannot activate model: user present={user is not None}, model_id={model_id}")
    
    print("MODEL_ACTIVATION: Activation function completed")
    return True
    
  def handle_discover_click(self, artist_id, model_id, ctrl_key=False):
    """
    JavaScript callback for when the discover button is clicked.
    
    Args:
        artist_id: The ID of the artist to navigate to
        model_id: The ID of the model to activate
        ctrl_key: Whether the ctrl key was pressed (to open in new tab)
    """
    timestamp = time.time()
    print(f"MODEL_ACTIVATION [{timestamp}]: Starting handler with artist={artist_id}, model={model_id}, ctrl={ctrl_key}")
    print(f"MODEL_ACTIVATION [{timestamp}]: model_id type: {type(model_id)}")
    
    try:
      # Make sure model_id is passed correctly
      if not model_id:
        print(f"MODEL_ACTIVATION [{timestamp}]: WARNING: No model_id provided in discover click")
        return {"success": False, "error": "No model_id provided"}
        
      # Convert model_id to string if needed
      model_id_str = str(model_id).strip()
      print(f"MODEL_ACTIVATION [{timestamp}]: Converted model_id to string: {model_id_str}")
      
      # Activate the model - call the required functions directly here to ensure they run
      user = anvil.users.get_user()
      if user:
        print(f"MODEL_ACTIVATION [{timestamp}]: Got user: {user['user_id']}")
        # Store model_id for reference
        self.model_id_view = model_id_str
        print(f"MODEL_ACTIVATION [{timestamp}]: Stored model_id_view: {self.model_id_view}")
        
        # 1. Update model usage on server - DIRECTLY CALL WITH EXACT PARAMETERS AS IN LOGS
        print(f"MODEL_ACTIVATION [{timestamp}]: Calling update_model_usage for user {user['user_id']} and model {model_id_str}")
        try:
          # Call with the exact parameter format seen in logs
          result = anvil.server.call('update_model_usage', user["user_id"], model_id_str)
          print(f"MODEL_ACTIVATION [{timestamp}]: Server call completed with result: {result}")
        except Exception as e:
          print(f"MODEL_ACTIVATION [{timestamp}]: ERROR in server call: {str(e)}")
        
        # 2. Save model ID in client storage
        print(f"MODEL_ACTIVATION [{timestamp}]: Saving model_id {model_id_str} to client storage")
        try:
          save_var('model_id', model_id_str)
          # Verify it was saved correctly
          saved_value = anvil.js.window.localStorage.getItem('model_id')
          print(f"MODEL_ACTIVATION [{timestamp}]: Storage value after save: {saved_value}")
        except Exception as e:
          print(f"MODEL_ACTIVATION [{timestamp}]: ERROR saving to storage: {str(e)}")
        
        # 3. Try MULTIPLE approaches to refresh models underline
        print(f"MODEL_ACTIVATION [{timestamp}]: Trying multiple approaches to refresh models underline")
        
        # Approach 1: Try get_open_form() directly
        try:
          main_form = get_open_form()
          print(f"MODEL_ACTIVATION [{timestamp}]: Main form type: {type(main_form).__name__}")
          
          if hasattr(main_form, 'refresh_models_underline'):
            print(f"MODEL_ACTIVATION [{timestamp}]: Found refresh_models_underline method on main_form, calling it")
            main_form.refresh_models_underline()
          else:
            print(f"MODEL_ACTIVATION [{timestamp}]: Main form doesn't have refresh_models_underline")
        except Exception as e:
          print(f"MODEL_ACTIVATION [{timestamp}]: Error with approach 1: {str(e)}")
        
        # Approach 2: Try to find parent form
        try:
          current_form = self
          parent = getattr(current_form, 'parent', None)
          print(f"MODEL_ACTIVATION [{timestamp}]: Parent form type: {type(parent).__name__ if parent else 'None'}")
          
          if parent and hasattr(parent, 'refresh_models_underline'):
            print(f"MODEL_ACTIVATION [{timestamp}]: Found refresh_models_underline on parent, calling it")
            parent.refresh_models_underline()
          elif parent:
            print(f"MODEL_ACTIVATION [{timestamp}]: Parent exists but no refresh_models_underline method")
            # Try to go up one more level
            grandparent = getattr(parent, 'parent', None)
            if grandparent and hasattr(grandparent, 'refresh_models_underline'):
              print(f"MODEL_ACTIVATION [{timestamp}]: Found refresh_models_underline on grandparent, calling it")
              grandparent.refresh_models_underline()
        except Exception as e:
          print(f"MODEL_ACTIVATION [{timestamp}]: Error with approach 2: {str(e)}")
        
        # Approach 3: Try to use app module directly
        try:
          if hasattr(anvil.app, 'refresh_models_underline'):
            print(f"MODEL_ACTIVATION [{timestamp}]: Found refresh_models_underline on anvil.app, calling it")
            anvil.app.refresh_models_underline()
          else:
            print(f"MODEL_ACTIVATION [{timestamp}]: anvil.app doesn't have refresh_models_underline")
            # List available app methods
            app_methods = [m for m in dir(anvil.app) if not m.startswith('_') and callable(getattr(anvil.app, m))]
            print(f"MODEL_ACTIVATION [{timestamp}]: Available app methods: {app_methods}")
        except Exception as e:
          print(f"MODEL_ACTIVATION [{timestamp}]: Error with approach 3: {str(e)}")
        
        # Approach 4: Try to use a global function if defined
        try:
          if 'refresh_models_underline' in globals():
            print(f"MODEL_ACTIVATION [{timestamp}]: Found global refresh_models_underline, calling it")
            globals()['refresh_models_underline']()
          elif 'refresh_models_underline' in locals():
            print(f"MODEL_ACTIVATION [{timestamp}]: Found local refresh_models_underline, calling it")
            locals()['refresh_models_underline']()
        except Exception as e:
          print(f"MODEL_ACTIVATION [{timestamp}]: Error with approach 4: {str(e)}")
          
        # Approach 5: Try direct access to MainIn form if registered somewhere
        try:
          if hasattr(anvil, 'MainIn') and hasattr(anvil.MainIn, 'refresh_models_underline'):
            print(f"MODEL_ACTIVATION [{timestamp}]: Found MainIn on anvil, calling refresh_models_underline")
            anvil.MainIn.refresh_models_underline()
            
          if hasattr(anvil.app, 'MainIn') and hasattr(anvil.app.MainIn, 'refresh_models_underline'):
            print(f"MODEL_ACTIVATION [{timestamp}]: Found MainIn on anvil.app, calling refresh_models_underline")
            anvil.app.MainIn.refresh_models_underline()
        except Exception as e:
          print(f"MODEL_ACTIVATION [{timestamp}]: Error with approach 5: {str(e)}")
      else:
        print(f"MODEL_ACTIVATION [{timestamp}]: No user found, cannot activate model")
    
      # Log final status
      print(f"MODEL_ACTIVATION [{timestamp}]: Handler completed successfully")
      
      # Return navigation info to JavaScript
      return {
        "success": True,
        "artist_id": artist_id,
        "model_id": model_id_str,
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
        print("MODEL_ACTIVATION: SLIDER_DEBUG: Parsed string data in setup_slider")
      except json.JSONDecodeError:
        print("MODEL_ACTIVATION: SLIDER_DEBUG: Could not parse data as JSON in setup_slider")
    
    if isinstance(data, list):
      print(f"MODEL_ACTIVATION: SLIDER_DEBUG: Processing {len(data)} models for slider")
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
      print(f"MODEL_ACTIVATION: SLIDER_DEBUG: Data is not a list, type: {type(data)}")
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
    
    print("MODEL_ACTIVATION: SLIDER_DEBUG: Generated HTML for slider boxes")
    
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
        
        // Check if our Python callback is available
        if (typeof window.pyDiscoverClicked === 'function') {
          try {
            console.log('MODEL_ACTIVATION_JS: Calling Python callback function');
            // Call the Python callback and then navigate
            window.pyDiscoverClicked(artistId, modelId, ctrlKeyPressed).then(function(result) {
              console.log('MODEL_ACTIVATION_JS: Python callback completed:', result);
              
              // Navigate based on ctrl key state
              if (ctrlKeyPressed) {
                console.log('MODEL_ACTIVATION_JS: Opening new tab');
                window.open(appOrigin + '/#artists?artist_id=' + artistId, '_blank');
              } else {
                console.log('MODEL_ACTIVATION_JS: Navigating in current tab');
                window.location.hash = 'artists?artist_id=' + artistId;
              }
            }).catch(function(error) {
              console.error('MODEL_ACTIVATION_JS: Error in Python callback:', error);
              // Navigate anyway if there was an error
              if (ctrlKeyPressed) {
                window.open(appOrigin + '/#artists?artist_id=' + artistId, '_blank');
              } else {
                window.location.hash = 'artists?artist_id=' + artistId;
              }
            });
          } catch (err) {
            console.error('MODEL_ACTIVATION_JS: Error calling Python function:', err);
            // Fallback - just navigate directly
            if (ctrlKeyPressed) {
              window.open(appOrigin + '/#artists?artist_id=' + artistId, '_blank');
            } else {
              window.location.hash = 'artists?artist_id=' + artistId;
            }
          }
        } else {
          console.warn('MODEL_ACTIVATION_JS: Python callback not available, navigating directly');
          // Fallback - just navigate directly
          if (ctrlKeyPressed) {
            window.open(appOrigin + '/#artists?artist_id=' + artistId, '_blank');
          } else {
            window.location.hash = 'artists?artist_id=' + artistId;
          }
        }
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
        
        // Configuration
        const config = {
          boxWidth: 295,           // Width of each model box including margin
          boxMargin: 20,           // Right margin of each box
          centeringOffset: -50,    // Additional offset to apply when centering (negative = more left)
          initDelayMs: 50          // Delay before initialization
        };
        
        // Initialize state
        let currentPosition = 0;
        
        // Function to calculate how many boxes are visible
        function calculateVisibleBoxes() {
          const container = track.parentElement;
          const containerWidth = container.offsetWidth;
          const visibleBoxes = Math.floor(containerWidth / config.boxWidth);
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Calculated visible boxes: ' + visibleBoxes + 
                     ' (container width: ' + containerWidth + 'px, box width: ' + config.boxWidth + 'px)');
          return visibleBoxes;
        }
        
        // Function to update slider position
        function updateSliderPosition(position) {
          currentPosition = position;
          
          // Clamp position so we can't scroll past the first or last item
          const maxPosition = (boxes.length - calculateVisibleBoxes()) * config.boxWidth;
          if (currentPosition < 0) currentPosition = 0;
          if (currentPosition > maxPosition) currentPosition = maxPosition;
          
          const transform = 'translateX(' + (-currentPosition) + 'px)';
          track.style.transform = transform;
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Updated slider position to: ' + 
                     currentPosition + ' transform: ' + transform);
          
          // Check if we should center the slider content when there are few items
          const visibleBoxes = calculateVisibleBoxes();
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Centering check - visible boxes: ' + 
                     visibleBoxes + ', total boxes: ' + boxes.length);
                     
          // Center the content if all boxes can fit with room to spare
          if (boxes.length <= visibleBoxes) {
            centerContent();
          }
          
          // Update arrow visibility based on position
          updateArrowVisibility();
        }
        
        // Function to center content
        function centerContent() {
          const container = track.parentElement;
          const containerWidth = container.offsetWidth;
          
          // Calculate actual width of all boxes (based on actual DOM measurements)
          let totalBoxesWidth = 0;
          for (let i = 0; i < boxes.length; i++) {
            const box = boxes[i];
            const style = window.getComputedStyle(box);
            const width = box.offsetWidth;
            const marginRight = parseInt(style.marginRight) || 0;
            
            // Add width and margin (except for last box)
            if (i < boxes.length - 1) {
              totalBoxesWidth += width + marginRight;
            } else {
              totalBoxesWidth += width; // Last box doesn't need margin
            }
          }
          
          // Calculate centering offset
          const extraSpace = containerWidth - totalBoxesWidth;
          
          // Apply dynamic centering with config offset for fine-tuning
          let centerOffset = Math.floor(extraSpace / 2) + config.centeringOffset;
          
          // Ensure we don't have negative offset (would push content off-screen)
          centerOffset = Math.max(0, centerOffset);
          
          // Apply transform for centering
          track.style.transform = 'translateX(' + centerOffset + 'px)';
          
          console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Centering with measured widths - ' +
                     'container: ' + containerWidth + 'px, content: ' + totalBoxesWidth + 'px, ' +
                     'offset: ' + centerOffset + 'px (with correction: ' + config.centeringOffset + 'px)');
        }
        
        // Function to update arrow visibility
        function updateArrowVisibility() {
          const maxPosition = (boxes.length - calculateVisibleBoxes()) * config.boxWidth;
          
          // If all boxes fit, hide both arrows
          if (maxPosition <= 0) {
            leftArrow.style.display = 'none';
            rightArrow.style.display = 'none';
            console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Hiding arrows - all content fits');
            return;
          }
          
          // Otherwise show/hide based on position
          leftArrow.style.display = currentPosition <= 0 ? 'none' : 'flex';
          rightArrow.style.display = currentPosition >= maxPosition ? 'none' : 'flex';
        }
        
        // Set up click handlers for arrows
        leftArrow.addEventListener('click', function() {
          updateSliderPosition(currentPosition - config.boxWidth);
        });
        
        rightArrow.addEventListener('click', function() {
          updateSliderPosition(currentPosition + config.boxWidth);
        });
        
        // Set initial position and arrow visibility
        console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Setting initial position');
        
        // IMPORTANT: Initialize immediately with proper centering if needed
        // Check if all content fits and center it immediately
        const visibleBoxes = calculateVisibleBoxes();
        const allContentFits = boxes.length <= visibleBoxes;
        
        if (allContentFits) {
          // Use the more accurate centering method for initial positioning
          centerContent();
          
          // Hide arrows since all content fits
          leftArrow.style.display = 'none';
          rightArrow.style.display = 'none';
        } else {
          // Regular initialization at left edge
          updateSliderPosition(0);
        }
        
        console.log('MODEL_ACTIVATION_JS: SLIDER_DEBUG: Slider fully initialized');
      }, config.initDelayMs);
    """
    
    # Add HTML debugging to check structure
    print("MODEL_ACTIVATION: SLIDER_DEBUG: Creating final HTML structure")
    
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
    
    print("MODEL_ACTIVATION: SLIDER_DEBUG: Slider HTML assigned to component")