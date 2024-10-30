from firebase_admin import messaging


def notification_send(*, tokens, payload, image = None):
  return messaging.send_each(
    [messaging.Message(
        notification = messaging.Notification(
          title = payload['title'],
          body  = payload['body'],
          image = image,
        ),
        data  = payload.get('data'),
        token = token,
      ) for token in tokens]
  )


def fcm_send(tokens, payload):
  return messaging.send_each(
    [messaging.Message(
                token = token, 
                data  = payload,
              ) for token in tokens])


def message_silent_send(*args, **kwargs):
  return fcm_send(*args, **kwargs)


