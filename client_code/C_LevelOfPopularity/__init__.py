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
    images = [artist['artist_picture_url'] for artist in data]
    
    # Create the bar chart
    fig = go.Figure(data=[go.Scatter(
        x=popularity,
        y=[0]*len(popularity),
        mode='markers', # Display as dots
        marker=dict(size=20, color='rgba(237,139,82,1)'),
        hoverinfo='skip',  # Disable hover effect since we display the text
    )])

    # Add the images using layout.images
    fig.update_layout(
      images=[dict(
        source=images[i],
        x=popularity[i],  # Place the image at the corresponding popularity value
        y=0.02,  # Slightly above the x-axis
        xref="x", yref="y",
        sizex=3, sizey=3,  # Image size (adjust as needed)
        xanchor="center", yanchor="bottom",  # Anchor the image to the center of the x position
        layer="above"  # Ensure the image is placed above the plot elements
      ) for i in range(len(images))]
    )   
    # Add artist names using layout.annotations
    annotations = [
      dict(
        x=popularity[i], 
        # y=0.15,  # Place the names higher than the images
        y = 0.1,  # Place the names higher than the images
        xref="x", 
        yref="y",
        text=names[i],  # Display the artist name
        showarrow=False,
        textangle = -5,
        font=dict(color="white", size=10),
        align="center"
      ) for i in range(len(names))
    ] 
    # Define a solid line along the x-axis using layout shapes
    fig.update_layout(
      shapes=[
          dict(
              type='line',
              x0=min(popularity), y0=0,  # Start of the line at y=1
              x1=max(popularity), y1=0,  # End of the line at y=1
              line=dict(color='white', width=2)  # Solid white line
          )
      ],
      annotations=annotations,
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
            showgrid=False,  # Disable y-axis grid lines
            range=[0, [0.5]*len(popularity)],  # Adjust y-axis range to add extra space

        ),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        font=dict(color="white"),
        template='plotly_dark',
        hoverlabel=dict(bgcolor="rgba(237,139,82, 0.8)")  # Customize hover background
    )
    
    # Assign the figure to the Plot component
    self.artist_popularity_plot.figure = fig