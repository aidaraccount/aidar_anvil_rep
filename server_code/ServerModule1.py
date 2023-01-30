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

@anvil.server.callable
def create_bar_chart(label, data, min, max):
  import plotly.graph_objs as go
  fig = go.Figure(data=[go.Bar(
      #x=None,
      y=data,
      #name=label,
      marker=dict(
            color=data,
            colorscale=[[0, 'red'], [1, 'green']],
            cmin=min,
            cmax=max
        ),
        width=[0.6],
        showlegend=False
  )])
  fig.update_layout(
    yaxis=dict(range=[min, max]),
    xaxis=dict(showticklabels=False),
    paper_bgcolor= 'rgb(40, 40, 40)',
    plot_bgcolor='rgb(40, 40, 40)',
    font=dict(color='rgb(175, 175, 175)', size=12),
    title=dict(text=label,
               font=dict(size=12, color='rgb(175, 175, 175)', family='Arial Black'),
               x=0.5, y=0.95,
               xanchor='center', yanchor='top'),
    margin=dict(l=10, r=10, t=40, b=10)
  )
  return fig
  