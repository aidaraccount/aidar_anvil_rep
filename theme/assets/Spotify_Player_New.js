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
  
  // Load the modern UI
  fetch('/theme/assets/Spotify_UI.html')
    .then(response => response.text())
    .then(html => {
      container.innerHTML = html;
      
      // Show auth section
      const authSection = document.getElementById('spotify-auth-section');
      const playerSection = document.getElementById('spotify-player-section');
      
      if (authSection) authSection.style.display = 'block';
      if (playerSection) playerSection.style.display = 'none';
    })
    .catch(error => {
      console.error('[SpotifyModern] Failed to load UI:', error);
      // Fallback to simple button
      container.innerHTML = `
        <div style="text-align: center; padding: 20px; background: #1db954; border-radius: 8px;">
          <h3 style="color: white; margin: 0 0 10px 0;">Connect Spotify Premium</h3>
          <button onclick="window.SpotifyWebPlayback.authenticate()" 
                  style="background: white; color: #1db954; border: none; padding: 12px 24px; border-radius: 25px; font-weight: bold; cursor: pointer;">
            Connect Spotify
          </button>
        </div>
      `;
    });
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

// 10. Export functions for backward compatibility
window.createOrUpdateSpotifyPlayer = createOrUpdateSpotifyPlayer;
window.playSpotify = playSpotify;
window.autoPlaySpotify = autoPlaySpotify;
window.playNextSong = playNextSong;

console.log('[SpotifyModern] Modern Spotify player integration loaded');
