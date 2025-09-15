"""
Spotify Authorization Code Flow - Backend Implementation
Minimal server-side endpoint for secure token exchange
"""

import anvil.server
import requests
import base64
import os
from urllib.parse import urlencode

# Spotify app credentials (should be in environment variables in production)
SPOTIFY_CLIENT_ID = 'e289b3517636414e8d96249bc8ef6477'
SPOTIFY_CLIENT_SECRET = 'c9fac5cb2831432c9911cd4a4ce16e4a'
SPOTIFY_REDIRECT_URI = 'https://vbnuuyxq55wvdcoz.anvil.app/_/theme/spotify-callback.html'

@anvil.server.callable
def get_spotify_auth_url():
    """
    1. Generate Spotify authorization URL
    Returns the URL for user to authenticate with Spotify
    """
    import secrets
    
    # Generate random state for security
    state = secrets.token_urlsafe(16)
    
    params = {
        'response_type': 'code',
        'client_id': SPOTIFY_CLIENT_ID,
        'scope': 'streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'state': state,
        'show_dialog': 'true'
    }
    
    auth_url = 'https://accounts.spotify.com/authorize?' + urlencode(params)
    return {'auth_url': auth_url, 'state': state}

@anvil.server.callable
def exchange_code_for_token(authorization_code, state):
    """
    2. Exchange authorization code for access token
    This is called by the callback page after user authentication
    """
    try:
        # Prepare token exchange request
        token_url = 'https://accounts.spotify.com/api/token'
        
        # Create authorization header (Base64 encoded client_id:client_secret)
        credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': SPOTIFY_REDIRECT_URI
        }
        
        # Make token exchange request
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            return {
                'success': True,
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in', 3600)
            }
        else:
            return {
                'success': False,
                'error': f'Token exchange failed: {response.status_code}',
                'details': response.text
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Token exchange error: {str(e)}'
        }

@anvil.server.callable
def refresh_spotify_token(refresh_token):
    """
    3. Refresh expired access token using refresh token
    """
    try:
        token_url = 'https://accounts.spotify.com/api/token'
        
        credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            return {
                'success': True,
                'access_token': token_data.get('access_token'),
                'expires_in': token_data.get('expires_in', 3600)
            }
        else:
            return {
                'success': False,
                'error': f'Token refresh failed: {response.status_code}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Token refresh error: {str(e)}'
        }
