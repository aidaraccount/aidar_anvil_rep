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
  console.log(options.uri);

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
        // console.log('Paused:', isPaused)
        // console.log('Buffering:', isBuffering)
        // console.log('Duration:', duration)
        // console.log('Position:', position)

        // Check if the song has ended
        if (!isPaused && position >= duration && duration > 0) {
          console.log("Track has ended. Moving to the next song.");
          playNextSong('track', artistSpotifyID); // Function to handle loading the next song
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
          // console.log('Paused:', isPaused)
          // console.log('Buffering:', isBuffering)
          // console.log('Duration:', duration)
          // console.log('Position:', position)

          // Check if the song has ended
          if (!isPaused && position >= duration && duration > 0) {
            console.log("Track has ended. Moving to the next song.");
            playNextSong('track', artistSpotifyID);; // Function to handle loading the next song
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
function playNextSong(trackOrArtist, artistSpotifyID) {
  // Update this logic to load the appropriate next song URI
  // const nextSongUri = getNextSongUri(); // Replace with your logic to fetch the next song's URI
  const nextSongUri = `spotify:track:${trackOrArtist}`; // Replace with your logic to fetch the next song's URI
  if (controller && nextSongUri) {
    controller.loadUri(nextSongUri);
    console.log(`Loading next song: ${nextSongUri}`);
    controller.play()
  } else {
    console.error("No next song URI available or controller is not initialized.");
  }
}




