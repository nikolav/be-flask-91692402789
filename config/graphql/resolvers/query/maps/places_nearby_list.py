
from config.graphql.init import query
from servcies.googlemaps import places_nearby


# googleapisPlacesNearby(location: JsonData!, next_page_token: String): JsonData!
@query.field('googleapisPlacesNearby')
def resolve_googleapisPlacesNearby(_obj, _info, location, next_page_token = None):
  return places_nearby(location, next_page_token = next_page_token)

