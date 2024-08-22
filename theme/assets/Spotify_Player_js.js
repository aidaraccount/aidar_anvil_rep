// window.addEventListener('load', function() {
var controller;

function createOrUpdateSpotifyPlayer(trackOrArtist, artistSpotifyID) {
  const element = document.querySelector('.anvil-role-spotify-footer-class #embed-iframe');
    
  if (!element) {
    console.error("ERROR MESSAGE: Embed iframe element not found.")
    return;
  }
    
  console.log("THIS IS THE ELEMENT:", element);
  console.log(artistSpotifyID);
  
  const options = {
    theme: 'dark',
    width: '100%',
    height: '80',
    uri: `spotify:${trackOrArtist}:${artistSpotifyID}`,
  };
  console.log(options);

  if (window.SpotifyIframeAPI) {
    window.SpotifyIframeAPI.createController(element, options, (EmbedController) => {
      controller = EmbedController;
      controller.addListener('ready', () => {
        console.log('Spotify Player ready');
      });
    });
  } else {
    window.onSpotifyIframeApiReady = (IFrameAPI) => {
      window.SpotifyIframeAPI = IFrameAPI; // Store the API globally for future use
      IFrameAPI.createController(element, options, (EmbedController) => {
        controller = EmbedController;
        controller.addListener('ready', () => {
          console.log('Spotify Player ready');
        });
      });
    };
  }
}

// });
