// window.addEventListener('load', function() {
var controller;
let globalCurrentArtistSpotifyID = null; // To persist the current track ID across function calls

function createOrUpdateSpotifyPlayer(trackOrArtist, currentArtistSpotifyID, spotifyTrackIDsList=null) {
  const element = document.querySelector('.anvil-role-spotify-footer-class #embed-iframe');
  const autoplaybutton = document.querySelector('.anvil-role-autoplay-toggle-button .fa-toggle-on')
  // console.log("THIS IS THE ELEMENT:", element)
  // console.log("THIS IS THE AUTOPLAY BUTTON ELEMENT:", autoplaybutton)
  
  if (!element) {
    console.error("ERROR MESSAGE: Embed iframe element not found.")
    return;
  }

  console.log("Global Current Artist Spotify ID BEFORE", globalCurrentArtistSpotifyID);
  console.log("Check", !globalCurrentArtistSpotifyID);
  // if (!globalCurrentArtistSpotifyID) {
  //   // Initialize globalCurrentArtistSpotifyID only if it hasn't been set
  //   globalCurrentArtistSpotifyID = currentArtistSpotifyID;
  // } else {
  //   globalCurrentArtistSpotifyID = currentArtistSpotifyID;
  // }
  globalCurrentArtistSpotifyID = currentArtistSpotifyID;
  
  console.log("track or artist", trackOrArtist);
  console.log("Current Spotify ID", currentArtistSpotifyID);
  console.log("Global Current Spotify ID", globalCurrentArtistSpotifyID);

  // Update the hidden text box with the new ID
  const nowPlayingBox = document.querySelector('.anvil-role-now-playing-id');
  if (nowPlayingBox) {
    nowPlayingBox.value = globalCurrentArtistSpotifyID;
    console.log("nowPlayingBox_value:", nowPlayingBox)
    console.log("nowPlayingBox_value:", nowPlayingBox.value)
  }

  const buttonPlay = document.querySelector('.anvil-role-button-custom-class-test');
  console.log("This is the buttonPlay", buttonPlay)
  if (buttonPlay) {
    let icon = buttonPlay.querySelector('i')
    if (icon) {
    icon.className = 'anvil-component-icon left fa fa-pause-circle left-icon'
    }
  }
  
  const options = {
    theme: 'dark',
    width: '100%',
    height: '80',
    uri: `spotify:${trackOrArtist}:${globalCurrentArtistSpotifyID}`,
  };
  // console.log(options.uri);

  if (window.SpotifyIframeAPI) {
    window.SpotifyIframeAPI.createController(element, options, (EmbedController) => {
      controller = EmbedController;
      controller.addListener('ready', () => {
        console.log('Spotify Player ready_1');
        if (autoplaybutton) {
          // The below line will activate playing music when the page is opened and the spotify player is built
          playSpotify_2();
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
    });
  } else {
    window.onSpotifyIframeApiReady = (IFrameAPI) => {
      window.SpotifyIframeAPI = IFrameAPI; // Store the API globally for future use
      IFrameAPI.createController(element, options, (EmbedController) => {
        controller = EmbedController;
        controller.addListener('ready', () => {
          console.log('Spotify Player ready_2');
          if (autoplaybutton) {
            // The below line will activate playing music when the page is opened and the spotify player is built
            playSpotify_2();
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
      }); 
    };
  }
}

function playSpotify_2() {
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
function playNextSong(trackOrArtist, spotifyTrackIDsList) {
  if (!spotifyTrackIDsList) {
    console.error("No track list available. Check out Spotify_Player_js.js file - playNextSong() function.");
    return;
  }
  const index = spotifyTrackIDsList.indexOf(globalCurrentArtistSpotifyID);
  const nextArtistSpotifyID = index !== -1 && index < spotifyTrackIDsList.length - 1 ? spotifyTrackIDsList[index + 1] : null;
  if (controller && nextArtistSpotifyID) {
    const nextSongUri = `spotify:${trackOrArtist}:${nextArtistSpotifyID}`; // Replace with your logic to fetch the next song's URI
    globalCurrentArtistSpotifyID = nextArtistSpotifyID;
    console.log("globalCurrentArtistSpotifyID of Next Song:", globalCurrentArtistSpotifyID)
    controller.loadUri(nextSongUri);
    console.log(`Loading next song: ${nextSongUri}`);
    controller.play()

  const nowPlayingBox = document.querySelector('.anvil-role-now-playing-id');
  if (nowPlayingBox) {
    nowPlayingBox.value = globalCurrentArtistSpotifyID;
    console.log("nowPlayingBox_value in the nextupsong:", nowPlayingBox.value)
  }
  } else {
    console.error("No next song URI available or controller is not initialized.");
  }
}




