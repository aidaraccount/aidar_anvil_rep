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
        hoverinfo='skip',  # Disable hover effect since we display the text
        # text=names,  # Display artist names
        # textfont=dict(color='white', size=12),  # Ensure text is visible
        # texttemplate="%{text}",  # Show text at all times
        # textposition='top center',  # Position text above the points
        # showlegend=False, # Don't show legend
    )])
    # Add a line using another scatter trace
    fig.add_trace(go.Scatter(
        x=[min(popularity), max(popularity)],
        y=[0, 0],  # A line on the y=0 axis
        mode='lines',
        line=dict(color='white', width=2)
    ))    
    # # Add annotations for each artist name as bubbles
    # for i, name in enumerate(names):
    #     fig.add_annotation(
    #         x=popularity[i],  # Align with the popularity point
    #         y=0.1,  # Position slightly above the dot
    #         text=name,  # Artist's name as text
    #         showarrow=True,  # Display an arrow
    #         arrowhead=2,  # Arrow type
    #         arrowsize=1,  # Arrow size
    #         arrowwidth=1,  # Arrow line width
    #         arrowcolor='white',  # Arrow color
    #         ax=popularity[i],  # Arrow start point (x)
    #         ay=0,  # Arrow start point (y) aligned with dot
    #         font=dict(
    #             color='white', 
    #             size=12, 
    #             family="Arial"
    #         ),
    #         bgcolor='rgba(255, 255, 255, 0.2)',  # Light semi-transparent background
    #         bordercolor='white',  # Border color to simulate bubble
    #         borderwidth=2,  # Bubble border width
    #         borderpad=4  # Padding around the text to make bubble bigger
    #     )
        
    # Define a solid line along the x-axis using layout shapes
    fig.update_layout(
        shapes=[
            dict(
                type='line',
                x0=min(popularity), y0=0,  # Start of the line at y=1
                x1=max(popularity), y1=0,  # End of the line at y=1
                line=dict(color='white', width=2)  # Solid white line
            )
        ]
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