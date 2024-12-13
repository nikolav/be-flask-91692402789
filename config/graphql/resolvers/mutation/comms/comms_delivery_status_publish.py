
from config.graphql.init         import mutation
from src.classes                 import ResponseStatus
from models.assets               import Assets
from models.assets               import AssetsType
from flask_app                   import db
from utils.geo                   import haversine_distance
from servcies.firebase.messaging import notification_send


# commsDeliveryStatusPublish(site: JsonData!): JsonData!
@mutation.field('commsDeliveryStatusPublish')
def resolve_commsDeliveryStatusPublish(_obj, _info, site):
  # site: {name:string, coords:{lat:number, lng:number}, vicinity:string:address}
  
  r   = ResponseStatus()
  
  # nearest group
  g   = None

  tokens    = set()
  responses = []

  try:
    
    # from groups with non-empty @data.coords
    lsa_groups_with_location = db.session.scalars(
      db.select(
        Assets
      ).where(
        AssetsType.PEOPLE_GROUP_TEAM.value == Assets.type,
        Assets.data['coords']['lat'].is_not(None),
        Assets.data['coords']['lng'].is_not(None),
      ))
    
    # calc min-distanced group from provided input point
    g = min(lsa_groups_with_location, 
          key = lambda a: haversine_distance(site['coords'], a.data['coords']),
        )
    
    # send notifications
    for u in g.users:
      tokens.update(u.cloud_messaging_device_tokens())
    
    if 0 < len(tokens):
      responses.append(
        notification_send(
          tokens  = list(tokens),
          payload = {
            'title' : 'Obaveštenje | 🚛 Isporuka',
            'body'  : f'🏪[{site['name']}] {site['vicinity']}',
          },
          # image   = image_
        ))

    
  except Exception as err:
    r.error = err
  
    
  r.status = { 'gname': g.name if g else None, 'responses': [str(res) for res in responses] }
  return r.dump()

  