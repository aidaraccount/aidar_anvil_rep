// window.addEventListener('load', function() {
var controller;
let globalCurrentArtistSpotifyID = null; // To persist the current track ID across function calls

// window.createOrUpdateSpotifyPlayer = function(trackOrArtist, currentArtistSpotifyID, spotifyTrackIDsList=null) {
function createOrUpdateSpotifyPlayer(trackOrArtist, currentArtistSpotifyID, spotifyTrackIDsList=null) {
  const element = document.querySelector('.anvil-role-spotify-footer-class #embed-iframe');
  const autoplaybutton = document.querySelector('.anvil-role-autoplay-toggle-button .fa-toggle-on')

  // check if the html for the player is imported (in the Discover Page)
  if (!element) {
    console.error("ERROR MESSAGE: Embed iframe element not found.")
    return;
  }

  globalCurrentArtistSpotifyID = currentArtistSpotifyID;

  // set the options for the Spotify Player
  const options = {
    theme: 'dark',
    width: '100%',
    height: '80',
    uri: `spotify:${trackOrArtist}:${globalCurrentArtistSpotifyID}`,
  };

  // console.log(`Initializing Spotify player with URI: ${options.uri}`);

  // the if statment checks if the SpotifyIgrameAPI already exists (if it is already loaded)
  if (window.SpotifyIframeAPI) {
    window.SpotifyIframeAPI.createController(element, options, (EmbedController) => {
      controller = EmbedController;
      controller.addListener('ready', () => {
        console.log('Spotify Player ready_1');
        if (autoplaybutton) {
          // The below line will activate playing music when the page is opened and the spotify player is built
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
            playNextSong('track', spotifyTrackIDsList); // Function to handle loading the next song
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
          setPlayButtonIcons(isPaused, trackOrArtist, spotifyTrackIDsList)
        } else {
          console.log("Playback is playing - 1");
          setPlayButtonIcons(isPaused, trackOrArtist, spotifyTrackIDsList)
        }
      });
      
    });
    
  } else {
    // if (controller) {
    //   controller.destroy(); // Clear the current controller to avoid mismatches
    // }
    window.onSpotifyIframeApiReady = (IFrameAPI) => {
      window.SpotifyIframeAPI = IFrameAPI; // Store the API globally for future use
      IFrameAPI.createController(element, options, (EmbedController) => {
        controller = EmbedController;
        controller.addListener('ready', () => {
          console.log('Spotify Player ready_2');
          if (autoplaybutton) {
            // The below line will activate playing music when the page is opened and the spotify player is built
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
              playNextSong('track', spotifyTrackIDsList); // Function to handle loading the next song
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
            setPlayButtonIcons(isPaused, trackOrArtist, spotifyTrackIDsList)
          } else {
            console.log("Playback is playing - 2");
            setPlayButtonIcons(isPaused, trackOrArtist, spotifyTrackIDsList)
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
// });


// Function to load the next song
function playNextSong(trackOrArtist, spotifyTrackIDsList, direction='forward') {
  
  // If statement to check if we are playing a list of custom songs or a playlist from Spotify
  if (!spotifyTrackIDsList) {
    console.error("No track list available. Check out Spotify_Player_js.js file - playNextSong() function.");
    return;
  }
  
  // Declaring the index of the current playing song and get the id for the next song to play
  const index = spotifyTrackIDsList.indexOf(globalCurrentArtistSpotifyID);
  let nextArtistSpotifyID = null;
  if (direction === 'forward') {
    nextArtistSpotifyID = index !== -1 && index < spotifyTrackIDsList.length - 1 ? spotifyTrackIDsList[index + 1] : null;
  } else if (direction === 'backward') {
    nextArtistSpotifyID = index !== -1 && index < spotifyTrackIDsList.length - 1 ? spotifyTrackIDsList[index - 1] : null;
  }

  // save the id to browser cache
  sessionStorage.setItem("lastplayedtrackid", nextArtistSpotifyID);
  sessionStorage.setItem("lastplayed", nextArtistSpotifyID);
  
  //  check if controller is instantiated and next song is define
  if (controller && nextArtistSpotifyID) {
    const nextSongUri = `spotify:${trackOrArtist}:${nextArtistSpotifyID}`; // Replace with your logic to fetch the next song's URI
    globalCurrentArtistSpotifyID = nextArtistSpotifyID;
    console.log("globalCurrentArtistSpotifyID of Next Song:", globalCurrentArtistSpotifyID)
    controller.loadUri(nextSongUri);
    console.log(`Loading next song: ${nextSongUri}`);
    controller.play()

    // Set play button icons
    setPlayButtonIcons(false, 'track', spotifyTrackIDsList)

  }
}

// Function to set the play button icons
function setPlayButtonIcons(isPaused, trackOrArtist, spotifyTrackIDsList=null) {
  
  // Set the icon of the small play buttons
  if (spotifyTrackIDsList) {
    spotifyTrackIDsList.forEach(function(currentId) {    
      const buttonPlay = document.querySelector(`.anvil-role-${currentId}`);
      
      if (currentId === globalCurrentArtistSpotifyID && !isPaused) {
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
  
}
