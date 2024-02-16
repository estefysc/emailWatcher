from __future__ import print_function

import os.path
import re
import pprint

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# This class is a singleton, but shouldn't the constructor be omitted?
# TODO: Check if this can be implemented better
class Actions:
    _instance = None

    # Static method to fetch the current instance.
    @staticmethod
    def get_instance():
       if not Actions._instance:
           Actions()
       return Actions._instance
    
    def __init__(self):
        if Actions._instance is None:
            # This is a list of dictionaries - unreadMessage object = {'id': '1899df5996b78573', 'threadId': '1899df5996b78573'} 
            self.__unreadMessages = []
            # TODO: delete? Currently not used
            self.__idEmailMap = {}
            # This is a dictionary with the senders' email address as the key and the amount of emails as the value
            self.__senders = {}
            # This is a list of dictionaries that follows the below structure
            # self.__masterEmailDictionary = {
            #     "alice@example.com": [
            #         {"msgId": "112414", "subject": "Welcome"},
            #         {"msgId": "2341234", "subject": "Offers"}
            #     ],
            #     # ...
            # }
            self.__masterEmailDictionary = {}

            # If modifying these scopes, delete the file token.json.
            SCOPES = ['https://mail.google.com/']

            creds = None

            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            
            # if invalid_grant: Token has been expired or revoked error, delete the token.json file to generate a new token.json file
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)

            # If there are no (valid) credentials available, let the user log in.
            # TODO: Try to catch the exception when the token expires and send a notification informing me. 
            # 
            # from google.auth.exceptions import RefreshError
            # try:
            #     # Your existing code for refreshing credentials
            #     if creds and creds.expired and creds.refresh_token:
            #         creds.refresh(Request())
            # except RefreshError as e:
            #     # e.response is the HTTP response, which contains the status code and the body
            #     status_code = e.response.status_code
            #     response_body = e.response.text

            #     if status_code == 400:
            #         print("Received 400 None error:")
            #         print(response_body)
            #         # Here you can log the error, send a notification, etc.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            Actions._instance = self

            try:
                # Call the Gmail API
                self.service = build('gmail', 'v1', credentials=creds)
            except HttpError as error:
                # TODO(developer) - Handle errors from gmail API.
                print(f'An error occurred: {error}')
        else:
            raise Exception("You cannot create another Actions class")

    def __extract_email_address(self, input_string):
        # Define the regular expression pattern to match an email address
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

        # Use re.search() to find the first occurrence of the email pattern in the input string
        match = re.search(email_pattern, input_string)

        # If a match is found, return the email address; otherwise, return None
        return match.group() if match else None
    
    def __insertIntoMasterEmailDictionary(self, fromEmail, messageId, subjectLine):
        if self.__masterEmailDictionary.get(fromEmail, None) is None:
            self.__masterEmailDictionary[fromEmail] = []
        
        messageDictionary = {"msgId": messageId, "subject": subjectLine}
        self.__masterEmailDictionary[fromEmail].append(messageDictionary)

    def __insertIntoSenders(self, messageId):
        """
        Populates the senders dictionary. It also calls the function that populates the masterEmailDictionary and the idEmailMap.
        """
        try:
            results = self.service.users().messages().get(userId='me', id=messageId).execute()
            payload = results.get('payload', {})
            headers = payload.get('headers', [])
            fromHeader = ''
            subjectHeader = ''

            # Keep in mind that the order of the headers is not guaranteed
            for header in headers:
                if header['name'] == 'From':
                    fromHeader = header   
                if header['name'] == 'Subject':
                    subjectHeader = header
                    
            fromEmail = self.__extract_email_address(fromHeader['value']).lower()
            subjectLine = subjectHeader['value']
            self.__insertIntoIdEmailMap(messageId, fromEmail)
            self.__senders[fromEmail] = self.__senders.get(fromEmail, 0) + 1
            self.__insertIntoMasterEmailDictionary(fromEmail, messageId, subjectLine)

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')
    
    def __insertIntoIdEmailMap(self, messageId, fromEmail):
        self.__idEmailMap[messageId] = fromEmail

    def __getUnreadMessages(self):
        """
        This function populates the self.__unreadMessages variable and returns the amount of unread messages. It also calls the function that
        populates the self.__senders dictionary
        """
        amountOfUnreadMessages = 0
        try:
            # Get all unread messages
            results = self.service.users().messages().list(userId='me', labelIds=['UNREAD'], maxResults=30).execute()
            self.__unreadMessages = results.get('messages', [])
           
            if not self.__unreadMessages:
                print ('No new messages found.')
            else:
                for message in self.__unreadMessages:
                    self.__insertIntoSenders(message['id'])
                    amountOfUnreadMessages += 1
            
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')
        
        return amountOfUnreadMessages
    
    def getProperty(self, property):
        if property == 'unreadMessages':
            return self.__unreadMessages
        elif property == 'senders':
            return self.__senders
        elif property == 'idEmailMap':
            return self.__idEmailMap
        else:
            return None
    
    def getSummary(self):
        """
        After the class is instantiated, this function should be called to kick off the process of getting the unread messages
        """
        amountUnread  = self.__getUnreadMessages()
        unreadReport = self.__senders
        filteredReport = ''

        for key, value in unreadReport.items():
            filteredReport += f"{key}: {value}\n"

        # The maximum WhatsApp message size is 4096 characters
        if len(filteredReport) < 4096:
            return f'You have {amountUnread} unread emails. Here is your summary:\n{filteredReport}'
        else:
            return 'You have too many unread messages. The summary exceeds the maximum WhatsApp message size allowed.'
    
    def askForInstructions(self):
        instructions = 'What would you like to do? Please respond with a number: 1 = Delete all unread messages, 2 = Delete some unread messages, 3 = Keep all unread messages, or 4 = Talk to assistant (if you no longer want to talk to the assistant, respond with "exit")'
        return instructions
    
    def deleteAllUnreadMessages(self):
        try:
            # suggested by copilot
            results = self.service.users().messages().batchDelete(userId='me', body={'ids': [message['id'] for message in self.__unreadMessages]}).execute()
            
            if not results:
                # Update the senders dictionary and the unreadMessages list
                self.__unreadMessages.clear()
                self.__senders.clear()
                return('All your unread emails have been deleted.')
            else:
                return('There was an error deleting your unread emails.')
                
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')

    def deleteSomeUnreadMessages(self, userResponse):
        """
        This function will delete all messages except the ones from the specified email addresses.
        """
        # Extracts the email addresses from the user's response. if email.strip() != '' is used to remove empty strings from the list
        emailsToKeep = [email.strip() for email in userResponse.split(',') if email.strip() != '']
        messageIdsToDelete = []

        for emailAddress, messages in self.__masterEmailDictionary.items():
            if emailAddress not in emailsToKeep:
                messageIdsToDelete.extend([message['msgId'] for message in messages])

        try:
            # suggested by copilot
            # if messageIdsToDelete is not empty
            if len(messageIdsToDelete) > 0:
                results = self.service.users().messages().batchDelete(userId='me', body={'ids': messageIdsToDelete}).execute()
                if not results:
                    #TODO: Update the senders dictionary and the unreadMessages list??? WHAT ELSE NEEDS TO BE UPDATED AFTER DELETING SOME EMAILS?
                    return('I kept the emails that were sent from the email addresses you specified. The rest have been deleted.')
                else:
                    return('There was an error deleting your unread emails.')
            else:
                return('You decided to keep the only unread email you had. I did not delete any emails.')
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')

    def getSpecificMessageContents(self, messageId):
        """
        Instance of Message example
        {
            "id": string,
            "threadId": string,
            "labelIds": [
                string
            ],
            "snippet": string,
            "historyId": string,
            "internalDate": string,
            "payload": {
                object (MessagePart)
            },
            "sizeEstimate": integer,
            "raw": string
        }
        """

        # Get a specific message and its contents
        results = self.service.users().messages().get(userId='me', id= messageId).execute()
        
        id = results.get('id', '')
        threadId = results.get('threadId', '')
        labelIds = results.get('labelIds', [])
        snippet = results.get('snippet', '')
        historyId = results.get('historyId', '')
        internalDate = results.get('internalDate', '')
        payload = results.get('payload', {})
        sizeEstimate = results.get('sizeEstimate', '')
        raw = results.get('raw', '')

        pprint.pprint(f'Payload: {payload}')
        
    def getInboxLabels(self):
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            if not labels:
                print('No labels found.')
                print('')
                return
            print('Inbox labels: ')
            for label in labels:
                print (label['name'])
            print('')
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')