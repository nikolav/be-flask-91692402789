import os
from dotenv import load_dotenv
from twilio.rest import Client


load_dotenv()
TWILIO_ACCOUNT_SID  = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN   = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

account_sid      = TWILIO_ACCOUNT_SID
auth_token       = TWILIO_AUTH_TOKEN
twilio_number    = TWILIO_PHONE_NUMBER
recipient_number = '+381665725523'

# Create Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms(*, 
             body,
             recipient_number,
             twilio_number = TWILIO_PHONE_NUMBER):
  message = client.messages.create(
      body  = body,
      from_ = twilio_number,
      to    = recipient_number
  )

  return message

# print(f'Message sent with SID: {message.sid}')

