from ._anvil_designer import C_GrowthImportanceTemplate
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


class C_GrowthImportance(C_GrowthImportanceTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.model_id_view = load_var("model_id_view")

    infos = json.loads(anvil.server.call("get_model_stats", self.model_id_view))[0]
    print(infos["min_pop"])
    if infos["min_pop"] is None:
      save_var("min_pop", 20)
      save_var("max_pop", 50)
    else:
      self.slider_1.values = infos["min_pop"], infos["max_pop"]
      self.set_slider_text_boxes()
      save_var("min_pop", infos["min_pop"])
      save_var("max_pop", infos["max_pop"])

    data = json.loads(anvil.server.call("get_pop_bar_artists", self.model_id_view))

    # Extract names and popularity
    names = [artist["name"] for artist in data]
    popularity = [artist["artist_popularity_lat"] for artist in data]
    images = [artist["artist_picture_url"] for artist in data]
    spotify_fol = self.shorten_number(
      [artist["artist_follower_lat"] for artist in data]
    )
    spotify_mon_lis = self.shorten_number(
      [artist["sp_mtl_listeners_lat"] for artist in data]
    )
    tiktok_fol = self.shorten_number([artist["tiktok_follower_lat"] for artist in data])
    soundcld_fol = self.shorten_number(
      [artist["soundcloud_follower_lat"] for artist in data]
    )

    # Create the hover text with image tag
    hover_texts = [
      # f"<b>{names[i]}</b><br><img src='{images[i]}' style='width:50px;height:50px;'>"
      f"""
      <b>{names[i]}</b><br>
      <br>
      <b>Spotify Popularity: {popularity[i]}</b><br>
      <b>Spotify Fol.: {spotify_fol[i]}</b><br>
      <b>Spotify mtl. List.: {spotify_mon_lis[i]}</b><br>
      <b>TikTok Fol.: {tiktok_fol[i]}</b><br>
      <b>SoundCloud Fol.: {soundcld_fol[i]}</b>"""
      for i in range(len(names))
    ]
    # Create the bar chart
    fig = go.Figure(
      data=[
        go.Scatter(
          x=popularity,
          y=[0.2] * len(popularity),
          mode="markers",  # Display as dots
          marker=dict(size=1, color="rgba(237,139,82,0)"),
          hoverinfo="text",  # Disable hover effect since we display the text
          text=hover_texts,  # Display artist names
        )
      ]
    )

    # Function to slightly offset positions on both x and y axes to avoid overlapping
    def adjust_position(x_pos, y_pos, x_min_distance=3, y_offset=0.06):
      adjusted_x_pos = x_pos[:]
      adjusted_y_pos = y_pos[:]
      for i in range(1, len(adjusted_x_pos)):
        # Offset x-axis if the points are too close
        if abs(adjusted_x_pos[i] - adjusted_x_pos[i - 1]) <= x_min_distance:
          adjusted_x_pos[i] += x_min_distance  # Slightly offset the x position
          # Always offset y-axis by a fixed amount to avoid overlapping on the y-axis
          adjusted_y_pos[i] += y_offset
      return adjusted_x_pos, adjusted_y_pos

    # Apply the adjustment to both x and y positions
    y_values = [0.03] * len(popularity)  # Default y position for images
    adjusted_popularity, adjusted_y_values = adjust_position(popularity, y_values)

    # Add the images using layout.images
    fig.update_layout(
      images=[
        dict(
          source=images[i],
          # x=popularity[i],  # Place the image at the corresponding popularity value
          x=adjusted_popularity[
            i
          ],  # Place the image at the corresponding popularity value
          y=adjusted_y_values[i],  # Slightly above the x-axis
          xref="x",
          yref="y",
          sizex=7,
          sizey=7,  # Image size (adjust as needed)
          xanchor="center",
          yanchor="bottom",  # Anchor the image to the center of the x position
          layer="above",  # Ensure the image is placed above the plot elements
        )
        for i in range(len(images))
      ]
    )
    # Add artist names using layout.annotations
    annotations = [
      dict(
        x=popularity[i],
        y=0.6,  # Place the names higher than the images
        xref="x",
        yref="y",
        text=names[i],  # Display the artist name
        showarrow=False,
        textangle=-13,
        font=dict(color="white", size=10),
        align="center",
      )
      for i in range(len(names))
    ]
    # Define a solid line along the x-axis using layout shapes
    fig.update_layout(
      shapes=[
        dict(
          type="line",
          x0=0,
          y0=0,  # Start of the line at y=0
          x1=100,
          y1=0,  # End of the line at y=0
          line=dict(color="white", width=1),  # Solid white line
        )
      ],
      # annotations=annotations,
      dragmode=False,
      xaxis=dict(
        # title='Popularity',
        showgrid=False,
        zeroline=True,
        zerolinewidth=2,
        range=[0, 100],  # Ensure the range matches the data
        tickvals=[],  # Hide tick values
        ticktext=[],  # Hide tick text
        showticklabels=False,
      ),
      yaxis=dict(
        showticklabels=False,
        showline=False,
        zeroline=False,
        visible=False,  # Hide the y-axis since it's not meaningful
        showgrid=False,  # Disable y-axis grid lines
      ),
      plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
      paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
      font=dict(color="white"),
      template="plotly_dark",
      hoverlabel=dict(bgcolor="rgba(250,250,250, 0.8)"),  # Customize hover background
      hovermode="x",  # Ensures hover appears near the data point
    )

    # Disable zooming, panning, and other interactions
    config = dict(
      displayModeBar=False,  # Hide the mode bar (zoom, pan, etc.)
      scrollZoom=False,  # Disable scroll to zoom
      dragmode=False,  # Disable dragging and panning
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
    save_var("min_pop", self.slider_1.formatted_values[0])
    save_var("max_pop", self.slider_1.formatted_values[1])

  def set_slider_text_boxes(self):
    self.text_box_left.text, self.text_box_right.text = self.slider_1.formatted_values

  def slider_1_slide(self, handle, **event_args):
    self.set_slider_text_boxes()

  def slider_1_textbox_enter(self, **event_args):
    self.slider_1.values = self.text_box_left.text, self.text_box_right.text
    self.set_slider_text_boxes()

  def slider_1_button_reset_click(self, **event_args):
    self.slider_1.reset()
    save_var("min_pop", 20)
    save_var("max_pop", 50)
    self.set_slider_text_boxes()

  def shorten_number(self, num):
    thresholds = [
      (1_000_000_000_000, "T"),  # Trillion
      (1_000_000_000, "B"),  # Billion
      (1_000_000, "M"),  # Million
      (1_000, "K"),  # Thousand
    ]

    def shorten_single_number(n):
      if n is None or not isinstance(n, (int, float)):
        return "-"
      for threshold, suffix in thresholds:
        if n >= threshold:
          return f"{n / threshold:.1f}{suffix}"
      return f"{n:.0f}"

    # If input is a list, process each number
    if isinstance(num, list):
      return [shorten_single_number(n) for n in num]
    # If input is a single number, just process it
    else:
      return shorten_single_number(num)
