
import googlemaps

from marshmallow import fields
from marshmallow import Schema

from flask_app   import API_KEY_GOOGLE_MAPS_PLACES
from src.classes import ResponseStatus


class SchemaCoordsLatLng(Schema):
  lat = fields.Number(required = True)
  lng = fields.Number(required = True)

class SchemaResultNearbyStoresNode(Schema):
  name     = fields.String()
  vicinity = fields.String()
  coords   = fields.Method('calc_coords')

  def calc_coords(self, node):
    return node.get('geometry', {}).get('location')

class SchemaResultNearbyStores(Schema):
  next_page_token = fields.String()
  results         = fields.List(fields.Nested(SchemaResultNearbyStoresNode))


_location = (44.793704910875114, 20.48102157162112,)
def places_nearby(
    location        = _location, *,
    next_page_token = None,
    types           = ("grocery_or_supermarket", "grocery_store", "supermarket", "shopping_mall",),
  ):
  r = ResponseStatus()
  
  try:
    gmaps = googlemaps.Client(key = API_KEY_GOOGLE_MAPS_PLACES)
    r.status = {
      'places': SchemaResultNearbyStores().dump(
        gmaps.places_nearby(
          location = location,
          type     = types,
          # name     = ('maxi', 'idea', 'univerexport', 'aroma', 'merkator', 'delhaize', 'aman', 'lidl', 'metro',),

          # radius   = 1223.33,
          rank_by  = 'distance',

          page_token = next_page_token,
        ))
    }

  except Exception as err:
    r.error = err
  
  return r.dump()


_address = 'MIhaila Milovanovića 76v, Mladenovac 11400'
_region  = 'sr'
def geocode_address(address = _address, region = _region):
  r = ResponseStatus()
  
  try:
    gmaps  = googlemaps.Client(key = API_KEY_GOOGLE_MAPS_PLACES)
    coords = SchemaCoordsLatLng().dump(
      gmaps.geocode(address, region = region)[0]['geometry']['location'])
    
    r.status = { 'coords': coords }

  except Exception as err:
    r.error = err

  return r.dump()

