from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from tunnel.actions import startNgrok
from gmail.actions import Actions
from messages.whatsapp.send_whats import WhatsApp
from server.actions import ServerManager

import threading
import time
import logging

app = Flask(__name__)

# TODO: how to deal with sandbox expiring every 72 hours - check email about using text messages:
# This is currently being solved by using the "shortcuts" app on the Iphone to send a daily message to the whatsapp sandbox number.

# TODO: how to deal with gmail token expiring

# Whatsapp Bot actions
@app.route("/", methods=['GET', 'POST'])
def bot():
    server_manager = ServerManager.get_server_instance()
    userId = request.values.get('From', None)
    gmail = Actions.get_instance()
    # creating response object - TwiML response object
    response = MessagingResponse()
    # user input
    userResponse = request.values.get('Body', '').lower()

     # Check if the user is in the process of deleting specific emails
    if session.get(userId) == 'deleting_specific_emails':
        session[userId] = 'will_stop_app'
        # Handle deletion of specific emails
        response.message(gmail.deleteSomeUnreadMessages(userResponse))
        # Reset the state
        response.message('Now remember to close the connection by sending me another message.') 
    elif session.get(userId) == 'will_stop_app':
        # clearing the session - TODO: Is this really needed? Had issues before with the session sticking from previous runs. This seems to have been related to using the same
        # secret key for the session. I changed it to use a new random one on every run, and it seems to be working fine now.
        for key in list(session.keys()):
            # TODO: get this into the logger
            print('Deleting session key: ' + key)
            session.pop(key)
        server_manager.shutdown_flask()
    else:
        match userResponse:
            case '1':
                # response.message('Respond with "yes" if you want to delete all unread messages.') 
                # session[userId] = 'deleting_all_unread'
                session[userId] = 'will_stop_app' 
                response.message(gmail.deleteAllUnreadMessages()) 
                response.message('Now remember to close the connection by sending me another message.') 
            case '2':
                # Keep specific unread messages
                response.message('Give me the email addresses of the emails you want to keep separated by a comma') 
                # Set the state
                session[userId] = 'deleting_specific_emails' 
            case '3':
                # Keep all the unread messages
                session[userId] = 'will_stop_app'
                response.message('All your unread messages will be kept. Now remember to close the connection by sending me another message.')
    return str(response)

def runApp():
    server_manager = ServerManager.get_server_instance()
    app.secret_key = server_manager.generate_new_secret_key()
    app.run(port=8000, debug=False)
    
def initProcess():
    whatsApp = WhatsApp()
    gmail = Actions.get_instance()
    summary = gmail.getSummary()

    sid = whatsApp.sendInitialMessage()
    if sid:
        logger.debug('Initial message sent!')

    whatsApp.sendWhats(summary)
    whatsApp.sendWhats(gmail.askForInstructions())

def test():
    gmail = Actions.get_instance()
    summary = gmail.getSummary()
    # print(summary)
    # print('This is Unread Messages' + str(gmail.getProperty('unreadMessages')))
    # print('This is senders' + str(gmail.getProperty('senders')))
    # print('This is idEmailMap' + str(gmail.getProperty('idEmailMap')))

    id = gmail.getProperty('unreadMessages')
    idToUse = id[0]['id']
    #print(idToUse)
    #gmail.getSpecificMessageContents(idToUse)

# Note that the whatsapp sandbox membership lasts 72 hours. After that, you need to request access again.
# netstat -ano | findStr "8000" - to check process and if port is in use
if __name__ == '__main__':
    # Create and configure logger
    logging.basicConfig(filename='emailWatcher.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logger = logging.getLogger('emailWatcher')
    ServerManager.init_server_manager()
    server_manager = ServerManager.get_server_instance()

    # Start ngrok tunnel
    #TODO: should I return proc or create a class and make it a property?
    startNgrok()
    
    # Create threads
    appThread = threading.Thread(target=runApp)
    initProcessThread = threading.Thread(target=initProcess)
    monitorThread = threading.Thread(target=server_manager.monitor_shutdown_flag, args=(logger,))

    # Start Flask app
    appThread.start()
    time.sleep(1)

    # Start initial process
    initProcessThread.start()
    time.sleep(1)

    monitorThread.start()


    

