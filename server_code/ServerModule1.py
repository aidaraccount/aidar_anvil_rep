import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#

@anvil.server.callable
def check_user_presence():
    user = anvil.users.get_user()
    if (user["user_id"] == None):
      new_user_id = anvil.server.call('CheckUserPresence', user["email"])
      if (new_user_id != None):
        user_row = app_tables.users.get(email = user["email"])
        user_row['user_id'] = new_user_id


@anvil.server.callable
def create_star_plot(data):
    import plotly.graph_objs as go
    import numpy as np
    fig = go.Figure(data=[go.Scatterpolar(
      r = data,
      theta = ['AvgDuration', 'AvgDanceability', 'AvgEnergy', 'AvgKey', 'AvgLoudness'],
      fill = 'toself'
    )])
    fig.update_layout(
      polar = dict(
        radialaxis = dict(
          visible = True,
          range = [0, 1]
        )),
      showlegend = False
    )
    return fig

