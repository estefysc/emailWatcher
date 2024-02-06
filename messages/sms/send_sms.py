# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

def sendSMS():
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure

    # Load the credentials from the config.cfg file
    account_sid = ''
    auth_token = ''

    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                        body='',
                        from_='',
                        to=''
                    )

    print(message.sid)