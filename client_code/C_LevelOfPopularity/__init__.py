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
    followers = [artist['artist_follower_lat'] for artist in data]
    spotify_fol = [artist['artist_follower_lat'] for artist in data]
    insta_fol = [artist['artist_follower_lat'] for artist in data]

    # Create the hover text with image tag
    hover_texts = [
      # f"<b>{names[i]}</b><br><img src='{images[i]}' style='width:50px;height:50px;'>"
      f"""
      <b>{names[i]}</b><br>
      <br>
      <b>Followers: {followers[i]}</b><br>
      <b>Spotify Followers: {followers[i]}</b><br>
      <b>Instagram Followers: {followers[i]}</b>"""
      for i in range(len(names))
    ]
    # Create the bar chart
    fig = go.Figure(data=[go.Scatter(
        x=popularity,
        y=[0.3]*len(popularity),
        mode='markers', # Display as dots
        marker=dict(size=1, color='rgba(237,139,82,0)'),
        hoverinfo='text',  # Disable hover effect since we display the text
        text=hover_texts,  # Display artist names
    )])

    # Add the images using layout.images
    fig.update_layout(
      images=[dict(
        source=images[i],
        x=popularity[i],  # Place the image at the corresponding popularity value
        y=0.1,  # Slightly above the x-axis
        xref="x", yref="y",
        sizex=5, sizey=5,  # Image size (adjust as needed)
        xanchor="center", yanchor="bottom",  # Anchor the image to the center of the x position
        layer="above"  # Ensure the image is placed above the plot elements
      ) for i in range(len(images))]
    )   
    # Add artist names using layout.annotations
    annotations = [
      dict(
        x=popularity[i], 
        y = 0.6,  # Place the names higher than the images
        xref="x", 
        yref="y",
        text=names[i],  # Display the artist name
        showarrow=False,
        textangle = -13,
        font=dict(color="white", size=10),
        align="center"
      ) for i in range(len(names))
    ] 
    # Define a solid line along the x-axis using layout shapes
    fig.update_layout(
      shapes=[
          dict(
              type='line',
              x0=0, y0=0,  # Start of the line at y=0
              x1=100, y1=0,  # End of the line at y=0
              line=dict(color='white', width=1)  # Solid white line
          )
      ],
      # annotations=annotations,
      dragmode=False,
      xaxis=dict(
        title='Popularity',
        showgrid=False, 
        zeroline=True,
        zerolinewidth=2,
        range=[0, 100],  # Ensure the range matches the data
        tickvals=[],  # Hide tick values
        ticktext=[],  # Hide tick text
        showticklabels=False,
      ),
      yaxis=dict(
        visible=False,  # Hide the y-axis since it's not meaningful
        showgrid=False,  # Disable y-axis grid lines
        zeroline=False,
        zerolinewidth=0,
      ),
      plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
      paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
      font=dict(color="white"),
      template='plotly_dark',
      hoverlabel=dict(bgcolor="rgba(237,139,82, 0.8)"), # Customize hover background
      hovermode="x",  # Ensures hover appears near the data point
    )
    
    # Disable zooming, panning, and other interactions
    config = dict(
      displayModeBar=False,  # Hide the mode bar (zoom, pan, etc.)
      scrollZoom=False,      # Disable scroll to zoom
      dragmode=False,        # Disable dragging and panning
      showAxisDragHandles=False,
      showAxisRangeEntryBoxes=False,
      editSelection=False,
      responsive=True,
      autosizable=True,
    )
    # Assign the figure to the Plot component
    self.artist_popularity_plot.figure = fig
    self.artist_popularity_plot.config = config


  def slider_1_change(self, handle, **event_args):
    """This method is called when the slider has finished sliding"""
    # print(
    #     f"slider 1 change\nhandle={handle} | value={self.slider_1.values[handle]} | formatted={self.slider_1.formatted_values[handle]}"
    # )
    
    save_var('min_pop', self.slider_1.formatted_values[0])
    save_var('max_pop', self.slider_1.formatted_values[1])
    # print('Pop-Range:', self.slider_1.formatted_values[0], self.slider_1.formatted_values[1])
    