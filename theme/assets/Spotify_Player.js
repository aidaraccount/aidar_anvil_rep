// Global variable to store the Spotify controller
var controller;

// Debouncing variables to prevent rapid button clicks
let isNavigating = false;
const NAVIGATION_DEBOUNCE_MS = 500;


// Centralized playback control function
function executePlaybackAction(action) {
  if (!controller) {
    console.error('Spotify controller not available');
    return false;
  }
  
  try {
    switch (action) {
      case 'play':
        if (controller.isPaused) {
          console.log('Resuming from paused position');
          controller.resume();
        } else if (!controller.isPlaying) {
          console.log('Starting playback');
          controller.play();
        }
        break;
      case 'pause':
        console.log('Pausing playback');
        controller.pause();
        break;
      case 'toggle':
        if (controller.isPaused || !controller.isPlaying) {
          executePlaybackAction('play');
        } else {
          executePlaybackAction('pause');
        }
        break;
    }
    return true;
  } catch (error) {
    console.error('Playback action failed:', error);
    // Fallback: try to reload the controller
    if (error.message && error.message.includes('403')) {
      console.log('Authentication error detected, attempting controller reload');
      setTimeout(() => {
        location.reload();
      }, 1000);
    }
    return false;
  }
}

// function to play/pause spotify - handles both event listener setup AND direct playback
function playSpotify() {
  console.log("playSpotify - sessionStorage.getItem('has_played'): " + sessionStorage.getItem("has_played"));
  
  // If called with no arguments, this is a direct playback call from Python
  if (arguments.length === 0) {
    return executePlaybackAction('toggle');
  }
  
  // Otherwise, set up event listeners for buttons
  const buttons = document.querySelectorAll('.anvil-role-cap-play-pause');
  
  buttons.forEach(button => {
    // Only attach if not already attached to prevent duplicates
    if (!button.hasAttribute('data-spotify-listener-attached')) {
      button.onclick = function () {
        executePlaybackAction('toggle');
      };
      button.setAttribute('data-spotify-listener-attached', 'true');
    }
  });
}

// function to initialize the spotify console
function createOrUpdateSpotifyPlayer(formElement, trackOrArtist, spotifyID, spotifyIDsList, autoplaybutton = false) {
  
  console.log("=== createOrUpdateSpotifyPlayer CALLED ===");
  console.log("Parameters:", {
    formElement: formElement ? "present" : "null",
    trackOrArtist,
    spotifyID,
    spotifyIDsList: spotifyIDsList ? spotifyIDsList.length + " items" : "null",
    autoplaybutton
  });
  
  console.log("createOrUpdateSpotifyPlayer - setItem globalCurrentSpotifyID: " + spotifyID);
  sessionStorage.setItem("globalCurrentSpotifyID", spotifyID);
  
  const element = document.querySelector('.anvil-role-cap-spotify-footer #embed-iframe');
  if (!element) {
    console.error("Spotify embed element not found");
    return;
  }
  
  console.log("Embed element found:", {
    innerHTML: element.innerHTML ? "has content" : "empty",
    childElementCount: element.childElementCount,
    hasExistingController: !!controller
  });

  // set the options for the Spotify Player
  const options = {
    theme: 'dark',
    width: '100%',
    height: '80',
    uri: `spotify:${trackOrArtist}:${spotifyID}`,
  };
  
  console.log("Spotify options:", options);

  // the if statment checks if the SpotifyIgrameAPI already exists (if it is already loaded)
  if (window.SpotifyIframeAPI) {
    let controller_status = 'not_ready';
    
    console.log("Creating Spotify controller with SpotifyIframeAPI...");
    
    window.SpotifyIframeAPI.createController(element, options, (EmbedController) => {
      controller = EmbedController;
      console.log("Controller created successfully");
      
      // Add error listener to catch 403 authentication errors
      controller.addListener('error', (error) => {
        console.log("Spotify controller error:", error);
        console.error("=== SPOTIFY CONTROLLER ERROR ===");
        console.error("Error type:", error.type);
        console.error("Error message:", error.message);
        console.error("Full error object:", error);
        
        // Handle authentication errors specifically
        if (error.type === 'authentication_error' || error.message.includes('403')) {
          console.log("Detected Spotify authentication error - attempting recovery");
          handleSpotifyAuthError();
        }
      });
      
      controller.addListener('ready', () => {
        console.log("createOrUpdateSpotifyPlayer - Spotify Player ready_1");
        console.log("Ready event - autoplaybutton:", autoplaybutton);
        console.log("Ready event - controller state:", {
          isPaused: controller.isPaused,
          position: controller.position,
          duration: controller.duration
        });
        controller_status = 'ready';
        if (autoplaybutton) {
          console.log("Calling autoPlaySpotify from ready_1 listener");
          autoPlaySpotify();
        }
      });
      
      controller.addListener('playback_update', e => {
        const {isPaused, isBuffering, duration, position } = e.data;
        
        // console.log("createOrUpdateSpotifyPlayer - 111 isPaused: " + isPaused);
        // console.log("createOrUpdateSpotifyPlayer - 111 isBuffering: " + isBuffering);  
        // console.log("createOrUpdateSpotifyPlayer - 111 duration: " + duration);
        // console.log("createOrUpdateSpotifyPlayer - 111 position: " + position);
        // console.log("createOrUpdateSpotifyPlayer - 111 controller_status: " + controller_status);
        
        // Check if the song has ended
        if (!isPaused && position >= duration && duration > 0 && controller_status === 'ready') {
          console.log("createOrUpdateSpotifyPlayer - Pos. 1: Track has ended. Moving to the next song.");
          controller_status = 'not_ready';
          
          // Load next song only if spotifyTrackIDsList is provided
          if (spotifyTrackIDsList) {
            playNextSong(formElement, 'track', spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList);
          } else {
            console.log("createOrUpdateSpotifyPlayer - No track list provided. Playback stopped.")
          }
        }
      });
      
      controller.addListener('playback_update', e => {
        const {isPaused, isBuffering, duration, position } = e.data;
        
        // Log the current playback state
        if (isBuffering) {
          console.log("createOrUpdateSpotifyPlayer - Playback is buffering - 1");
        } else if (isPaused) {
          console.log("createOrUpdateSpotifyPlayer - Playback is paused - 1");
          setPlayButtonIcons(trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList)
        } else {
          console.log("createOrUpdateSpotifyPlayer - Playback is playing - 1");
          setPlayButtonIcons(trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList)
        }
      });
    
    });
    
  } else {
    console.log("SpotifyIframeAPI not loaded, loading script...");
    const script = document.createElement("script");
    script.src = "https://open.spotify.com/embed/iframe-api/v1";
    script.async = true;
    document.body.appendChild(script);

    window.onSpotifyIframeApiReady = (IFrameAPI) => {
      console.log("SpotifyIframeApiReady callback triggered");
      let controller_status = 'not_ready';
      
      console.log("Creating controller via onSpotifyIframeApiReady...");
      IFrameAPI.createController(element, options, (EmbedController) => {
        controller = EmbedController;
        console.log("Controller created via onSpotifyIframeApiReady");
        
        // Add error listener to catch 403 authentication errors
        controller.addListener('error', (error) => {
          console.log("Spotify controller error (path 2):", error);
          console.error("=== SPOTIFY CONTROLLER ERROR (PATH 2) ===");
          console.error("Error type:", error.type);
          console.error("Error message:", error.message);
          console.error("Full error object:", error);
          
          // Handle authentication errors specifically
          if (error.type === 'authentication_error' || error.message.includes('403')) {
            console.log("Detected Spotify authentication error - attempting recovery (path 2)");
            handleSpotifyAuthError();
          }
        });
        
        controller.addListener('ready', () => {
          console.log('createOrUpdateSpotifyPlayer - Spotify Player ready_2');
          console.log("Ready event (path 2) - autoplaybutton:", autoplaybutton);
          console.log("Ready event (path 2) - controller state:", {
            isPaused: controller.isPaused,
            position: controller.position,
            duration: controller.duration
          });
          controller_status = 'ready';
          if (autoplaybutton) {
            console.log("Calling autoPlaySpotify from ready_2 listener");
            autoPlaySpotify();
          }
        });  
        
        controller.addListener('playback_update', e => {
          const {isPaused, isBuffering, duration, position} = e.data;
          
          // Check if the song has ended
          if (!isPaused && position >= duration && duration > 0) {
            console.log("createOrUpdateSpotifyPlayer - Pos. 2: Track has ended. Moving to the next song.");

            // Load next song only if spotifyIDsList is provided
            if (spotifyIDsList) {
              playNextSong(formElement, 'track', spotifyIDsList, spotifyIDsList, spotifyIDsList);
            } else {
              console.log("createOrUpdateSpotifyPlayer - No track list provided. Playback stopped.");
            }
          }
        });
        
        controller.addListener('playback_update', e => {
          const {isPaused, isBuffering, duration, position} = e.data;
          
          // Log the current playback state
          if (isBuffering) {
            console.log("createOrUpdateSpotifyPlayer - Playback is buffering - 2");
          } else if (isPaused) {
            console.log("createOrUpdateSpotifyPlayer - Playback is paused - 2");
            setPlayButtonIcons(trackOrArtist, spotifyIDsList, spotifyIDsList)
          } else {
            console.log("createOrUpdateSpotifyPlayer - Playback is playing - 2");
            setPlayButtonIcons(trackOrArtist, spotifyIDsList, spotifyIDsList)
          }
        });
        
      }); 
    };
  }
}

// This function is triggered only when the AUTOPLAY button is switched on
function autoPlaySpotify() {
  executePlaybackAction('play');
}

// This function is triggered when the user clicks on the next/previous song buttons
function playNextSong(formElement, trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList, direction) {
  
  console.log("playNextSong - direction: " + direction);
  
  // Debounce navigation to prevent rapid clicks
  if (isNavigating) {
    console.log("playNextSong - Navigation in progress, ignoring click");
    return;
  }
  
  if (!spotifyTrackIDsList || spotifyTrackIDsList.length === 0) {
    console.error("playNextSong - No Spotify track IDs available");
    return;
  }
  
  // Set navigation flag
  isNavigating = true;
  setTimeout(() => {
    isNavigating = false;
  }, NAVIGATION_DEBOUNCE_MS);

  // console.log("playNextSong - 000 trackOrArtist: " + trackOrArtist);
  // console.log("playNextSong - 000 spotifyTrackIDsList: " + spotifyTrackIDsList);  
  // console.log("playNextSong - 000 spotifyArtistIDsList: " + spotifyArtistIDsList);
  // console.log("playNextSong - 000 spotifyArtistNameList: " + spotifyArtistNameList);
  // console.log("playNextSong - 000 direction: " + direction);
  
  let globalSpotifyArtistIDsList = spotifyArtistIDsList;
  
  // If statement to check if we are playing a list of custom songs or a playlist from Spotify
  if (!spotifyTrackIDsList) {
    console.error("No track list available. Check out Spotify_Player.js file - playNextSong() function.");
    return;
  }
  
  // Declaring the index of the current playing song and get the id for the next song to play
  const index = spotifyTrackIDsList.indexOf(sessionStorage.getItem("globalCurrentSpotifyID"));
  console.log("playNextSong - getItem globalCurrentSpotifyID: " + sessionStorage.getItem("globalCurrentSpotifyID"));
  
  let nextSpotifyTrackID = null;
  let nextSpotifyArtistID = null;
  let nextSpotifyArtistName = null;
  
  if (direction === 'initial') {
    console.log("playNextSong - first song? index: " + index);
    nextSpotifyTrackID = spotifyTrackIDsList[index];
    if (spotifyArtistIDsList) {
      nextSpotifyArtistID = spotifyArtistIDsList[index];
      nextSpotifyArtistName = spotifyArtistNameList[index];
    }
  } else if (direction === 'forward') {
    if (index !== -1 && index < spotifyTrackIDsList.length - 1) {
      nextSpotifyTrackID = spotifyTrackIDsList[index + 1];
      if (spotifyArtistIDsList) {
        nextSpotifyArtistID = spotifyArtistIDsList[index + 1];
        nextSpotifyArtistName = spotifyArtistNameList[index + 1];
      }
    }
  } else if (direction === 'backward') {
    if (index !== -1 && index > 0) {
      nextSpotifyTrackID = spotifyTrackIDsList[index - 1];
      if (spotifyArtistIDsList) {
        nextSpotifyArtistID = spotifyArtistIDsList[index - 1];
        nextSpotifyArtistName = spotifyArtistNameList[index - 1];
      }
    }
  } else if (direction === 'fast-forward' && spotifyArtistIDsList) {
    if (index !== -1 && index < spotifyTrackIDsList.length - 1) {
      const currentArtistID = spotifyArtistIDsList[index];
      let nextIndex = index + 1;
      while (nextIndex < spotifyArtistIDsList.length && spotifyArtistIDsList[nextIndex] === currentArtistID) {
        nextIndex++;
      }
      if (nextIndex < spotifyTrackIDsList.length) {
        nextSpotifyTrackID = spotifyTrackIDsList[nextIndex];
        nextSpotifyArtistID = spotifyArtistIDsList[nextIndex];
        nextSpotifyArtistName = spotifyArtistNameList[nextIndex];
      }
    }
  } else if (direction === 'fast-backward' && spotifyArtistIDsList) {
    if (index !== -1 && index > 0) {
      const currentArtistID = spotifyArtistIDsList[index];
      let prevIndex = index - 1;
      while (prevIndex >= 0 && spotifyArtistIDsList[prevIndex] === currentArtistID) {
        prevIndex--;
      }
      if (prevIndex >= 0) {
        nextSpotifyTrackID = spotifyTrackIDsList[prevIndex];
        nextSpotifyArtistID = spotifyArtistIDsList[prevIndex];
        nextSpotifyArtistName = spotifyArtistNameList[prevIndex];
        // Move to the first track of the previous artist
        while (prevIndex > 0 && spotifyArtistIDsList[prevIndex - 1] === nextSpotifyArtistID) {
          prevIndex--;
        }
        nextSpotifyTrackID = spotifyTrackIDsList[prevIndex];
        nextSpotifyArtistID = spotifyArtistIDsList[prevIndex];
        nextSpotifyArtistName = spotifyArtistNameList[prevIndex];
      }
    }
  } else {
    const index = spotifyTrackIDsList.indexOf(direction);
    nextSpotifyTrackID = spotifyTrackIDsList[index];
    if (spotifyArtistIDsList) {
      nextSpotifyArtistID = spotifyArtistIDsList[index];
      nextSpotifyArtistName = spotifyArtistNameList[index];
    }    
  }

  // console.log("playNextSong - 111 index: " + index);
  // console.log("playNextSong - 111 globalSpotifyArtistIDsList: " + globalSpotifyArtistIDsList);  
  // console.log("playNextSong - 111 spotifyArtistIDsList: " + spotifyArtistIDsList);
  // console.log("playNextSong - 111 nextSpotifyTrackID: " + nextSpotifyTrackID);
  // console.log("playNextSong - 111 nextSpotifyArtistID: " + nextSpotifyArtistID);
  // console.log("playNextSong - 111 nextSpotifyArtistName: " + nextSpotifyArtistName);
  
  // save the id to browser cache
  sessionStorage.setItem("lastplayedtrackid", nextSpotifyTrackID);
  console.log("playNextSong - setItem lastplayedtrackid: " + nextSpotifyTrackID);
  
  if (spotifyArtistIDsList) {
    sessionStorage.setItem("lastplayedartistid", nextSpotifyArtistID)
    console.log("playNextSong - setItem lastplayedartistid: " + nextSpotifyArtistID);
  }
  
  //  check if controller is instantiated and next song is define
  if (controller && nextSpotifyTrackID) {
    const nextSongUri = `spotify:${trackOrArtist}:${nextSpotifyTrackID}`;
    // globalCurrentSpotifyID = nextSpotifyTrackID;
    sessionStorage.setItem("globalCurrentSpotifyID", nextSpotifyTrackID);
    console.log("playNextSong - setItem globalCurrentSpotifyID: " + nextSpotifyTrackID);

    // Check if the artist has changed -> read their name & scroll into view
    const currentArtistID = spotifyArtistIDsList ? spotifyArtistIDsList[index] : null;  
    console.log("playNextSong - 222 currentArtistID: " + currentArtistID);
    
    if (nextSpotifyArtistID && (currentArtistID !== nextSpotifyArtistID || sessionStorage.getItem("has_played") === 'False')) {
      // read name
      speakText(`Presenting, ${nextSpotifyArtistName}!`)
      
      // scroll in view
      const scroll_element = document.querySelector(`.anvil-role-${nextSpotifyArtistID}`);
      if (scroll_element) {
        scroll_element.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });        
      } else {
        console.error(`Element with class .anvil-role-${nextSpotifyArtistID} not found`);
      }
    }

    // reload the controler only if not the first song is played (as its alreay pre-loaded)
    if (index === 0 && direction === 'initial') {
      console.log("playNextSong - No new CONTROLLER needed!");
      // start playing immediately for initial song
      executePlaybackAction('play');
      
      // Set play button icons
      setPlayButtonIcons('track', spotifyTrackIDsList, spotifyArtistIDsList)
    } else {
      // Load new URI and wait for it to be ready before playing
      try {
        controller.loadUri(nextSongUri);
        console.log("playNextSong - Loading next song uri!");
        
        // Add a one-time listener for when the new URI is ready
        const onReady = () => {
          executePlaybackAction('play');
          // Set play button icons after successful play
          setPlayButtonIcons('track', spotifyTrackIDsList, spotifyArtistIDsList);
          controller.removeListener('ready', onReady);
        };
        controller.addListener('ready', onReady);
      } catch (error) {
        console.error('Failed to load new URI:', error);
        // Fallback: try to reload the page if URI loading fails
        setTimeout(() => {
          location.reload();
        }, 1000);
      }
    }

    // load similar artist profile
    if (nextSpotifyArtistID && (currentArtistID !== nextSpotifyArtistID && sessionStorage.getItem("has_played") === 'True')) {
      anvil.call(formElement, 'reload_discover', nextSpotifyArtistID);
    }
    
  }
}

// Function to set the play button icons - optimized to reduce DOM queries
function setPlayButtonIcons(trackOrArtist, spotifyTrackIDsList=null, spotifyArtistIDsList=null) {
  
  // Set the icon of the small play buttons
  if (spotifyTrackIDsList) {
    const currentSpotifyID = sessionStorage.getItem("globalCurrentSpotifyID");
    const isCurrentlyPaused = controller && controller.isPaused;
    
    // Cache DOM queries outside the loop
    const buttonSelectors = spotifyTrackIDsList.map(id => ({
      id,
      buttonPlay: document.querySelector(`.anvil-role-${id}`),
      buttonPlay_inner: document.querySelector(`.anvil-role-${id}-inner`)
    }));
    
    buttonSelectors.forEach(({id, buttonPlay, buttonPlay_inner}) => {
      const isCurrentTrack = id === currentSpotifyID;
      const shouldShowPause = isCurrentTrack && !isCurrentlyPaused;
      const iconClass = shouldShowPause ? 
        'anvil-component-icon left fa fa-pause-circle left-icon' : 
        'anvil-component-icon left fa fa-play-circle left-icon';

      // Update main playlist button
      if (buttonPlay) {
        const icon = buttonPlay.querySelector('i');
        if (icon) {
          icon.className = iconClass;
        }
      }

      // Update inner track releases button
      if (buttonPlay_inner) {
        const icon = buttonPlay_inner.querySelector('i');
        if (icon) {
          icon.className = iconClass;
        }
      }
    });
  }
  
  // Set the icon of the big central play buttons - optimized
  const isCurrentlyPaused = controller && controller.isPaused;
  
  // DISCOVER page big play button
  const buttonPlayBig = document.querySelector(`.anvil-role-cap-play-spotify-button-big1`);
  if (buttonPlayBig) {
    const icon = buttonPlayBig.querySelector('i');
    if (icon) {
      let iconClass;
      if (isCurrentlyPaused || trackOrArtist === 'track') {
        iconClass = 'anvil-component-icon left fa fa-play-circle left-icon';
      } else if (trackOrArtist === 'artist') {
        iconClass = 'anvil-component-icon left fa fa-pause-circle left-icon';
      }
      if (iconClass) icon.className = iconClass;
    }
  }
  
  // LISTEN-IN page big play button
  const buttonPlayBig2 = document.querySelector(`.anvil-role-cap-play-spotify-button-big2`);
  if (buttonPlayBig2) {
    const icon = buttonPlayBig2.querySelector('i');
    if (icon) {
      icon.className = isCurrentlyPaused ? 
        'anvil-component-icon left fa fa-play-circle left-icon' : 
        'anvil-component-icon left fa fa-pause-circle left-icon';
    }
  }

  // set classes of forward and backward buttons on LISTEN-IN
  if (spotifyTrackIDsList) {
    
    const buttonBackward = document.querySelector(`.anvil-role-cap-backward-button`);
    if (buttonBackward) {
     if (sessionStorage.getItem("globalCurrentSpotifyID") === spotifyTrackIDsList[0]) {
        buttonBackward.classList.remove('anvil-role-icon-button');
        buttonBackward.classList.add('anvil-role-icon-button-disabled');
      } else {
        buttonBackward.classList.remove('anvil-role-icon-button-disabled');
        buttonBackward.classList.add('anvil-role-icon-button');
      }
    }

    const buttonForward = document.querySelector(`.anvil-role-cap-forward-button`);
    if (buttonForward) {
      if (sessionStorage.getItem("globalCurrentSpotifyID") === spotifyTrackIDsList[spotifyTrackIDsList.length - 1]) {
        buttonForward.classList.remove('anvil-role-icon-button');
        buttonForward.classList.add('anvil-role-icon-button-disabled');
      } else {
        buttonForward.classList.remove('anvil-role-icon-button-disabled');
        buttonForward.classList.add('anvil-role-icon-button');
      }
    }
  
  }

  // set classes of fast-forward and fast-backward buttons on LISTEN-IN
  if (spotifyTrackIDsList && spotifyArtistIDsList) {
    const buttonFastBackward = document.querySelector(`.anvil-role-cap-fast-backward-button`);
    if (buttonFastBackward) {
      // Check if there is a previous artist
      const currentArtistIndex = spotifyTrackIDsList.indexOf(sessionStorage.getItem("globalCurrentSpotifyID"));
      let hasPreviousArtist = false;
      if (currentArtistIndex > 0) {
        const currentArtistID = spotifyArtistIDsList[currentArtistIndex];
        for (let i = currentArtistIndex - 1; i >= 0; i--) {
          if (spotifyArtistIDsList[i] !== currentArtistID) {
            hasPreviousArtist = true;
            break;
          }
        }
      }
  
      if (hasPreviousArtist) {
        buttonFastBackward.classList.remove('anvil-role-icon-button-disabled');
        buttonFastBackward.classList.add('anvil-role-icon-button');
      } else {
        buttonFastBackward.classList.remove('anvil-role-icon-button');
        buttonFastBackward.classList.add('anvil-role-icon-button-disabled');
      }
    }
  
    const buttonFastForward = document.querySelector(`.anvil-role-cap-fast-forward-button`);
    if (buttonFastForward) {
      // Check if there is a next artist
      const currentArtistIndex = spotifyTrackIDsList.indexOf(sessionStorage.getItem("globalCurrentSpotifyID"));
      let hasNextArtist = false;
      if (currentArtistIndex < spotifyTrackIDsList.length - 1) {
        const currentArtistID = spotifyArtistIDsList[currentArtistIndex];
        for (let i = currentArtistIndex + 1; i < spotifyArtistIDsList.length; i++) {
          if (spotifyArtistIDsList[i] !== currentArtistID) {
            hasNextArtist = true;
            break;
          }
        }
      }
  
      if (hasNextArtist) {
        buttonFastForward.classList.remove('anvil-role-icon-button-disabled');
        buttonFastForward.classList.add('anvil-role-icon-button');
      } else {
        buttonFastForward.classList.remove('anvil-role-icon-button');
        buttonFastForward.classList.add('anvil-role-icon-button-disabled');
      }
    }
  }
}

// Function to handle Spotify authentication errors with recovery attempts
function handleSpotifyAuthError() {
  console.log("=== HANDLING SPOTIFY AUTH ERROR ===");
  
  // Show user notification
  showSpotifyAuthNotification();
  
  // Clear Spotify-related storage to force fresh authentication
  try {
    // Clear session storage
    sessionStorage.removeItem('globalCurrentSpotifyID');
    sessionStorage.removeItem('spotify-sdk-initialization-state');
    
    // Clear local storage Spotify data
    Object.keys(localStorage).forEach(key => {
      if (key.toLowerCase().includes('spotify')) {
        localStorage.removeItem(key);
      }
    });
    
    // Clear cookies related to Spotify
    document.cookie.split(";").forEach(cookie => {
      const eqPos = cookie.indexOf("=");
      const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
      if (name.toLowerCase().includes('spotify') || name.toLowerCase().includes('sp_')) {
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=.spotify.com";
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
      }
    });
    
    console.log("Cleared Spotify session data");
  } catch (error) {
    console.log("Error clearing Spotify session data:", error);
  }
  
  // Attempt automatic recovery with fresh session
  setTimeout(() => {
    console.log("Attempting automatic recovery from 403 error with fresh session");
    
    // Clear the existing iframe and controller
    const element = document.querySelector('.anvil-role-cap-spotify-footer #embed-iframe');
    if (element) {
      element.innerHTML = '';
      
      // Reset global controller
      if (window.controller) {
        window.controller = null;
      }
      
      // Force a complete page reload to clear all Spotify state
      setTimeout(() => {
        console.log("Forcing page reload to clear Spotify Connect session");
        window.location.reload(true);
      }, 1500);
    }
  }, 1000);
}

// Function to show user-friendly notification about the authentication issue
function showSpotifyAuthNotification() {
  // Remove any existing notification
  const existingNotification = document.querySelector('.spotify-auth-notification');
  if (existingNotification) {
    existingNotification.remove();
  }
  
  // Create notification element
  const notification = document.createElement('div');
  notification.className = 'spotify-auth-notification';
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #ff6b6b;
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    z-index: 10000;
    max-width: 350px;
    font-family: Arial, sans-serif;
    font-size: 14px;
    line-height: 1.4;
  `;
  
  notification.innerHTML = `
    <strong>Spotify Connect Conflict</strong><br>
    Multiple Spotify sessions detected. Clearing session data and reloading...
    <br><br>
    <strong>Manual fixes if needed:</strong><br>
    • Close Spotify app on other devices<br>
    • Log out of Spotify completely, then log back in<br>
    • Use incognito/private browsing mode<br>
    • Pause playback on all other Spotify devices<br>
    <br>
    <button onclick="this.parentElement.remove()" style="
      background: white; 
      color: #ff6b6b; 
      border: none; 
      padding: 5px 10px; 
      border-radius: 4px; 
      cursor: pointer;
      font-size: 12px;
      margin-top: 5px;
    ">Dismiss</button>
  `;
  
  document.body.appendChild(notification);
  
  // Auto-remove after 8 seconds
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 8000);
}

// function for speaking the artists name
function speakText(text, callback=null) {
  // Check if the browser supports speech synthesis
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text); // Create a speech utterance
    
    // Attach an event listener for when the speech ends
    utterance.onend = () => {
      console.log('Speech synthesis completed.');
      if (callback) {
        callback(); // Execute the callback function
      }
    };
    
    window.speechSynthesis.speak(utterance); // Speak the text
  } else {
    console.error('Speech synthesis is not supported in this browser.');
    if (callback) {
      callback(); // Fallback to execute callback immediately
    }
  }
}
