var controller;
let globalCurrentSpotifyID = null;

function createOrUpdateSpotifyPlayer(trackOrArtist, currentSpotifyID, spotifyTrackIDsList=null, spotifyArtistIDsList=null, spotifyArtistNameList=null) {
  const element = document.querySelector('.anvil-role-spotify-footer-class #embed-iframe');
  const autoplaybutton = document.querySelector('.anvil-role-autoplay-toggle-button .fa-toggle-on')

  // check if the html for the player is imported (in the Discover Page)
  if (!element) {
    console.error("ERROR MESSAGE: Embed iframe element not found.")
    return;
  }

  globalCurrentSpotifyID = currentSpotifyID;

  // set the options for the Spotify Player
  const options = {
    theme: 'dark',
    width: '100%',
    height: '80',
    uri: `spotify:${trackOrArtist}:${globalCurrentSpotifyID}`,
  };

  // the if statment checks if the SpotifyIgrameAPI already exists (if it is already loaded)
  if (window.SpotifyIframeAPI) {
    window.SpotifyIframeAPI.createController(element, options, (EmbedController) => {
      controller = EmbedController;
      controller.addListener('ready', () => {
        console.log('Spotify Player ready_1');
        if (autoplaybutton) {
          autoPlaySpotify();
        }
      });
      
      controller.addListener('playback_update', e => {
        const {isPaused, isBuffering, duration, position } = e.data;
        
        // Check if the song has ended
        if (!isPaused && position >= duration && duration > 0) {
          console.log("Track has ended. Moving to the next song.");

          // Load next song only if spotifyTrackIDsList is provided
          if (spotifyTrackIDsList) {
            playNextSong('track', spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList);
          } else {
            console.log("No track list provided. Playback stopped.")
          }
        }
      });
      
      controller.addListener('playback_update', e => {
        const {isPaused, isBuffering, duration, position } = e.data;
        
        // Log the current playback state
        if (isBuffering) {
          console.log("Playback is buffering - 1");
        } else if (isPaused) {
          console.log("Playback is paused - 1");
          setPlayButtonIcons(isPaused, trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList)
        } else {
          console.log("Playback is playing - 1");
          setPlayButtonIcons(isPaused, trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList)
        }
      });
      
    });
    
  } else {
    window.onSpotifyIframeApiReady = (IFrameAPI) => {
      window.SpotifyIframeAPI = IFrameAPI; // Store the API globally for future use
      IFrameAPI.createController(element, options, (EmbedController) => {
        controller = EmbedController;
        controller.addListener('ready', () => {
          console.log('Spotify Player ready_2');
          if (autoplaybutton) {
            autoPlaySpotify();
          }
        });
        
        controller.addListener('playback_update', e => {
          const { isPaused, isBuffering, duration, position } = e.data;
          
          // Check if the song has ended
          if (!isPaused && position >= duration && duration > 0) {
            console.log("Track has ended. Moving to the next song.");

            // Load next osng only if spotifyTrackIDsList is provided
            if (spotifyTrackIDsList) {
              playNextSong('track', spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList);
            } else {
              console.log("No track list provided. Playback stopped.");
            }
          }
        });
        
        controller.addListener('playback_update', e => {
          const {isPaused, isBuffering, duration, position } = e.data;
          
          // Log the current playback state
          if (isBuffering) {
            console.log("Playback is buffering - 2");
          } else if (isPaused) {
            console.log("Playback is paused - 2");
            setPlayButtonIcons(isPaused, trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList)
          } else {
            console.log("Playback is playing - 2");
            setPlayButtonIcons(isPaused, trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList)
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
function playNextSong(trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList=null, spotifyArtistNameList=null, direction='forward') {
  
  // If statement to check if we are playing a list of custom songs or a playlist from Spotify
  if (!spotifyTrackIDsList) {
    console.error("No track list available. Check out Spotify_Player_js.js file - playNextSong() function.");
    return;
  }
  
  // Declaring the index of the current playing song and get the id for the next song to play
  const index = spotifyTrackIDsList.indexOf(globalCurrentSpotifyID);
  let nextSpotifyTrackID = null;
  let nextSpotifyArtistID = null;
  let nextSpotifyArtistName = null;
  
  if (direction === 'initial') {
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
  }

  // save the id to browser cache
  sessionStorage.setItem("lastplayed", nextSpotifyTrackID);
  sessionStorage.setItem("lastplayedtrackid", nextSpotifyTrackID);
  if (spotifyArtistIDsList) {
    sessionStorage.setItem("lastplayedartistid", nextSpotifyArtistID)
  }
  
  //  check if controller is instantiated and next song is define
  if (controller && nextSpotifyTrackID) {
    const nextSongUri = `spotify:${trackOrArtist}:${nextSpotifyTrackID}`;
    globalCurrentSpotifyID = nextSpotifyTrackID;
    controller.loadUri(nextSongUri);
    
    // Check if the artist has changed to read their name
    // Version 1: start player when speech is over
    // const currentArtistID = spotifyArtistIDsList ? spotifyArtistIDsList[index] : null;    
    // if (nextSpotifyArtistID && (currentArtistID !== nextSpotifyArtistID || sessionStorage.getItem("has_played") === 'False')) {
    //   speakText(`...Presenting, ${nextSpotifyArtistName}!`, () => {
    //     controller.play();
    //   });
    // } else {
    //   controller.play();
    // }
    
    // Version 2: start player imediatelly
    const currentArtistID = spotifyArtistIDsList ? spotifyArtistIDsList[index] : null;    
    if (nextSpotifyArtistID && (currentArtistID !== nextSpotifyArtistID || sessionStorage.getItem("has_played") === 'False')) {
      speakText(`...Presenting, ${nextSpotifyArtistName}!`)
    }
    controller.play();
    
    // Set play button icons
    setPlayButtonIcons(false, 'track', spotifyTrackIDsList, spotifyArtistIDsList)

  }
}

// Function to set the play button icons
function setPlayButtonIcons(isPaused, trackOrArtist, spotifyTrackIDsList=null, spotifyArtistIDsList=null) {
  
  // Set the icon of the small play buttons
  if (spotifyTrackIDsList) {
    spotifyTrackIDsList.forEach(function(currentId) {    
      const buttonPlay = document.querySelector(`.anvil-role-${currentId}`);
      
      if (currentId === globalCurrentSpotifyID && !isPaused) {
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
    })
  }
  
  // Set the icon of the big central play button on DISCOVER
  // should be play when nothing is playling to start the artists tracks
  const buttonPlayBig = document.querySelector(`.anvil-role-play-spotify-button-artist`);

  if (isPaused) {
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
  if (trackOrArtist ==  'artist' && !isPaused) {
    if (buttonPlayBig) {
      let icon = buttonPlayBig.querySelector('i')
      if (icon) {
        icon.className = 'anvil-component-icon left fa fa-pause-circle left-icon'
      }
    }    
  }
  
  // Set the icon of the big central play button on LISTEN-IN
  // all three buttons (small play, big play and console play) should be aligned
  const buttonPlayBig2 = document.querySelector(`.anvil-role-play-spotify-button-artist2`);

  if (isPaused) {
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
    
    const buttonBackward = document.querySelector(`.anvil-role-backward-button`);
    if (buttonBackward) {
     if (globalCurrentSpotifyID === spotifyTrackIDsList[0]) {
        buttonBackward.classList.remove('anvil-role-icon-button');
        buttonBackward.classList.add('anvil-role-icon-button-disabled');
      } else {
        buttonBackward.classList.remove('anvil-role-icon-button-disabled');
        buttonBackward.classList.add('anvil-role-icon-button');
      }
    }

    const buttonForward = document.querySelector(`.anvil-role-forward-button`);
    if (buttonForward) {
      if (globalCurrentSpotifyID === spotifyTrackIDsList[spotifyTrackIDsList.length - 1]) {
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
    const buttonFastBackward = document.querySelector(`.anvil-role-fast-backward-button`);
    if (buttonFastBackward) {
      // Check if there is a previous artist
      const currentArtistIndex = spotifyTrackIDsList.indexOf(globalCurrentSpotifyID);
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
  
    const buttonFastForward = document.querySelector(`.anvil-role-fast-forward-button`);
    if (buttonFastForward) {
      // Check if there is a next artist
      const currentArtistIndex = spotifyTrackIDsList.indexOf(globalCurrentSpotifyID);
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
