/**
 * Modern Spotify Web Playback SDK Integration
 * Replaces the legacy iframe-based player with proper SDK control
 * Provides seamless integration with existing AIDAR codebase
 */

// Import the Web Playback SDK functionality
if (typeof window.SpotifyWebPlayback === 'undefined') {
  // Load the Web Playback SDK module
  const script = document.createElement('script');
  script.src = '/theme/assets/Spotify_WebPlayback.js';
  script.async = true;
  document.head.appendChild(script);
}

// 1. Modern replacement for createOrUpdateSpotifyPlayer
function createOrUpdateSpotifyPlayer(formElement, trackOrArtist, currentSpotifyID, spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList) {
  console.log('[SpotifyModern] Initializing modern Spotify player...');
  
  // Check if user is authenticated with Spotify
  const token = localStorage.getItem('spotify_access_token');
  
  if (!token) {
    console.log('[SpotifyModern] No authentication token found, requesting login...');
    showSpotifyAuthPrompt();
    return;
  }
  
  // Initialize Web Playback SDK if not ready
  if (!window.SpotifyWebPlayback || !window.SpotifyWebPlayback.isReady()) {
    console.log('[SpotifyModern] Initializing Web Playback SDK...');
    window.SpotifyWebPlayback.initialize(token);
    
    // Wait for initialization and then play
    setTimeout(() => {
      if (window.SpotifyWebPlayback.isReady()) {
        playTrackWithWebSDK(trackOrArtist, currentSpotifyID, spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList);
      }
    }, 2000);
  } else {
    // SDK is ready, play immediately
    playTrackWithWebSDK(trackOrArtist, currentSpotifyID, spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList);
  }
}

// 2. Play track using Web Playback SDK
function playTrackWithWebSDK(trackOrArtist, currentSpotifyID, spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList) {
  console.log(`[SpotifyModern] Playing ${trackOrArtist}: ${currentSpotifyID}`);
  
  // Update session storage
  sessionStorage.setItem("globalCurrentSpotifyID", currentSpotifyID);
  
  // Use Web Playback SDK to play
  window.SpotifyWebPlayback.play(
    trackOrArtist, 
    currentSpotifyID, 
    spotifyTrackIDsList, 
    spotifyArtistIDsList, 
    spotifyArtistNameList
  );
  
  // Update UI to show player section
  showSpotifyPlayerUI();
}

// 3. Show authentication prompt
function showSpotifyAuthPrompt() {
  const container = document.querySelector('.anvil-role-cap-spotify-footer');
  if (!container) {
    console.error('[SpotifyModern] Spotify container not found');
    return;
  }
  
  // Embed the UI directly instead of fetching it
  const spotifyUI = `
    <div class="spotify-web-player" id="spotify-web-player">
      <!-- Authentication Section -->
      <div class="spotify-auth-section" id="spotify-auth-section">
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

      <!-- Player Section -->
      <div class="spotify-player-section" id="spotify-player-section" style="display: none;">
        <!-- Track Info -->
        <div class="spotify-track-info">
          <div class="spotify-track-details">
            <div class="spotify-track-name">No track selected</div>
            <div class="spotify-artist-name">Select a track to play</div>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="spotify-progress-container">
          <div class="spotify-progress-bar">
            <div class="spotify-progress" style="width: 0%;"></div>
          </div>
          <div class="spotify-time-info">
            <span class="spotify-current-time">0:00</span>
            <span class="spotify-total-time">0:00</span>
          </div>
        </div>

        <!-- Controls -->
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

        <!-- Volume Control -->
        <div class="spotify-volume-container">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M10.717 3.55A.5.5 0 0 1 11 4v8a.5.5 0 0 1-.812.39L7.825 10.5H5.5A.5.5 0 0 1 5 10V6a.5.5 0 0 1 .5-.5h2.325l2.363-1.89a.5.5 0 0 1 .529-.06z"/>
            <path d="M11.536 14.01A8.473 8.473 0 0 0 14.026 8a8.473 8.473 0 0 0-2.49-6.01l-.708.707A7.476 7.476 0 0 1 13.025 8c0 2.071-.84 3.946-2.197 5.303l.708.707z"/>
            <path d="M10.121 12.596A6.48 6.48 0 0 0 12.025 8a6.48 6.48 0 0 0-1.904-4.596l-.707.707A5.483 5.483 0 0 1 11.025 8a5.483 5.483 0 0 1-1.61 3.89l.706.706z"/>
          </svg>
          <input type="range" class="spotify-volume-slider" min="0" max="100" value="80" 
                 onchange="window.SpotifyWebPlayback.setVolume(this.value / 100)">
        </div>
      </div>

      <!-- Messages Section -->
      <div class="spotify-message" id="spotify-message"></div>
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
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .spotify-artist-name {
      font-size: 14px;
      opacity: 0.8;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .spotify-progress-container {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .spotify-progress-bar {
      height: 4px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 2px;
      overflow: hidden;
    }

    .spotify-progress {
      height: 100%;
      background: white;
      border-radius: 2px;
      transition: width 0.3s ease;
    }

    .spotify-time-info {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
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

    .spotify-volume-container {
      display: flex;
      align-items: center;
      gap: 8px;
      justify-content: center;
    }

    .spotify-volume-slider {
      width: 80px;
      height: 4px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 2px;
      outline: none;
      -webkit-appearance: none;
    }

    .spotify-volume-slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 12px;
      height: 12px;
      background: white;
      border-radius: 50%;
      cursor: pointer;
    }

    .spotify-volume-slider::-moz-range-thumb {
      width: 12px;
      height: 12px;
      background: white;
      border-radius: 50%;
      cursor: pointer;
      border: none;
    }

    @media (max-width: 480px) {
      .spotify-web-player {
        padding: 16px;
      }
      
      .spotify-controls {
        gap: 12px;
      }
      
      .spotify-control-button {
        width: 36px;
        height: 36px;
      }
      
      .spotify-play-button {
        width: 44px;
        height: 44px;
      }
    }
    </style>
  `;
  
  container.innerHTML = spotifyUI;
  
  // Show auth section
  const authSection = document.getElementById('spotify-auth-section');
  const playerSection = document.getElementById('spotify-player-section');
  
  if (authSection) authSection.style.display = 'block';
  if (playerSection) playerSection.style.display = 'none';
}

// 4. Show player UI after authentication
function showSpotifyPlayerUI() {
  const authSection = document.getElementById('spotify-auth-section');
  const playerSection = document.getElementById('spotify-player-section');
  
  if (authSection) authSection.style.display = 'none';
  if (playerSection) playerSection.style.display = 'block';
}

// 5. Modern replacement for playSpotify
function playSpotify() {
  console.log('[SpotifyModern] Play/pause toggle requested');
  
  if (window.SpotifyWebPlayback && window.SpotifyWebPlayback.isReady()) {
    window.SpotifyWebPlayback.toggle();
  } else {
    console.warn('[SpotifyModern] Web Playback SDK not ready');
  }
}

// 6. Modern replacement for autoPlaySpotify
function autoPlaySpotify() {
  console.log('[SpotifyModern] Auto-play requested');
  
  // Check if autoplay toggle is enabled
  const autoplayButton = document.querySelector('.anvil-role-cap-autoplay-toggle-button .fa-toggle-on');
  
  if (autoplayButton && window.SpotifyWebPlayback && window.SpotifyWebPlayback.isReady()) {
    // Small delay to ensure track is loaded
    setTimeout(() => {
      window.SpotifyWebPlayback.toggle();
    }, 1000);
  }
}

// 7. Modern replacement for playNextSong
function playNextSong(formElement, trackOrArtist, spotifyTrackIDsList, spotifyArtistIDsList, spotifyArtistNameList) {
  console.log('[SpotifyModern] Playing next song...');
  
  const currentSpotifyID = sessionStorage.getItem("globalCurrentSpotifyID");
  
  if (!spotifyTrackIDsList || spotifyTrackIDsList.length === 0) {
    console.log('[SpotifyModern] No track list available');
    return;
  }
  
  const currentIndex = spotifyTrackIDsList.indexOf(currentSpotifyID);
  
  if (currentIndex >= 0 && currentIndex < spotifyTrackIDsList.length - 1) {
    const nextTrackID = spotifyTrackIDsList[currentIndex + 1];
    console.log('[SpotifyModern] Moving to next track:', nextTrackID);
    
    createOrUpdateSpotifyPlayer(
      formElement, 
      trackOrArtist, 
      nextTrackID, 
      spotifyTrackIDsList, 
      spotifyArtistIDsList, 
      spotifyArtistNameList
    );
  } else {
    console.log('[SpotifyModern] Reached end of playlist');
  }
}

// 8. Listen for authentication completion
window.addEventListener('storage', (e) => {
  if (e.key === 'spotify_access_token' && e.newValue) {
    console.log('[SpotifyModern] Authentication completed, initializing player...');
    
    // Initialize Web Playback SDK with new token
    if (window.SpotifyWebPlayback) {
      window.SpotifyWebPlayback.initialize(e.newValue);
    }
    
    // Update UI
    showSpotifyPlayerUI();
  }
});

// 9. Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  console.log('[SpotifyModern] Modern Spotify player module loaded');
  
  // Check for existing authentication
  const token = localStorage.getItem('spotify_access_token');
  if (token && window.SpotifyWebPlayback) {
    console.log('[SpotifyModern] Found existing token, initializing...');
    window.SpotifyWebPlayback.initialize(token);
  }
});

// 10. Legacy function compatibility
function setPlayButtonIcons(trackOrArtist, spotifyTrackIDsList = null, spotifyArtistIDsList = null) {
  console.log('[SpotifyModern] setPlayButtonIcons called - updating UI icons');
  
  // Update play/pause button icons based on current state
  const currentSpotifyID = sessionStorage.getItem("globalCurrentSpotifyID");
  
  // Set the icon of the small play buttons
  if (spotifyTrackIDsList && currentSpotifyID) {
    const currentIndex = spotifyTrackIDsList.indexOf(currentSpotifyID);
    
    // Update all play buttons to show correct state
    const playButtons = document.querySelectorAll('.anvil-role-cap-play-button, .play-button');
    
    playButtons.forEach((button, index) => {
      if (index === currentIndex) {
        // Current playing track - show pause icon
        button.innerHTML = '⏸️';
        button.classList.add('playing');
      } else {
        // Other tracks - show play icon
        button.innerHTML = '▶️';
        button.classList.remove('playing');
      }
    });
  }
  
  // Update fast forward/backward button states
  updateNavigationButtons(spotifyTrackIDsList, spotifyArtistIDsList);
}

function updateNavigationButtons(spotifyTrackIDsList, spotifyArtistIDsList) {
  const currentSpotifyID = sessionStorage.getItem("globalCurrentSpotifyID");
  
  if (!spotifyTrackIDsList || !currentSpotifyID) return;
  
  const currentIndex = spotifyTrackIDsList.indexOf(currentSpotifyID);
  
  // Update fast forward button
  const buttonFastForward = document.querySelector('.anvil-role-cap-fast-forward-button');
  if (buttonFastForward) {
    let hasNextArtist = false;
    if (currentIndex < spotifyTrackIDsList.length - 1 && spotifyArtistIDsList) {
      const currentArtistID = spotifyArtistIDsList[currentIndex];
      for (let i = currentIndex + 1; i < spotifyArtistIDsList.length; i++) {
        if (spotifyArtistIDsList[i] !== currentArtistID) {
          hasNextArtist = true;
          break;
        }
      }
    }
    
    if (hasNextArtist) {
      buttonFastForward.style.opacity = '1';
      buttonFastForward.style.pointerEvents = 'auto';
    } else {
      buttonFastForward.style.opacity = '0.3';
      buttonFastForward.style.pointerEvents = 'none';
    }
  }
  
  // Update rewind button
  const buttonRewind = document.querySelector('.anvil-role-cap-rewind-button');
  if (buttonRewind) {
    let hasPreviousArtist = false;
    if (currentIndex > 0 && spotifyArtistIDsList) {
      const currentArtistID = spotifyArtistIDsList[currentIndex];
      for (let i = currentIndex - 1; i >= 0; i--) {
        if (spotifyArtistIDsList[i] !== currentArtistID) {
          hasPreviousArtist = true;
          break;
        }
      }
    }
    
    if (hasPreviousArtist) {
      buttonRewind.style.opacity = '1';
      buttonRewind.style.pointerEvents = 'auto';
    } else {
      buttonRewind.style.opacity = '0.3';
      buttonRewind.style.pointerEvents = 'none';
    }
  }
}

// 11. Export functions for backward compatibility
window.createOrUpdateSpotifyPlayer = createOrUpdateSpotifyPlayer;
window.playSpotify = playSpotify;
window.autoPlaySpotify = autoPlaySpotify;
window.playNextSong = playNextSong;
window.setPlayButtonIcons = setPlayButtonIcons;

console.log('[SpotifyModern] Modern Spotify player integration loaded');
