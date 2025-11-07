# TEST COMMENT
import stripe.checkout
import anvil.server
import anvil.users
from anvil import open_form
from anvil_extras import routing
from datetime import datetime

from .MainOut import MainOut
from .MainOut_Register import MainOut_Register
from .MainIn import MainIn
from .Home import Home


user = anvil.users.get_user()
if user:
  routing.launch()
else:
  routing.launch()
  open_form('MainOut')