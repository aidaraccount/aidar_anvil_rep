from ._anvil_designer import C_LevelOfPopularityTemplate
from ..C_RefPopupTable import C_RefPopupTable
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

import plotly.graph_objects as go

from ..nav import click_link, click_button, logout, save_var, load_var


class C_LevelOfPopularity(C_LevelOfPopularityTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.    
    self.model_id_view = load_var("model_id_view")

    data = json.loads(anvil.server.call('get_pop_bar_artists', self.model_id_view))
    print(data)
     # Extract names and popularity
    names = [artist['name'] for artist in data]
    popularity = [artist['artist_popularity_lat'] for artist in data]
    
    # Create the bar chart
    fig = go.Figure(data=[go.Scatter(
        x=popularity,
        y=[0]*len(popularity),
        mode='markers', # Display as dots
        marker=dict(size=10, color='rgba(237,139,82,1)'),
        showlegend=False # Don't show legend
    )])
    
    # Add annotations (artist names in bubbles)
    annotations = []
    for i, artist_name in enumerate(names):
        annotations.append(
            dict(
                x=popularity[i],  # x coordinate
                y=0.5,  # y coordinate slightly above the point
                text=artist_name,  # Artist's name
                showarrow=True,  # Show arrow pointing to the point
                arrowhead=2,  # Arrowhead style
                ax=0,  # x-axis offset for the arrow
                ay=-20,  # y-axis offset for the arrow
                bgcolor="rgba(237,139,82,0.8)",  # Bubble background color
                font=dict(color="white"),  # Text color inside the bubble
                arrowcolor="rgba(237,139,82,1)"  # Arrow color
            )
        )
      
    # Customize the layout of the chart
    fig.update_layout(
        xaxis=dict(
          title='Popularity',
          showgrid=False, 
          zeroline=True,
          zerolinewidth=2
        ),
        yaxis=dict(
            visible=False,  # Hide the y-axis since it's not meaningful
            showgrid=False  # Disable y-axis grid lines
        ),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        font=dict(color="white"),
        template='plotly_dark',
        hoverlabel=dict(bgcolor="rgba(237,139,82, 0.8)")  # Customize hover background
    )
    
    # Assign the figure to the Plot component
    self.artist_popularity_plot.figure = fig