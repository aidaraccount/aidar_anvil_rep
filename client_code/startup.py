import anvil.server
import anvil.users
from anvil import open_form
from anvil_extras import routing

from .Main_Out import Main_Out
from .Main_In import Main_In
from .Home import Home


user = anvil.users.get_user()
if user:
  routing.launch()
else:
  routing.launch()
  # open_form('Main_Out')
  open_form('Main_Out_New')
