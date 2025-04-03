import anvil.server
import anvil.users
from anvil import open_form
from anvil_extras import routing
from datetime import datetime

from .MainOut import MainOut
from .MainOut_Register import MainOut_Register
from .MainIn import MainIn
from .Home import Home

# Add diagnostic print to track startup execution
print(f"STARTUP: Executing startup.py - {datetime.now()}", flush=True)

user = anvil.users.get_user()
if user:
  print(f"STARTUP: User logged in, launching routing - {datetime.now()}", flush=True)
  routing.launch()
else:
  print(f"STARTUP: No user, launching routing and opening MainOut - {datetime.now()}", flush=True)
  routing.launch()
  open_form('MainOut')
