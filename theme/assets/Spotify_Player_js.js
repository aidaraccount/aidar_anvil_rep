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
    console.log('Spotify API is being initialized...1')
    window.SpotifyIframeAPI.createController(element, options, (EmbedController) => {
      controller = EmbedController;
      controller.addListener('ready', () => {
        console.log('Spotify Player ready_1');
        console.log('line 31 - before current state')
        current_state()
        console.log('line 33 - after current state')
        if (autoplaybutton) {
          // The below line will activate playing music when the page is opened and the spotify player is built
          playSpotify_2();
          console.log('line 37 - before current state')
          current_state()
          console.log('line 39 - after current state')
        }
      });
      // Listen for state changes
      // controller.addListener('player_state_changed', ({ position, duration, track_window: { current_track } }) => {
      //   console.log('Currently Playing:', current_track);
      //   console.log('Position in Song:', position);
      //   console.log('Duration of Song:', duration);

      //   // Check if the song has ended
      //   if (position === 0 && current_track && duration > 0) {
      //     console.log("Track has ended. Moving to the next song.");
      //     // playNextSong();
      //   }
      // });
    });
  } else {
    console.log('Spotify API is being initialized...2')
    window.onSpotifyIframeApiReady = (IFrameAPI) => {
      window.SpotifyIframeAPI = IFrameAPI; // Store the API globally for future use
      IFrameAPI.createController(element, options, (EmbedController) => {
        controller = EmbedController;
        controller.addListener('ready', () => {
          console.log('Spotify Player ready_2');
          console.log('line 63 - before current state')
          current_state()
          console.log('line 65 - after current state')
          if (autoplaybutton) {
            // The below line will activate playing music when the page is opened and the spotify player is built
            playSpotify_2();
            console.log('line 66 - before current state')
            current_state()
            console.log('line 68 - after current state')
          }
        });

        // Listen for state changes
        // controller.addListener('player_state_changed', ({ position, duration, track_window: { current_track } }) => {
        //   console.log('Currently Playing:', current_track);
        //   console.log('Position in Song:', position);
        //   console.log('Duration of Song:', duration);

        //   if (position === 0 && current_track && duration > 0) {
        //     console.log("Track has ended. Moving to the next song.");
        //     // playNextSong();
        //   }
        // });
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
function current_state() {
  controller.addListener('player_state_changed', (state) => {
    console.log("player_state_changed triggered!");
    console.log(state); // Log the entire state object
    const { position, duration, track_window: { current_track } } = state;
  
    if (position === 0 && current_track && duration > 0) {
      console.log("Track has ended. Moving to the next song.");
      // playNextSong();
    }
  });
}


controller.getCurrentState().then((state) => {
  if (!state) {
    console.log("User is not playing music through the Web Playback SDK");
  } else {
    console.log("Current state:", state);
  }
}).catch((err) => {
  console.error("Error getting current state:", err);
});

controller.addListener('initialization_error', ({ message }) => {
  console.error('Initialization error:', message);
});
controller.addListener('authentication_error', ({ message }) => {
  console.error('Authentication error:', message);
});
controller.addListener('account_error', ({ message }) => {
  console.error('Account error:', message);
});
controller.addListener('playback_error', ({ message }) => {
  console.error('Playback error:', message);
});
