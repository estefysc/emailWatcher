from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from tunnel.actions import startNgrok, getNgrokPid
from gmail.actions import Actions
from messages.whatsapp.send_whats import WhatsApp
from server.actions import ServerManager
from server.sessionManager import SessionManager  
from assistants.whatsAssistant import WhatsAssistant

import threading
import time
import logging

app = Flask(__name__)

# TODO: how to deal with gmail token expiring

@app.route("/", methods=['GET', 'POST'])
def bot():
    # TODO: create a funcition for this behavior and make the bot() function call it
    """
    Handles incoming WhatsApp messages and manages the email management bot's responses.
    
    This function processes incoming messages through a Twilio webhook and manages different
    conversation states through Flask sessions. It supports the following features:
    
    - Deleting all unread emails (Option 1)
    - Deleting specific unread emails while keeping others (Option 2)
    - Keeping all unread emails (Option 3)
    - Interacting with an AI assistant (Option 4)
    
    The function maintains different session states:
    - 'deleting_specific_emails': Processing email addresses to keep
    - 'will_stop_app': Preparing to shut down the application
    - 'talking to assistant': Engaging with the AI assistant
    
    Returns:
        str: A TwiML response containing the bot's message
    """
    
    # creating response object - TwiML response object
    response = MessagingResponse()
    assistant = WhatsAssistant("Email Watcher Assistant")
    session_manager = SessionManager.get_session_manager_instance()
    # user input
    userResponse = request.values.get('Body', '').lower()
    print('User response: ' + userResponse)
    userId = request.values.get('From', None)
    print('User ID: ' + userId)
    print('Session: ' + str(session))

     # Check if the user is in the process of deleting specific emails
    if session.get('status') == 'deleting_specific_emails':
        session['status'] = 'will_stop_app'
        gmail = Actions.get_instance()
        # Handle deletion of specific emails
        response.message(gmail.deleteSomeUnreadMessages(userResponse))
        # Reset the state
        response.message('Now remember to close the connection by sending me another message.') 
    elif session.get('status') == 'will_stop_app':
        server_manager = ServerManager.get_server_instance()
        # clearing the session - TODO: Is this really needed? Had issues before with the session sticking from previous runs. This seems to have been related to using the same
        # secret key for the session. I changed it to use a new random one on every run, and it seems to be working fine now.
        for key in list(session.keys()):
            # TODO: get this into the logger
            print('Deleting session key: ' + key)
            session.pop(key)
        server_manager.shutdown_flask()
    elif session.get('status') == 'talking to assistant':
        if userResponse == 'exit':
            session['status'] = 'will_stop_app'
            response.message('Now remember to close the connection by sending me another message.')
            print(response)
            assistant.deleteAllAssistants()
        else:
            print('Accessed talking to assistant')
            assistanId = session_manager.checkIfAgentInSession(userId)
            print('Obtained assistantId = ' + assistanId)
            assistantThreadId = session_manager.getAssistantThreadIdFromSession(userId)
            print('Obtained assistantThreadId = ' + assistantThreadId)
            assistantResponse = assistant.processUserInput(userResponse, assistanId, assistantThreadId)
            print('Obtained Assistant response = ')
            print(assistantResponse)
            
            # NOTE: if the response is too long, the message will not be sent.
            response.message(assistantResponse)
    else:
        match userResponse:
            case '1': 
                session['status'] = 'will_stop_app' 
                gmail = Actions.get_instance()
                response.message(gmail.deleteAllUnreadMessages()) 
                response.message('Now remember to close the connection by sending me another message.') 
            case '2':
                # Keep specific unread messages
                response.message('Give me the email addresses of the emails you want to keep separated by a comma') 
                # Set the state
                session['status'] = 'deleting_specific_emails' 
            case '3':
                # Keep all the unread messages
                session['status'] = 'will_stop_app'
                response.message('All your unread messages will be kept. Now remember to close the connection by sending me another message.')
            case '4':
                # talk to assistant
                session['status'] = 'talking to assistant'
                session_manager.createSessionObjects(userId)
                assistantResponse = assistant.startInteraction(userId, session_manager)
                response.message(assistantResponse)
    return str(response)

def runApp():
    """
    Initializes and runs the Flask application server.
    
    This function:
    - Gets an instance of the ServerManager
    - Generates a new secret key for the Flask session
    - Starts the Flask application on port 8000
    
    Note:
        The secret key is regenerated on each run to prevent session persistence between application restarts, 
        which adds an extra layer of security by ensuring that old session data is invalidated. 
        This is particularly useful for personal tools where session persistence is not required, and you want 
        to ensure that session hijacking or tampering is minimized. However, in production environments, if session 
        persistence across restarts is necessary, a fixed secret key should be used and stored securely to maintain session continuity.
    """

    server_manager = ServerManager.get_server_instance()
    app.secret_key = server_manager.generate_new_secret_key()
    # if we need to handle multiple http requests at the same time, threaded=True needs to be set
    app.run(port=8000, debug=False)
    
def initProcess(logger):
    """
    Initializes the email management service and sends the initial WhatsApp messages.
    
    This function performs the following steps:
    1. Creates WhatsApp and Gmail service instances
    2. Retrieves a summary of unread emails
    3. Sends an initial WhatsApp message to confirm connection
    4. Sends the email summary via WhatsApp
    5. Sends instructions for available email management options
    
    Args:
        logger: A logging.Logger instance for debug message logging
    """

    whatsApp = WhatsApp()
    gmail = Actions.get_instance()
    summary = gmail.getSummary()
    
    sid = whatsApp.sendInitialMessage()
    if sid:
        logger.debug('Initial message sent!')

    whatsApp.sendWhats(summary, logger)
    whatsApp.sendWhats(gmail.askForInstructions(), logger)

if __name__ == '__main__':
    """
    Main execution block for the Email Watcher application.
    
    This script initializes and runs a WhatsApp-based email management service that allows users
    to manage their unread emails through WhatsApp messages. The application runs three main
    threads:
    
    1. Flask Application Thread: Handles incoming WhatsApp webhook requests
    2. Initialization Thread: Sets up WhatsApp connection and sends initial messages
    3. Monitor Thread: Watches for shutdown signals
    
    The application uses ngrok to create a secure tunnel for webhook communication and
    maintains both server and session management for handling multiple users.
    
    Note:
        The WhatsApp sandbox has a 72-hour expiration period. This is handled through
        automated daily messages via iPhone shortcuts to maintain the sandbox connection.
    """

    # Create and configure logger
    logging.basicConfig(filename='emailWatcher.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logger = logging.getLogger('emailWatcher')
    server_manager = ServerManager()
    session_manager = SessionManager()

    # Start ngrok tunnel
    #TODO: should I receive the proc or create a class and make it a property?
    startNgrok()

    # Create threads
    appThread = threading.Thread(target=runApp)
    initProcessThread = threading.Thread(target=initProcess, args=(logger,))
    monitorThread = threading.Thread(target=server_manager.monitor_shutdown_flag, args=(logger,))

    # Start Flask app
    appThread.start()
    time.sleep(1)

    # Start initial process
    initProcessThread.start()
    time.sleep(1)

    monitorThread.start()


    

