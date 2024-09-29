from firebase_admin import messaging


def fcm_send(tokens, payload):
  return messaging.send_each(
    [messaging.Message(
                token = token, 
                data  = payload
              ) for token in tokens])

