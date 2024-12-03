
import json

from config.graphql.init import mutation
from src.classes         import ResponseStatus
from flask_app           import VIBER_CHANNELS_CACHEID


# viberChannelSetupChannelsDrop(channelNames: [String!]!): JsonData!
@mutation.field('viberChannelSetupChannelsDrop')
def resolve_viberChannelSetupChannelsDrop(_obj, _info, channelNames = []):
  r   = ResponseStatus()
  res = None

  try:

    if channelNames:
      from flask_app import redis_client
      _err, client = redis_client

      channels = json.loads(client.get(VIBER_CHANNELS_CACHEID).decode())

      # if has channels to drop
      if any(ch in channels for ch in channelNames):
        # reset channels cache
        #  copy uncleared keys
        res = client.set(
          VIBER_CHANNELS_CACHEID,
          json.dumps(
            { ch_name: ch_info for ch_name, ch_info in channels.items() 
                if not ch_name in channelNames }))


  except Exception as err:
    r.error = err


  else:
    r.status = str(res)


  return r.dump()




