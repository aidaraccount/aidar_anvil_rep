var controller;

// function to play/pause spotify
function playSpotify() {
  console.log("playSpotify - sessionStorage.getItem('has_played'): " + sessionStorage.getItem("has_played"));
  const buttons = document.querySelectorAll('.anvil-role-cap-play-pause');
  
  buttons.forEach(button => {
    button.onclick = function () {

      // console.log("playSpotify - controller.isPaused:" + controller.isPaused);
      // console.log("playSpotify - controller.isPlaying:" + controller.isPlaying);
      // console.log("playSpotify - !controller.isPlaying:" + !controller.isPlaying);
      // console.log("playSpotify - controller" + controller);
      
      if (controller.isPaused) {
        console.log('playSpotify - 1. Resume playing from the paused position')
        controller.resume();  // Resume playing from the paused position
        controller.isPlaying = true;
        controller.isPaused = false;
      } else if (!controller.isPlaying) {
        console.log('playSpotify - 2. Start playing if not already playing')
        controller.play();    // Start playing if not already playing
        controller.isPlaying = true;
        controller.isPaused = false;
      } else {
        console.log('playSpotify - 3. Pause the player if its currently playing')
        controller.pause();   // Pause the player if it's currently playing
        controller.isPlaying = false;
        controller.isPaused = true;
      }
    };
  });
}

// function to initialize the spotify console
function createOrUpdateSpotifyPlayer(formElement, trackOrArtist, currentSpotifyID, spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList) {
  
  // console.log("createOrUpdateSpotifyPlayer - 000 trackOrArtist: " + trackOrArtist);
  // console.log("createOrUpdateSpotifyPlayer - 000 currentSpotifyID: " + currentSpotifyID);  
  // console.log("createOrUpdateSpotifyPlayer - 000 spotifyTrackIDsList: " + spotifyTrackIDsList);
  // console.log("createOrUpdateSpotifyPlayer - 000 spotifyArtistIDsList: " + spotifyArtistIDsList);
  // console.log("createOrUpdateSpotifyPlayer - 000 spotifyArtistNameList: " + spotifyArtistNameList);
  
  const element = document.querySelector('.anvil-role-cap-spotify-footer #embed-iframe');
  const autoplaybutton = document.querySelector('.anvil-role-cap-autoplay-toggle-button .fa-toggle-on')

  // check if the html for the player is imported (in the Discover Page)
  if (!element) {
    console.error("ERROR MESSAGE: Embed iframe element not found.")
    return;
  }

  // globalCurrentSpotifyID = currentSpotifyID;
  sessionStorage.setItem("globalCurrentSpotifyID", currentSpotifyID);
  console.log("createOrUpdateSpotifyPlayer - setItem globalCurrentSpotifyID: " + currentSpotifyID);

  // set the options for the Spotify Player
  const options = {
    theme: 'dark',
    width: '100%',
    height: '80',
    uri: `spotify:${trackOrArtist}:${currentSpotifyID}`,
  };

  // the if statment checks if the SpotifyIgrameAPI already exists (if it is already loaded)
  if (window.SpotifyIframeAPI) {
    let controller_status = 'not_ready';
    
    window.SpotifyIframeAPI.createController(element, options, (EmbedController) => {
      controller = EmbedController;
      controller.addListener('ready', () => {
        console.log('createOrUpdateSpotifyPlayer - Spotify Player ready_1');
        controller_status = 'ready';
        if (autoplaybutton) {
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
    window.onSpotifyIframeApiReady = (IFrameAPI) => {
      window.SpotifyIframeAPI = IFrameAPI; // Store the API globally for future use
      IFrameAPI.createController(element, options, (EmbedController) => {
        controller = EmbedController;
        controller.addListener('ready', () => {
          console.log('createOrUpdateSpotifyPlayer - Spotify Player ready_2');
          if (autoplaybutton) {
            autoPlaySpotify();
          }
        });
        
        controller.addListener('playback_update', e => {
          const {isPaused, isBuffering, duration, position} = e.data;
          
          // Check if the song has ended
          if (!isPaused && position >= duration && duration > 0) {
            console.log("createOrUpdateSpotifyPlayer - Pos. 2: Track has ended. Moving to the next song.");

            // Load next osng only if spotifyTrackIDsList is provided
            if (spotifyTrackIDsList) {
              playNextSong(formElement, 'track', spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList);
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
            setPlayButtonIcons(trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList)
          } else {
            console.log("createOrUpdateSpotifyPlayer - Playback is playing - 2");
            setPlayButtonIcons(trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList)
          }
        });
        
      }); 
    };
  }
}

// This function is triggered only when the AUTOPLAY button is switched on
function autoPlaySpotify() {
  if (controller) {
    // Check the playback state and decide what to do
    if (controller.isPaused) {
      controller.resume();  // Resume playing from the paused position
      controller.isPlaying = true;
      controller.isPaused = false;
    } else if (!controller.isPlaying) {
      controller.play();    // Start playing if not already playing
      controller.isPlaying = true;
      controller.isPaused = false;
    }
  } else {
    console.error("Spotify controller is not initialized.");
  }
}

// Function to load the next song
function playNextSong(formElement, trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList, direction='forward') {

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

    // reload the controler only if not the first song is played (as its alreay pre-loaded)
    if (index === 0 && direction === 'initial') {
      console.log("playNextSong - No new CONTROLLER needed!");
    } else {
      controller.loadUri(nextSongUri);
      console.log("playNextSong - Loading next song uri!");
    }
    
    // Check if the artist has changed -> read their name & scroll into view
    const currentArtistID = spotifyArtistIDsList ? spotifyArtistIDsList[index] : null;  
    console.log("playNextSong - 222 currentArtistID: " + currentArtistID);
    
    if (nextSpotifyArtistID && (currentArtistID !== nextSpotifyArtistID || sessionStorage.getItem("has_played") === 'False')) {
      // read name
      speakText(`...Presenting, ${nextSpotifyArtistName}!`)
      
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
    
    // start playling
    controller.play();
    controller.isPlaying = true;
    controller.isPaused = false;
    
    // Set play button icons
    setPlayButtonIcons('track', spotifyTrackIDsList, spotifyArtistIDsList)

    // load similar artist profile
    if (nextSpotifyArtistID && (currentArtistID !== nextSpotifyArtistID && sessionStorage.getItem("has_played") === 'True')) {
      anvil.call(formElement, 'reload_discover', nextSpotifyArtistID);
    }
    
  }
}

// Function to set the play button icons
function setPlayButtonIcons(trackOrArtist, spotifyTrackIDsList=null, spotifyArtistIDsList=null) {
  
  // Set the icon of the small play buttons
  if (spotifyTrackIDsList) {
    spotifyTrackIDsList.forEach(function(currentId) {

      // inside the Listen-In playlist
      const buttonPlay = document.querySelector(`.anvil-role-${currentId}`);      
      if (currentId === sessionStorage.getItem("globalCurrentSpotifyID") && !controller.isPaused) {
        if (buttonPlay) {
          let icon = buttonPlay.querySelector('i')
          if (icon) {
            icon.className = 'anvil-component-icon left fa fa-pause-circle left-icon'
          }
        }
      } else {
        if (buttonPlay) {
          let icon = buttonPlay.querySelector('i')
          if (icon) {
            icon.className = 'anvil-component-icon left fa fa-play-circle left-icon'
          }
        }
      }

      // inside the Listen-In C_Discover artists Track Releases
      const buttonPlay_inner = document.querySelector(`.anvil-role-${currentId}-inner`);    
      if (currentId === sessionStorage.getItem("globalCurrentSpotifyID") && !controller.isPaused) {
        if (buttonPlay_inner) {
          let icon = buttonPlay_inner.querySelector('i')
          if (icon) {
            icon.className = 'anvil-component-icon left fa fa-pause-circle left-icon'
          }
        }
      } else {
        if (buttonPlay_inner) {
          let icon = buttonPlay_inner.querySelector('i')
          if (icon) {
            icon.className = 'anvil-component-icon left fa fa-play-circle left-icon'
          }
        }
      }
      
    })
  }
  
  // Set the icon of the big central play button on DISCOVER
  // should be play when nothing is playling to start the artists tracks
  const buttonPlayBig = document.querySelector(`.anvil-role-cap-play-spotify-button-big1`);

  if (controller.isPaused) {
    if (buttonPlayBig) {
      let icon = buttonPlayBig.querySelector('i')
      if (icon) {
        icon.className = 'anvil-component-icon left fa fa-play-circle left-icon'
      }
    }
  }
  if (trackOrArtist ==  'track') {
    if (buttonPlayBig) {
      let icon = buttonPlayBig.querySelector('i')
      if (icon) {
        icon.className = 'anvil-component-icon left fa fa-play-circle left-icon'
      }
    }    
  }
  if (trackOrArtist ==  'artist' && !controller.isPaused) {
    if (buttonPlayBig) {
      let icon = buttonPlayBig.querySelector('i')
      if (icon) {
        icon.className = 'anvil-component-icon left fa fa-pause-circle left-icon'
      }
    }    
  }
  
  // Set the icon of the big central play button on LISTEN-IN
  // all three buttons (small play, big play and console play) should be aligned
  const buttonPlayBig2 = document.querySelector(`.anvil-role-cap-play-spotify-button-big2`);

  if (controller.isPaused) {
    if (buttonPlayBig2) {
      let icon = buttonPlayBig2.querySelector('i')
      if (icon) {
        icon.className = 'anvil-component-icon left fa fa-play-circle left-icon'
      }
    }
  } else {
    if (buttonPlayBig2) {
      let icon = buttonPlayBig2.querySelector('i')
      if (icon) {
        icon.className = 'anvil-component-icon left fa fa-pause-circle left-icon'
      }
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
