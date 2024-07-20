import anvil.server
from anvil_extras import routing


def click_link(element, target, event_args):
  if event_args:
    if event_args['keys']['ctrl'] is True:
      element.url = f"{anvil.server.get_app_origin()}/#{target}"
    else:
      element.url = ''
      routing.set_url_hash(target)
  else:
    element.url = ''
    routing.set_url_hash(target)

def click_button(target, event_args):
  if event_args['keys']['ctrl'] is True:
    anvil.js.window.open(f"{anvil.server.get_app_origin()}/#{target}", '_blank')
  else:
    routing.set_url_hash(target)
