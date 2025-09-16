# Spotify "App Not Found" Error - Troubleshooting Guide

## Problem
Getting "We could not find an app that matched your request" when trying to authenticate with Spotify.

## Root Cause Analysis
This error occurs when Spotify cannot match the authentication request to your registered app. The most common causes are:

1. **Redirect URI Mismatch** (90% of cases)
2. **Client ID Issues** (8% of cases)  
3. **Spotify App Configuration** (2% of cases)

## Diagnostic Steps

### Step 1: Check Current URLs
Open the debug tool: `/_/theme/spotify-debug.html`

This will show you:
- Current origin URL
- Generated redirect URI
- Whether you're in Anvil debug mode
- Configuration status

### Step 2: Verify Spotify App Configuration

Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and check:

**Required Redirect URIs to Add:**
```
https://vbnuuyxq55wvdcoz.anvil.app/_/theme/spotify-callback.html
http://localhost:3030/_/theme/spotify-callback.html
https://your-production-domain.com/_/theme/spotify-callback.html
```

**Current Client ID:** `e289b3517636414e8d96249bc8ef6477`

### Step 3: Anvil Debug Mode Issues

Anvil debug URLs change frequently and may not match your Spotify app configuration.

**Current Debug URL Pattern:**
- Changes with each session
- Format: `https://[random-id].anvil.app/debug/[session-id]`
- Redirect becomes: `https://[random-id].anvil.app/debug/[session-id]/_/theme/spotify-callback.html`

**Solutions:**
1. Add the stable Anvil URL: `https://vbnuuyxq55wvdcoz.anvil.app/_/theme/spotify-callback.html`
2. Test with production deployment
3. Use localhost for development

### Step 4: Enhanced Logging

The authentication flow now includes detailed logging. Check browser console for:
```
[SpotifyWebPlayback] Debug Info:
  - Current URL: [your current URL]
  - Origin: [your origin]
  - Client ID: [your client ID]
  - Is Anvil Debug: [true/false]
[SpotifyWebPlayback] Auth Parameters:
  - Redirect URI (raw): [the redirect URI being used]
  - Redirect URI (encoded): [URL encoded version]
[SpotifyWebPlayback] Complete Auth URL: [full Spotify auth URL]
```

## Quick Fixes

### Fix 1: Update Spotify App Redirect URIs
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Select your AIDAR app
3. Click "Edit Settings"
4. In "Redirect URIs", add ALL of these:
   ```
   https://vbnuuyxq55wvdcoz.anvil.app/_/theme/spotify-callback.html
   http://localhost:3030/_/theme/spotify-callback.html
   https://your-actual-domain.com/_/theme/spotify-callback.html
   ```
5. Save and wait 5-10 minutes for propagation

### Fix 2: Test with Stable URL
Instead of using the changing debug URL, test with:
```javascript
// Force stable Anvil URL for testing
const redirectUri = 'https://vbnuuyxq55wvdcoz.anvil.app/_/theme/spotify-callback.html';
```

### Fix 3: Use Implicit Grant for Testing
For quick testing, you can temporarily use the Implicit Grant flow:
```javascript
// Change response_type from 'code' to 'token'
response_type=token
// This bypasses the redirect URI issues for testing
```

## Testing Procedure

1. **Open Debug Tool**: Navigate to `/_/theme/spotify-debug.html`
2. **Check Configuration**: Verify all values are correct
3. **Test Current Config**: Click "Test Current Config" button
4. **Check Console**: Look for detailed auth URL in browser console
5. **Try Alternative**: Use "Test with Debug URL" or "Test with Production URL"

## Expected Console Output (Success)
```
[SpotifyWebPlayback] Starting Authorization Code Flow...
[SpotifyWebPlayback] Debug Info:
  - Current URL: https://vbnuuyxq55wvdcoz.anvil.app/...
  - Origin: https://vbnuuyxq55wvdcoz.anvil.app
  - Client ID: e289b3517636414e8d96249bc8ef6477
  - Is Anvil Debug: false
[SpotifyWebPlayback] Auth Parameters:
  - Redirect URI (raw): https://vbnuuyxq55wvdcoz.anvil.app/_/theme/spotify-callback.html
[SpotifyWebPlayback] Complete Auth URL: https://accounts.spotify.com/authorize?client_id=...
[SpotifyWebPlayback] Opening authentication popup...
```

## Common Mistakes

1. **Case Sensitivity**: Redirect URIs are case-sensitive
2. **Trailing Slashes**: Don't add trailing slashes to redirect URIs
3. **HTTP vs HTTPS**: Must match exactly
4. **URL Encoding**: Spotify expects properly encoded URLs

## If Still Not Working

1. **Double-check Client ID**: Ensure `e289b3517636414e8d96249bc8ef6477` is correct
2. **Wait for Propagation**: Spotify changes can take 10-15 minutes
3. **Try Incognito**: Clear browser cache/cookies
4. **Check Spotify App Status**: Ensure app is not in "Development Mode" restrictions

## Alternative: Deploy to Production

If debug mode continues to cause issues:
1. Deploy your Anvil app to production
2. Use the stable production URL
3. Add production redirect URI to Spotify app
4. Test with production deployment

This eliminates the variable debug URLs that cause most redirect URI mismatches.
