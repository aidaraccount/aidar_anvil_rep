import anvil.secrets
import anvil.stripe
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import json

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

# -----------------------------------------
# 1. SERVER MODULE FOR THE HOME PAGE
# -----------------------------------------

# 1.1 STATS FUNCTIONS
@anvil.server.callable
def get_home_agents(user_id):
    """
    Get agents data for the home page.
    
    Args:
        user_id: User ID
    """
    data = anvil.server.call('get_home_agents', user_id)
    return data

# 1.2 STATS FUNCTIONS
@anvil.server.callable
def get_home_stats(user_id):
    """
    Get stats data for the home page.
    
    Args:
        user_id: User ID
        
    Returns:
        Dict containing stats and news data
    """
    data = anvil.server.call('app_home', user_id)
    return data

# 1.3 SHORTS FUNCTIONS
@anvil.server.callable
def get_home_shorts(user_id, selected_wl_ids=None):
    """
    Get watchlists and shorts data for the home page.
    
    Args:
        user_id: User ID
        selected_wl_ids: Optional list of specifically selected watchlist IDs
        
    Returns:
        Dict containing watchlists and shorts data
    """
    # Get watchlists
    watchlists = json.loads(anvil.server.call("get_watchlist_ids", user_id))
    
    # Get shorts if watchlists exist
    shorts = None
    
    if selected_wl_ids is not None:
        if len(selected_wl_ids) > 0:
            # Use the selected watchlist IDs provided by the client
            print(f"Using specifically selected watchlist IDs: {selected_wl_ids}")
            shorts = anvil.server.call('get_shorts', selected_wl_ids, 0, 12)
        else:
            # Empty selected_wl_ids list provided - user has deselected all watchlists
            print(f"All watchlists deselected - returning no shorts")
            shorts = None
    elif watchlists is not None and len(watchlists) > 0:
        # No specific selection, use all available watchlists
        wl_ids = [wl["watchlist_id"] for wl in watchlists]
        shorts = anvil.server.call('get_shorts', wl_ids, 0, 12)
    
    return {
        "watchlists": watchlists,
        "shorts": shorts
    }

@anvil.server.callable
def get_additional_shorts(user_id, wl_ids, offset, limit):
    """
    Get additional shorts data for the home page.
    
    Args:
        user_id: User ID
        wl_ids: List of watchlist IDs
        offset: Offset for pagination
        limit: Limit for pagination
        
    Returns:
        Shorts data
    """
    shorts = anvil.server.call('get_shorts', wl_ids, offset, limit)
    return shorts
