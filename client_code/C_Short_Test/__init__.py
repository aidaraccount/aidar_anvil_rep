from ._anvil_designer import C_Short_TestTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class C_Short_Test(C_Short_TestTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.
    self.html = f"""
    <div class="masonry-item-test">
      <iframe src="{data["external_url"]}/embed/?omitscript=true&hidecaption=true"
        width="300"
        frameborder="0" scrolling="no"
        allowtransparency="true" allowfullscreen="true">
      </iframe>      
    </div>
    """

    # self.html = f"""
    # <div class="masonry-item">
    #   <iframe id="instaFrame" src="{data["external_url"]}/embed/?omitscript=true&hidecaption=true"
    #     width="400" height="480"
    #     frameborder="0" scrolling="no"
    #     allowtransparency="true" allowfullscreen="true">
    #   </iframe>
    # </div>
    
    # <script>
    #   function adjustIframeHeight() {{
    #     var iframe = document.getElementById('instaFrame');
    #     if (!iframe) return;
    
    #     iframe.onload = function() {{
    #       setTimeout(() => {{
    #         try {{
    #           var newHeight = iframe.contentWindow.document.body.scrollHeight;
    #           if (newHeight) {{
    #             iframe.style.height = newHeight + "px";
    #           }}
    #         }} catch (e) {{
    #           console.warn("Cannot access iframe content due to cross-origin restrictions.");
    #         }}
    #       }}, 1000); // Delay for loading
    #     }};
    #   }}
    
    #   window.addEventListener("load", adjustIframeHeight);
    # </script>
    # """

    