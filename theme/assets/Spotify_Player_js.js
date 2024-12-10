// window.addEventListener('load', function() {
var controller;

function createOrUpdateSpotifyPlayer(trackOrArtist, artistSpotifyID) {
  const element = document.querySelector('.anvil-role-spotify-footer-class #embed-iframe');
  const autoplaybutton = document.querySelector('.anvil-role-autoplay-toggle-button .fa-toggle-on')
  // console.log("THIS IS THE ELEMENT:", element)
  // console.log("THIS IS THE AUTOPLAY BUTTON ELEMENT:", autoplaybutton)
  
  if (!element) {
    console.error("ERROR MESSAGE: Embed iframe element not found.")
    return;
  }
  
  // console.log(artistSpotifyID);
  
  const options = {
    theme: 'dark',
    width: '100%',
    height: '80',
    uri: `spotify:${trackOrArtist}:${artistSpotifyID}`,
  };
  // console.log(options);

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
      // Listen for state changes
      controller.addListener('player_state_changed', ({ position, duration, track_window: { current_track } }) => {
        console.log('Currently Playing:', current_track);
        console.log('Position in Song:', position);
        console.log('Duration of Song:', duration);

        // Check if the song has ended
        if (position === 0 && current_track && duration > 0) {
          console.log("Track has ended. Moving to the next song.");
          // playNextSong();
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

        // Listen for state changes
        controller.addListener('player_state_changed', ({ position, duration, track_window: { current_track } }) => {
          console.log('Currently Playing:', current_track);
          console.log('Position in Song:', position);
          console.log('Duration of Song:', duration);

          if (position === 0 && current_track && duration > 0) {
            console.log("Track has ended. Moving to the next song.");
            // playNextSong();
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
    console.log("NOTTTTTTTTTT OKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK 222222222222222222")
    console.error("Spotify controller is not initialized.");
  }
}
// });

