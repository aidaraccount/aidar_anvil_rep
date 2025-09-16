/**
 * Spotify Web Playback SDK - Authorization Code Flow Implementation
 * Clean, minimal implementation following official Spotify documentation
 */

let spotifyPlayer = null;
let currentDeviceId = null;

// 1. Initialize Spotify Web Playback SDK
function initializeSpotifyWebPlayback(accessToken) {
  console.log('[SpotifyWebPlayback] Initializing with Authorization Code Flow...');
  
  if (!window.Spotify || !window.Spotify.Player) {
    console.error('[SpotifyWebPlayback] Spotify Web Playback SDK not loaded');
    return;
  }
  
  // Create player instance
  spotifyPlayer = new window.Spotify.Player({
    name: 'AIDAR Web Player',
    getOAuthToken: cb => { cb(accessToken); },
    volume: 0.8
  });
  
  // Add event listeners
  spotifyPlayer.addListener('ready', ({ device_id }) => {
    console.log('[SpotifyWebPlayback] Ready with Device ID:', device_id);
    currentDeviceId = device_id;
  });
  
  spotifyPlayer.addListener('not_ready', ({ device_id }) => {
    console.log('[SpotifyWebPlayback] Device has gone offline:', device_id);
  });
  
  spotifyPlayer.addListener('player_state_changed', (state) => {
    if (!state) return;
    
    console.log('[SpotifyWebPlayback] Player state changed:', state);
    updatePlayerUI(state);
  });
  
  // Connect to the player
  spotifyPlayer.connect().then(success => {
    if (success) {
      console.log('[SpotifyWebPlayback] Successfully connected to Spotify!');
    }
  });
}

// 2. Authentication using Authorization Code Flow
async function authenticateSpotify() {
  try {
    console.log('[SpotifyWebPlayback] Starting Authorization Code Flow...');
    
    // Enhanced logging for debugging
    const currentURL = window.location.href;
    const origin = window.location.origin;
    const clientId = window.SPOTIFY_CONFIG?.CLIENT_ID || 'e289b3517636414e8d96249bc8ef6477';
    
    console.log('[SpotifyWebPlayback] Debug Info:');
    console.log('  - Current URL:', currentURL);
    console.log('  - Origin:', origin);
    console.log('  - Client ID:', clientId);
    console.log('  - Is Anvil Debug:', origin.includes('anvil.app'));
    
    // Check if anvil.server is available
    if (typeof anvil === 'undefined' || typeof anvil.server === 'undefined') {
      console.log('[SpotifyWebPlayback] Anvil server not available, using fallback method');
      
      // Construct redirect URI with enhanced logging
      const redirectUri = origin + '/_/theme/spotify-callback.html';
      const encodedRedirectUri = encodeURIComponent(redirectUri);
      const scopes = encodeURIComponent('streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state');
      const state = Math.random().toString(36).substring(2, 15);
      
      console.log('[SpotifyWebPlayback] Auth Parameters:');
      console.log('  - Redirect URI (raw):', redirectUri);
      console.log('  - Redirect URI (encoded):', encodedRedirectUri);
      console.log('  - State:', state);
      console.log('  - Scopes:', 'streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state');
      
      sessionStorage.setItem('spotify_auth_state', state);
      
      const authUrl = `https://accounts.spotify.com/authorize?` +
        `client_id=${clientId}&` +
        `response_type=token&` +
        `redirect_uri=${encodedRedirectUri}&` +
        `scope=${scopes}&` +
        `state=${state}&` +
        `show_dialog=true`;
      
      console.log('[SpotifyWebPlayback] Complete Auth URL:', authUrl);
      console.log('[SpotifyWebPlayback] Opening authentication popup...');
      
      // Open authentication popup
      const popup = window.open(authUrl, 'spotify-auth', 'width=500,height=600,scrollbars=yes,resizable=yes');
      
      if (!popup) {
        console.error('[SpotifyWebPlayback] Failed to open popup - popup blocked?');
        alert('Popup blocked! Please allow popups for authentication.');
        return;
      }
      
      // Listen for authentication completion
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          console.log('[SpotifyWebPlayback] Popup closed, checking for token...');
          
          // Check if we got the token
          setTimeout(() => {
            const token = localStorage.getItem('spotify_access_token');
            if (token) {
              console.log('[SpotifyWebPlayback] Authentication successful - token found');
              initializeSpotifyWebPlayback(token);
              showPlayerUI();
            } else {
              console.log('[SpotifyWebPlayback] Authentication failed or cancelled - no token found');
            }
          }, 500);
        }
      }, 1000);
      
      return;
    }
    
    // Get authorization URL from backend
    const authData = await anvil.server.call('get_spotify_auth_url');
    
    // Store state for validation
    sessionStorage.setItem('spotify_auth_state', authData.state);
    
    // Open authentication popup
    const popup = window.open(
      authData.auth_url, 
      'spotify-auth', 
      'width=500,height=600,scrollbars=yes,resizable=yes'
    );
    
    // Listen for authentication completion
    const checkClosed = setInterval(() => {
      if (popup.closed) {
        clearInterval(checkClosed);
        
        // Check if we got the token
        setTimeout(() => {
          const token = localStorage.getItem('spotify_access_token');
          if (token) {
            console.log('[SpotifyWebPlayback] Authentication successful');
            initializeSpotifyWebPlayback(token);
            showPlayerUI();
          } else {
            console.log('[SpotifyWebPlayback] Authentication failed or cancelled');
          }
        }, 500);
      }
    }, 1000);
    
  } catch (error) {
    console.error('[SpotifyWebPlayback] Authentication error:', error);
  }
}

// 3. Play track
async function playTrack(trackId) {
  if (!spotifyPlayer || !currentDeviceId) {
    console.error('[SpotifyWebPlayback] Player not ready');
    return;
  }
  
  const token = localStorage.getItem('spotify_access_token');
  if (!token) {
    console.error('[SpotifyWebPlayback] No access token');
    return;
  }
  
  try {
    const response = await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${currentDeviceId}`, {
      method: 'PUT',
      body: JSON.stringify({ uris: [`spotify:track:${trackId}`] }),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      console.log('[SpotifyWebPlayback] Track started playing:', trackId);
    } else {
      console.error('[SpotifyWebPlayback] Failed to play track:', response.status);
    }
  } catch (error) {
    console.error('[SpotifyWebPlayback] Error playing track:', error);
  }
}

// 4. Playback controls
async function togglePlayback() {
  if (!spotifyPlayer) return;
  spotifyPlayer.togglePlay();
}

async function nextTrack() {
  if (!spotifyPlayer) return;
  spotifyPlayer.nextTrack();
}

async function previousTrack() {
  if (!spotifyPlayer) return;
  spotifyPlayer.previousTrack();
}

async function setVolume(volume) {
  if (!spotifyPlayer) return;
  spotifyPlayer.setVolume(volume);
}

// 5. UI Updates
function updatePlayerUI(state) {
  const trackName = state.track_window.current_track.name;
  const artistName = state.track_window.current_track.artists[0].name;
  const isPlaying = !state.paused;
  
  // Update track info
  const trackNameEl = document.querySelector('.spotify-track-name');
  const artistNameEl = document.querySelector('.spotify-artist-name');
  
  if (trackNameEl) trackNameEl.textContent = trackName;
  if (artistNameEl) artistNameEl.textContent = artistName;
  
  // Update play/pause button
  const playIcon = document.querySelector('.play-icon');
  const pauseIcon = document.querySelector('.pause-icon');
  
  if (playIcon && pauseIcon) {
    if (isPlaying) {
      playIcon.style.display = 'none';
      pauseIcon.style.display = 'block';
    } else {
      playIcon.style.display = 'block';
      pauseIcon.style.display = 'none';
    }
  }
  
  // Update progress bar
  const progress = (state.position / state.duration) * 100;
  const progressBar = document.querySelector('.spotify-progress');
  if (progressBar) {
    progressBar.style.width = `${progress}%`;
  }
  
  // Update time display
  const currentTimeEl = document.querySelector('.spotify-current-time');
  const totalTimeEl = document.querySelector('.spotify-total-time');
  
  if (currentTimeEl) currentTimeEl.textContent = formatTime(state.position);
  if (totalTimeEl) totalTimeEl.textContent = formatTime(state.duration);
}

function formatTime(ms) {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function showPlayerUI() {
  const authSection = document.getElementById('spotify-auth-section');
  const playerSection = document.getElementById('spotify-player-section');
  
  if (authSection) authSection.style.display = 'none';
  if (playerSection) playerSection.style.display = 'block';
}

// 6. Check if user is already authenticated
function checkExistingAuth() {
  const token = localStorage.getItem('spotify_access_token');
  const expires = localStorage.getItem('spotify_token_expires');
  
  if (token && expires && Date.now() < parseInt(expires)) {
    console.log('[SpotifyWebPlayback] Using existing valid token');
    initializeSpotifyWebPlayback(token);
    showPlayerUI();
    return true;
  }
  
  return false;
}

// 7. Export functions for global access
window.SpotifyWebPlayback = {
  authenticate: authenticateSpotify,
  playTrack: playTrack,
  toggle: togglePlayback,
  next: nextTrack,
  previous: previousTrack,
  setVolume: setVolume,
  checkAuth: checkExistingAuth,
  isReady: () => spotifyPlayer !== null
};

// 8. Required callback for Spotify SDK
window.onSpotifyWebPlaybackSDKReady = () => {
  console.log('[SpotifyWebPlayback] SDK Ready - callback triggered');
  // SDK is now available, check for existing auth
  setTimeout(() => {
    if (checkExistingAuth()) {
      console.log('[SpotifyWebPlayback] Auto-initialized with existing token');
    }
  }, 500);
};

console.log('[SpotifyWebPlayback] Authorization Code Flow module loaded');
