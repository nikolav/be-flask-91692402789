from firebase_admin import messaging


def send(*, tokens, message_payload):
  message = messaging.MulticastMessage(
    notification = messaging.Notification(**message_payload),
    tokens = list(tokens)
  )
  return messaging.send_multicast(message)

