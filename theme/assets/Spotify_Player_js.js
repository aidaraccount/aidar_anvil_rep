// window.addEventListener('load', function() {
var controller;
let globalCurrentArtistSpotifyID = null; // To persist the current track ID across function calls

function createSpotifyController(trackOrArtist, element, autoplaybutton, spotifyTrackIDsList, IFrameAPI) {
  if (controller) {
    controller.destroy(); // Ensure we start clean
    controller = null;
    console.log('the controller has been destroyed')
  }

  console.log("Track or Artist",trackOrArtist)
  console.log("URI song:", globalCurrentArtistSpotifyID)
  
  const options = {
    theme: 'dark',
    width: '100%',
    height: '80',
    uri: `spotify:${trackOrArtist}:${globalCurrentArtistSpotifyID}`,
  };

  IFrameAPI.createController(element, options, (EmbedController) => {
    controller = EmbedController;

    controller.addListener('ready', () => {
      console.log('Spotify Player Ready');
      if (autoplaybutton) {
        playSpotify_2();
      }
    });

    controller.addListener('playback_update', e => {
      const {isPaused, duration, position} = e.data;

      if (!isPaused && position >= duration && duration > 0) {
        console.log('Track has ended. Moving to the next song.');
        if (spotifyTrackIDsList) {
          playNextSong('track', spotifyTrackIDsList);
        } else {
          console.log('No track list provided. Playback stopped.');
        }
      }
    });
  })
}

function createOrUpdateSpotifyPlayer(trackOrArtist, currentArtistSpotifyID, spotifyTrackIDsList=null) {
  const element = document.querySelector('.anvil-role-spotify-footer-class #embed-iframe');
  const autoplaybutton = document.querySelector('.anvil-role-autoplay-toggle-button .fa-toggle-on')
  
  if (!element) {
    console.error("ERROR MESSAGE: Embed iframe element not found.")
    return;
  }

  globalCurrentArtistSpotifyID = currentArtistSpotifyID;

  // the if statment checks if the SpotifyIgrameAPI already exists (if it is already loaded)
  if (window.SpotifyIframeAPI) {
    console.log("createOrUpdateSpotifyPlayer", "Scenario IF 1")
    createSpotifyController(trackOrArtist, element, autoplaybutton, spotifyTrackIDsList, window.SpotifyIframeAPI)
  } else {
    console.log("createOrUpdateSpotifyPlayer", "Scenario IF 2")
    if (!window.onSpotifyIframeApiReady) {
      console.log("createOrUpdateSpotifyPlayer", "Scenario IF 3")
      window.onSpotifyIframeApiReady = (IFrameAPI) => {
        window.SpotifyIframeAPI = IFrameAPI;
        createSpotifyController(trackOrArtist, element, autoplaybutton, spotifyTrackIDsList, IFrameAPI);
      };
    }
  }
}

function playSpotify_2() {
  if (controller) {
    console.log("SPOTIFY PLAYER PLAYSPOTIFY_2 FUNCTION IS RUN")
    // Check the playback state and decide what to do
    if (controller.isPaused) {
      console.log("SPOTIFY PLAYER PLAYSPOTIFY_2 FUNCTION IS RUN")
      controller.resume();  // Resume playing from the paused position
      controller.isPlaying = true;
      controller.isPaused = false;
    } else if (!controller.isPlaying) {
      console.log("SPOTIFY PLAYER PLAYSPOTIFY_2 FUNCTION IS RUN")
      controller.play();    // Start playing if not already playing
      controller.isPlaying = true;
      controller.isPaused = false;
    }
  } else {
    console.log("SPOTIFY PLAYER PLAYSPOTIFY_2 FUNCTION IS RUN")
    console.error("Spotify controller is not initialized.");
  }
}
// });

// Function to load the next song
function playNextSong(trackOrArtist, spotifyTrackIDsList) {
  // If statement to check if we are playing a list of custom songs or a playlist from Spotify
  if (!spotifyTrackIDsList) {
    console.error("No track list available. Check out Spotify_Player_js.js file - playNextSong() function.");
    return;
  }
  // Declaring the index of the current playing song and defining the index for the next song to play
  const index = spotifyTrackIDsList.indexOf(globalCurrentArtistSpotifyID);
  const nextArtistSpotifyID = index !== -1 && index < spotifyTrackIDsList.length - 1 ? spotifyTrackIDsList[index + 1] : null;
  //  check if controller is instantiated and next song is define
  if (controller && nextArtistSpotifyID) {
    const nextSongUri = `spotify:${trackOrArtist}:${nextArtistSpotifyID}`; // Replace with your logic to fetch the next song's URI
    globalCurrentArtistSpotifyID = nextArtistSpotifyID;
    console.log("globalCurrentArtistSpotifyID of Next Song:", globalCurrentArtistSpotifyID)
    controller.loadUri(nextSongUri);
    console.log(`Loading next song: ${nextSongUri}`);
    controller.play()

    // For loop to change the icon of the play button. 
    spotifyTrackIDsList.forEach(function(currentId) {
      const buttonPlay = document.querySelector(`.anvil-role-${currentId}`);
      // console.log("Button PLAY HTML", buttonPlay)
      if (currentId === globalCurrentArtistSpotifyID) {
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
    
  // Text box test
  const nowPlayingBox = document.querySelector('.anvil-role-now-playing-id');
  if (nowPlayingBox) {
    nowPlayingBox.value = globalCurrentArtistSpotifyID;
    console.log("nowPlayingBox_value in the nextupsong:", nowPlayingBox.value)
  }
  } else {
    console.error("No next song URI available or controller is not initialized.");
  }
}




