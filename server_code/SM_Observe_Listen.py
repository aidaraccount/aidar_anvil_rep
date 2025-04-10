import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# -----------------------------------------
# 1. SERVER MODULE FOR OBSERVE_LISTEN PAGE
# -----------------------------------------

# 1.1 ARTISTS TRACK LOADING FUNCTION
@anvil.server.callable
def get_observe_tracks_data(notification_id):
    """
    Get observed tracks data for the panel.
    
    Args:
        notification_id: Notification ID
        
    Returns:
        Observed tracks data
    """
    # Call the original function to get the data
    tracks = anvil.server.call('get_observed_tracks', notification_id)
    return tracks

# 1.2 ARTIST DISCOVER LOADING FUNCTION
@anvil.server.callable
def get_artist_discover_data(artist_id):
    """
    Get artist discover data for C_Discover component.
    
    Args:
        artist_id: Artist ID
        
    Returns:
        Artist data for discover panel
    """
    # No actual processing needed here - just pass through the artist_id
    # The client will use this ID to initialize the C_Discover component
    return artist_id
