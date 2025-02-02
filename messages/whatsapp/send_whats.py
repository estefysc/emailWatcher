from twilio.rest import Client
from configparser import ConfigParser

import os

class WhatsApp:
  def __init__(self):
    self.reader = ConfigParser()
    # Get the directory of the current file
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # Construct the path to config.cfg in the root directory
    config_path = os.path.join(root_dir, 'config.cfg')
    self.reader.read(config_path)
    self.account_sid = self.reader.get('WHATSAPP', 'ACCOUNT_SID')
    self.auth_token = self.reader.get('WHATSAPP', 'AUTH_TOKEN')
    self.client = Client(self.account_sid, self.auth_token)

  def sendInitialMessage(self):
    message = self.client.messages.create(
      from_=self.reader.get('MESSAGES', 'FROM_NUMBER'),
      body='The Email Watcher is now active!',
      to=self.reader.get('MESSAGES', 'TO_NUMBER')
    )
    return message.sid

  def sendWhats(self, userResponse, logger):
    logger.debug(f'Sending user response: {userResponse}')
    message = self.client.messages.create(
      from_=self.reader.get('MESSAGES', 'FROM_NUMBER'),
      body=userResponse,
      to=self.reader.get('MESSAGES', 'TO_NUMBER')
    )