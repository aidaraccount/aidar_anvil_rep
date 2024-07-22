#import anvil.server
#from .MainForm import MainForm

#from anvil_extras import routing

#routing.launch()

import anvil.server
from anvil_extras import routing
import anvil.users

def launch_app():
    if anvil.users.get_user():
        from .Main_In import Main_In
        Main_In()
    else:
        from .Main_Out import Main_Out
        Main_Out()

routing.launch(launch_app)
