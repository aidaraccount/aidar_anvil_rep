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

# 1.1 SHORTS FUNCTIONS
@anvil.server.callable
def get_home_shorts(wl_ids, offset, limit):
    """
    Get shorts data for the home page.
    
    Args:
        wl_ids: List of watchlist IDs
        offset: Offset for pagination
        limit: Limit for pagination
        
    Returns:
        Shorts data
    """
    shorts = anvil.server.call('get_shorts', wl_ids, offset, limit)
    return shorts

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
