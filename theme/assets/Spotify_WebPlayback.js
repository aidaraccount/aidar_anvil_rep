/**
 * Spotify Web Playback SDK Implementation
 * Replaces the problematic iframe-based player with proper SDK integration
 * Requires Spotify Premium and user authentication
 */

// Global variables for Spotify Web Playback SDK
let spotifyPlayer = null;
let deviceId = null;
let spotifyToken = null;
let isSpotifyReady = false;
let currentTrackUri = null;

// 1. Initialize Spotify Web Playback SDK
function initializeSpotifyWebPlayback(accessToken) {
  console.log('[SpotifyWebPlayback] Initializing Web Playback SDK...');
  
  if (!accessToken) {
    console.error('[SpotifyWebPlayback] No access token provided');
    return;
  }
  
  spotifyToken = accessToken;
  
  // Load Spotify Web Playback SDK
  if (!window.Spotify) {
    const script = document.createElement('script');
    script.src = 'https://sdk.scdn.co/spotify-player.js';
    script.async = true;
    document.head.appendChild(script);
    
    window.onSpotifyWebPlaybackSDKReady = () => {
      createSpotifyPlayer();
    };
  } else {
    createSpotifyPlayer();
  }
}

// 2. Create Spotify Player instance
function createSpotifyPlayer() {
  console.log('[SpotifyWebPlayback] Creating Spotify Player...');
  
  spotifyPlayer = new Spotify.Player({
    name: 'AIDAR Music Player',
    getOAuthToken: cb => { cb(spotifyToken); },
    volume: 0.8
  });

  // 3. Add event listeners
  setupSpotifyEventListeners();
  
  // 4. Connect to Spotify
  spotifyPlayer.connect().then(success => {
    if (success) {
      console.log('[SpotifyWebPlayback] Successfully connected to Spotify!');
      isSpotifyReady = true;
    } else {
      console.error('[SpotifyWebPlayback] Failed to connect to Spotify');
    }
  });
}

// 3. Setup event listeners for Spotify Player
function setupSpotifyEventListeners() {
  // Ready event - get device ID
  spotifyPlayer.addListener('ready', ({ device_id }) => {
    console.log('[SpotifyWebPlayback] Ready with Device ID:', device_id);
    deviceId = device_id;
    isSpotifyReady = true;
  });

  // Not Ready event
  spotifyPlayer.addListener('not_ready', ({ device_id }) => {
    console.log('[SpotifyWebPlayback] Device ID has gone offline:', device_id);
    isSpotifyReady = false;
  });

  // Initialization Error
  spotifyPlayer.addListener('initialization_error', ({ message }) => {
    console.error('[SpotifyWebPlayback] Initialization Error:', message);
  });

  // Authentication Error
  spotifyPlayer.addListener('authentication_error', ({ message }) => {
    console.error('[SpotifyWebPlayback] Authentication Error:', message);
    // Trigger re-authentication
    requestSpotifyAuthentication();
  });

  // Account Error (Premium required)
  spotifyPlayer.addListener('account_error', ({ message }) => {
    console.error('[SpotifyWebPlayback] Account Error:', message);
    showPremiumRequiredMessage();
  });

  // Playback Error
  spotifyPlayer.addListener('playback_error', ({ message }) => {
    console.error('[SpotifyWebPlayback] Playback Error:', message);
  });

  // Player State Changed
  spotifyPlayer.addListener('player_state_changed', (state) => {
    if (!state) return;
    
    console.log('[SpotifyWebPlayback] Player state changed:', state);
    
    const { 
      current_track, 
      next_tracks, 
      previous_tracks, 
      paused, 
      position, 
      duration 
    } = state;
    
    // Update UI based on playback state
    updatePlaybackUI(state);
    
    // Handle track end
    if (position === 0 && paused && current_track) {
      console.log('[SpotifyWebPlayback] Track ended, moving to next...');
      handleTrackEnd();
    }
  });
}

// 4. Play track using Web Playback SDK
async function playSpotifyTrack(trackOrArtist, spotifyId, spotifyTrackIdsList, spotifyArtistIdsList, spotifyArtistNameList) {
  console.log(`[SpotifyWebPlayback] Playing ${trackOrArtist}: ${spotifyId}`);
  
  if (!isSpotifyReady || !deviceId) {
    console.error('[SpotifyWebPlayback] Player not ready or no device ID');
    return;
  }
  
  const uri = `spotify:${trackOrArtist}:${spotifyId}`;
  currentTrackUri = uri;
  
  // Store track info for navigation
  sessionStorage.setItem("globalCurrentSpotifyID", spotifyId);
  sessionStorage.setItem("spotifyTrackIdsList", JSON.stringify(spotifyTrackIdsList || []));
  sessionStorage.setItem("spotifyArtistIdsList", JSON.stringify(spotifyArtistIdsList || []));
  sessionStorage.setItem("spotifyArtistNameList", JSON.stringify(spotifyArtistNameList || []));
  
  try {
    // Use Spotify Web API to start playback on our device
    const response = await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`, {
      method: 'PUT',
      body: JSON.stringify({
        uris: [uri]
      }),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${spotifyToken}`
      }
    });
    
    if (response.ok) {
      console.log('[SpotifyWebPlayback] Playback started successfully');
    } else {
      const error = await response.json();
      console.error('[SpotifyWebPlayback] Playback failed:', error);
      
      // Handle specific errors
      if (response.status === 403) {
        showPremiumRequiredMessage();
      } else if (response.status === 401) {
        requestSpotifyAuthentication();
      }
    }
  } catch (error) {
    console.error('[SpotifyWebPlayback] Network error:', error);
  }
}

// 5. Playback controls
async function toggleSpotifyPlayback() {
  if (!spotifyPlayer) return;
  
  const state = await spotifyPlayer.getCurrentState();
  
  if (!state) {
    console.log('[SpotifyWebPlayback] No active playback');
    return;
  }
  
  if (state.paused) {
    spotifyPlayer.resume().then(() => {
      console.log('[SpotifyWebPlayback] Resumed playback');
    });
  } else {
    spotifyPlayer.pause().then(() => {
      console.log('[SpotifyWebPlayback] Paused playback');
    });
  }
}

async function nextSpotifyTrack() {
  if (!spotifyPlayer) return;
  
  spotifyPlayer.nextTrack().then(() => {
    console.log('[SpotifyWebPlayback] Skipped to next track');
  });
}

async function previousSpotifyTrack() {
  if (!spotifyPlayer) return;
  
  spotifyPlayer.previousTrack().then(() => {
    console.log('[SpotifyWebPlayback] Skipped to previous track');
  });
}

// 6. Authentication flow
function requestSpotifyAuthentication() {
  console.log('[SpotifyWebPlayback] Requesting Spotify authentication...');
  
  const clientId = 'YOUR_SPOTIFY_CLIENT_ID'; // Replace with your actual client ID
  const redirectUri = encodeURIComponent(window.location.origin + '/spotify-callback');
  const scopes = encodeURIComponent('streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state');
  
  const authUrl = `https://accounts.spotify.com/authorize?` +
    `client_id=${clientId}&` +
    `response_type=token&` +
    `redirect_uri=${redirectUri}&` +
    `scope=${scopes}&` +
    `show_dialog=true`;
  
  // Open authentication in popup
  const popup = window.open(authUrl, 'spotify-auth', 'width=500,height=600');
  
  // Listen for authentication completion
  const checkClosed = setInterval(() => {
    if (popup.closed) {
      clearInterval(checkClosed);
      // Check if we got the token from localStorage (set by callback page)
      const token = localStorage.getItem('spotify_access_token');
      if (token) {
        initializeSpotifyWebPlayback(token);
      }
    }
  }, 1000);
}

// 7. Handle authentication callback
function handleSpotifyCallback() {
  const hash = window.location.hash.substring(1);
  const params = new URLSearchParams(hash);
  const accessToken = params.get('access_token');
  
  if (accessToken) {
    console.log('[SpotifyWebPlayback] Authentication successful');
    localStorage.setItem('spotify_access_token', accessToken);
    
    // Close popup and notify parent
    if (window.opener) {
      window.close();
    } else {
      // Redirect back to main app
      window.location.href = '/';
    }
  }
}

// 8. UI Updates
function updatePlaybackUI(state) {
  const { current_track, paused, position, duration } = state;
  
  if (!current_track) return;
  
  // Update track info display
  const trackNameElement = document.querySelector('.spotify-track-name');
  const artistNameElement = document.querySelector('.spotify-artist-name');
  const progressElement = document.querySelector('.spotify-progress');
  
  if (trackNameElement) {
    trackNameElement.textContent = current_track.name;
  }
  
  if (artistNameElement) {
    artistNameElement.textContent = current_track.artists.map(a => a.name).join(', ');
  }
  
  if (progressElement) {
    const progressPercent = (position / duration) * 100;
    progressElement.style.width = `${progressPercent}%`;
  }
  
  // Update play/pause button
  updatePlayPauseButton(!paused);
}

function updatePlayPauseButton(isPlaying) {
  const playButton = document.querySelector('.spotify-play-button');
  if (playButton) {
    playButton.innerHTML = isPlaying ? '⏸️' : '▶️';
  }
}

function showPremiumRequiredMessage() {
  console.warn('[SpotifyWebPlayback] Spotify Premium required for playback');
  
  // Show user-friendly message
  const messageElement = document.querySelector('.spotify-message');
  if (messageElement) {
    messageElement.innerHTML = `
      <div class="premium-required">
        <h3>Spotify Premium Required</h3>
        <p>To play music directly in AIDAR, you need a Spotify Premium account.</p>
        <button onclick="window.open('https://www.spotify.com/premium/', '_blank')">
          Upgrade to Premium
        </button>
      </div>
    `;
  }
}

// 9. Track navigation
function handleTrackEnd() {
  const trackIdsList = JSON.parse(sessionStorage.getItem("spotifyTrackIdsList") || "[]");
  const currentId = sessionStorage.getItem("globalCurrentSpotifyID");
  
  if (trackIdsList.length > 0) {
    const currentIndex = trackIdsList.indexOf(currentId);
    if (currentIndex >= 0 && currentIndex < trackIdsList.length - 1) {
      const nextTrackId = trackIdsList[currentIndex + 1];
      console.log('[SpotifyWebPlayback] Auto-playing next track:', nextTrackId);
      
      // Play next track
      const artistIdsList = JSON.parse(sessionStorage.getItem("spotifyArtistIdsList") || "[]");
      const artistNameList = JSON.parse(sessionStorage.getItem("spotifyArtistNameList") || "[]");
      
      playSpotifyTrack('track', nextTrackId, trackIdsList, artistIdsList, artistNameList);
    }
  }
}

// 10. Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  // Check if we're on the callback page
  if (window.location.hash.includes('access_token')) {
    handleSpotifyCallback();
    return;
  }
  
  // Check for existing token
  const existingToken = localStorage.getItem('spotify_access_token');
  if (existingToken) {
    console.log('[SpotifyWebPlayback] Found existing token, initializing...');
    initializeSpotifyWebPlayback(existingToken);
  }
});

// 11. Public API for integration with existing code
window.SpotifyWebPlayback = {
  initialize: initializeSpotifyWebPlayback,
  play: playSpotifyTrack,
  toggle: toggleSpotifyPlayback,
  next: nextSpotifyTrack,
  previous: previousSpotifyTrack,
  authenticate: requestSpotifyAuthentication,
  isReady: () => isSpotifyReady
};

console.log('[SpotifyWebPlayback] Spotify Web Playback SDK module loaded');
