/**
 * Spotify Player Integration - Authorization Code Flow
 * Clean, minimal implementation for AIDAR app
 * Maintains backward compatibility with existing function calls
 */

// 1. Main player initialization function (backward compatible)
function createOrUpdateSpotifyPlayer(formElement, trackOrArtist, currentSpotifyID, spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList) {
  console.log('[SpotifyPlayer] Initializing player for:', trackOrArtist, currentSpotifyID);
  
  // Check if user is authenticated
  if (!window.SpotifyWebPlayback.checkAuth()) {
    console.log('[SpotifyPlayer] No authentication, showing auth prompt');
    showAuthPrompt();
    return;
  }
  
  // If authenticated and SDK is ready, play the track
  if (window.SpotifyWebPlayback.isReady()) {
    playTrackWithSDK(currentSpotifyID);
  } else {
    // Wait for SDK to be ready
    setTimeout(() => {
      if (window.SpotifyWebPlayback.isReady()) {
        playTrackWithSDK(currentSpotifyID);
      }
    }, 2000);
  }
  
  // Update session storage for compatibility
  sessionStorage.setItem("globalCurrentSpotifyID", currentSpotifyID);
  sessionStorage.setItem("globalTrackOrArtist", trackOrArtist);
}

// 2. Play track using Web Playback SDK
function playTrackWithSDK(spotifyId) {
  if (!spotifyId) {
    console.error('[SpotifyPlayer] No Spotify ID provided');
    return;
  }
  
  console.log('[SpotifyPlayer] Playing track:', spotifyId);
  window.SpotifyWebPlayback.playTrack(spotifyId);
}

// 3. Show authentication prompt
function showAuthPrompt() {
  const container = document.querySelector('.anvil-role-cap-spotify-footer');
  if (!container) {
    console.error('[SpotifyPlayer] Spotify container not found');
    return;
  }
  
  container.innerHTML = `
    <div class="spotify-web-player">
      <div class="spotify-auth-section">
        <div class="spotify-connect-prompt">
          <h3>Connect to Spotify</h3>
          <p>Connect your Spotify Premium account for seamless music playback</p>
          <button class="spotify-auth-button" onclick="window.SpotifyWebPlayback.authenticate()">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.42 1.56-.299.421-1.02.599-1.559.3z"/>
            </svg>
            Connect Spotify Premium
          </button>
        </div>
      </div>
      
      <div class="spotify-player-section" id="spotify-player-section" style="display: none;">
        <div class="spotify-track-info">
          <div class="spotify-track-details">
            <div class="spotify-track-name">No track selected</div>
            <div class="spotify-artist-name">Select a track to play</div>
          </div>
        </div>
        
        <div class="spotify-controls">
          <button class="spotify-control-button" onclick="window.SpotifyWebPlayback.previous()" title="Previous">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M3.3 1a.7.7 0 0 1 .7.7v5.15l9.95-5.744a.7.7 0 0 1 1.05.606v12.588a.7.7 0 0 1-1.05.606L4 8.149V13.3a.7.7 0 0 1-1.4 0V1.7a.7.7 0 0 1 .7-.7z"/>
            </svg>
          </button>
          
          <button class="spotify-play-button spotify-control-button" onclick="window.SpotifyWebPlayback.toggle()" title="Play/Pause">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" class="play-icon">
              <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/>
            </svg>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" class="pause-icon" style="display: none;">
              <path d="M5.5 3.5A1.5 1.5 0 0 1 7 2h1.5a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 8.5 14H7a1.5 1.5 0 0 1-1.5-1.5v-9zM2.5 3.5A1.5 1.5 0 0 1 4 2h1.5a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 5.5 14H4a1.5 1.5 0 0 1-1.5-1.5v-9z"/>
            </svg>
          </button>
          
          <button class="spotify-control-button" onclick="window.SpotifyWebPlayback.next()" title="Next">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M12.7 1a.7.7 0 0 0-.7.7v5.15L2.05 1.107A.7.7 0 0 0 1 1.712v12.588a.7.7 0 0 0 1.05.606L12 8.149V13.3a.7.7 0 0 0 1.4 0V1.7a.7.7 0 0 0-.7-.7z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <style>
    .spotify-web-player {
      background: linear-gradient(135deg, #1db954 0%, #1ed760 100%);
      border-radius: 12px;
      padding: 20px;
      color: white;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      box-shadow: 0 8px 32px rgba(29, 185, 84, 0.3);
      margin: 16px 0;
    }
    .spotify-auth-section {
      text-align: center;
    }
    .spotify-connect-prompt h3 {
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 600;
    }
    .spotify-connect-prompt p {
      margin: 0 0 20px 0;
      opacity: 0.9;
      font-size: 14px;
    }
    .spotify-auth-button {
      background: rgba(255, 255, 255, 0.2);
      border: 2px solid rgba(255, 255, 255, 0.3);
      color: white;
      padding: 12px 24px;
      border-radius: 50px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.3s ease;
    }
    .spotify-auth-button:hover {
      background: rgba(255, 255, 255, 0.3);
      border-color: rgba(255, 255, 255, 0.5);
      transform: translateY(-2px);
    }
    .spotify-player-section {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .spotify-track-info {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .spotify-track-details {
      flex: 1;
    }
    .spotify-track-name {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 4px;
    }
    .spotify-artist-name {
      font-size: 14px;
      opacity: 0.8;
    }
    .spotify-controls {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 16px;
    }
    .spotify-control-button {
      background: rgba(255, 255, 255, 0.2);
      border: none;
      color: white;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .spotify-control-button:hover {
      background: rgba(255, 255, 255, 0.3);
      transform: scale(1.1);
    }
    .spotify-play-button {
      width: 48px;
      height: 48px;
      background: white;
      color: #1db954;
    }
    .spotify-play-button:hover {
      background: rgba(255, 255, 255, 0.9);
      transform: scale(1.1);
    }
    </style>
  `;
}

// 4. Legacy compatibility functions
function setPlayButtonIcons(trackOrArtist, spotifyTrackIDsList = null, spotifyArtistIDsList = null) {
  // This function is called by existing code to update UI
  // In the new implementation, UI updates are handled automatically by the SDK
  console.log('[SpotifyPlayer] setPlayButtonIcons called (handled by SDK)');
}

// Legacy playSpotify function for backward compatibility
function playSpotify() {
  console.log('[SpotifyPlayer] Legacy playSpotify() called');
  
  // Get the current Spotify ID from session storage (set by createOrUpdateSpotifyPlayer)
  const currentSpotifyID = sessionStorage.getItem("globalCurrentSpotifyID");
  const trackOrArtist = sessionStorage.getItem("globalTrackOrArtist");
  
  if (!currentSpotifyID) {
    console.warn('[SpotifyPlayer] No current Spotify ID found in session storage');
    return;
  }
  
  // Check if user is authenticated
  if (!window.SpotifyWebPlayback.checkAuth()) {
    console.log('[SpotifyPlayer] No authentication, showing auth prompt');
    showAuthPrompt();
    return;
  }
  
  // Play the track
  playTrackWithSDK(currentSpotifyID);
}

// Legacy autoPlaySpotify function for backward compatibility
function autoPlaySpotify() {
  console.log('[SpotifyPlayer] Legacy autoPlaySpotify() called');
  
  // Check if autoplay toggle is enabled
  const autoplayButton = document.querySelector('.anvil-role-cap-autoplay-toggle-button .fa-toggle-on');
  if (!autoplayButton) {
    console.log('[SpotifyPlayer] Autoplay is disabled');
    return;
  }
  
  // Use the same logic as playSpotify
  playSpotify();
}

// Legacy playNextSong function for backward compatibility
function playNextSong(formElement, trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList, direction = 'forward') {
  console.log('[SpotifyPlayer] Legacy playNextSong() called with direction:', direction);
  
  if (!spotifyTrackIDsList || spotifyTrackIDsList.length === 0) {
    console.error('[SpotifyPlayer] No track list provided for playNextSong');
    return;
  }
  
  const currentSpotifyID = sessionStorage.getItem("globalCurrentSpotifyID");
  const currentIndex = spotifyTrackIDsList.indexOf(currentSpotifyID);
  
  let nextIndex = 0;
  
  // Determine next track based on direction
  switch (direction) {
    case 'initial':
      nextIndex = 0;
      break;
    case 'forward':
      nextIndex = currentIndex < spotifyTrackIDsList.length - 1 ? currentIndex + 1 : 0;
      break;
    case 'backward':
      nextIndex = currentIndex > 0 ? currentIndex - 1 : spotifyTrackIDsList.length - 1;
      break;
    case 'fast-forward':
    case 'fast-backward':
      // For fast navigation, find next/previous artist
      if (spotifyArtistIDsList && spotifyArtistIDsList.length > 0) {
        const currentArtistID = spotifyArtistIDsList[currentIndex];
        if (direction === 'fast-forward') {
          for (let i = currentIndex + 1; i < spotifyArtistIDsList.length; i++) {
            if (spotifyArtistIDsList[i] !== currentArtistID) {
              nextIndex = i;
              break;
            }
          }
        } else {
          for (let i = currentIndex - 1; i >= 0; i--) {
            if (spotifyArtistIDsList[i] !== currentArtistID) {
              nextIndex = i;
              break;
            }
          }
        }
      } else {
        nextIndex = direction === 'fast-forward' ? 
          Math.min(currentIndex + 5, spotifyTrackIDsList.length - 1) : 
          Math.max(currentIndex - 5, 0);
      }
      break;
  }
  
  const nextSpotifyID = spotifyTrackIDsList[nextIndex];
  
  // Update session storage
  sessionStorage.setItem("globalCurrentSpotifyID", nextSpotifyID);
  sessionStorage.setItem("lastplayedtrackid", nextSpotifyID);
  
  if (spotifyArtistIDsList && spotifyArtistIDsList[nextIndex]) {
    sessionStorage.setItem("lastplayedartistid", spotifyArtistIDsList[nextIndex]);
  }
  
  // Play the next track
  if (window.SpotifyWebPlayback.checkAuth()) {
    playTrackWithSDK(nextSpotifyID);
  } else {
    showAuthPrompt();
  }
}

// 5. Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  // Check if user is already authenticated
  setTimeout(() => {
    if (window.SpotifyWebPlayback && window.SpotifyWebPlayback.checkAuth()) {
      console.log('[SpotifyPlayer] User already authenticated');
    }
  }, 1000);
});

console.log('[SpotifyPlayer] Clean Authorization Code Flow integration loaded');
