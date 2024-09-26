from firebase_admin import messaging


def send(*, tokens, payload):  
  return messaging.send_each(
    [messaging.Message(
      token = tok, 
      data  = payload,
    ) for tok in tokens])

