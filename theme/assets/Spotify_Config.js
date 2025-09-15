/**
 * Spotify Configuration for AIDAR
 * Centralized configuration - only AIDAR needs to set this up once
 * Users just login with their existing Spotify Premium accounts
 */

// PRODUCTION CONFIGURATION
const SPOTIFY_CONFIG = {
  // Replace with your actual AIDAR Spotify app client ID
  CLIENT_ID: 'e289b3517636414e8d96249bc8ef6477',
  
  // Scopes needed for playback
  SCOPES: [
    'streaming',
    'user-read-email', 
    'user-read-private',
    'user-read-playback-state',
    'user-modify-playback-state'
  ],
  
  // Redirect URIs (configure these in your Spotify app)
  REDIRECT_URIS: {
    production: window.location.origin + '/spotify-callback',
    development: 'http://localhost:3000/spotify-callback'
  }
};

// Export for use in other modules
window.SPOTIFY_CONFIG = SPOTIFY_CONFIG;

console.log('[SpotifyConfig] Configuration loaded for client:', SPOTIFY_CONFIG.CLIENT_ID);
