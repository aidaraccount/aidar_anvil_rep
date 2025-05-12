"""
# --- 1. CLIENT CONFIGURATION MODULE ---
# Contains configuration values for client-side components.
# This module can be imported anywhere in the client-side Anvil application.
"""

import anvil.server

# --- 2. CONFIGURATION CACHE ---
# Cache for server-side configuration to avoid multiple calls
_config_cache = {}

# --- 3. PRICING CONFIGURATION ---
def get_price_values():
    """
    # --- 3.1 GET PRICING VALUES ---
    Fetches pricing configuration from the server.
    Uses cached values if available.

    Returns:
    --------
    dict
        Dictionary containing price values for all plans and frequencies
    """
    if 'price_values' not in _config_cache:
        try:
            # Fetch pricing config from server
            server_config = anvil.server.call('get_pricing_config')
            if server_config and 'price_values' in server_config:
                _config_cache['price_values'] = server_config['price_values']
            else:
                print("[CONFIG_ERROR] Invalid pricing configuration returned from server")
                # Return empty dict as fallback
                return {}
        except Exception as e:
            print(f"[CONFIG_ERROR] Error fetching pricing configuration: {e}")
            # Return empty dict as fallback
            return {}
    
    return _config_cache['price_values']

# --- 4. CONVENIENCE FUNCTIONS ---
def calculate_price(plan, frequency, user_count=1):
    """
    # --- 4.1 CALCULATE PRICE ---
    Calculate the price for a given plan, frequency, and user count.

    Parameters:
    -----------
    plan : str
        The plan type ('explore' or 'professional')
    frequency : str
        The billing frequency ('monthly' or 'yearly')
    user_count : int, optional
        Number of users (only relevant for professional plan)

    Returns:
    --------
    tuple
        (price_string, raw_price)
    """
    plan = plan.lower() if plan else ""
    frequency = frequency.lower() if frequency else ""
    price_values = get_price_values()

    if not price_values or plan not in price_values:
        return ("", 0)

    if frequency == 'monthly':
        monthly_price = price_values[plan]['monthly']
        if plan == 'professional':
            amount = monthly_price * user_count
            return (f'€{amount:.2f}/mo', amount)
        else:
            return (f'€{monthly_price:.2f}/mo', monthly_price)
    elif frequency == 'yearly':
        yearly_per_month = price_values[plan]['yearly_per_month']
        if plan == 'professional':
            monthly_amount = yearly_per_month * user_count
            yearly_amount = yearly_per_month * 12 * user_count
            return (f'€{yearly_amount:.2f}/yr ({monthly_amount:.2f}/mo/user)', yearly_amount)
        else:
            yearly_amount = yearly_per_month * 12
            return (f'€{yearly_amount:.2f}/yr ({yearly_per_month:.2f}/mo)', yearly_amount)

    return ("", 0)
