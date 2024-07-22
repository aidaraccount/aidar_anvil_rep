import anvil.server
from .MainForm import MainForm

from anvil_extras import routing

routing.launch()

#import anvil.server
#from anvil_extras import routing
#import anvil.users

#def launch_app():
#  user = anvil.users.get_user()
#  if user:
#    open_form('Main_In')
#  else:
#    open_form('Main_Out')

#routing.launch(launch_app)
