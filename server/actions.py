import time
import os
import secrets
from tunnel.actions import closeNgrokConnection, getNgrokPid

# make it a server manager class (singleton)

shutdown_flask_flag = False

def shutdown_flask():
    global shutdown_flask_flag
    shutdown_flask_flag = True

def monitor_shutdown_flag(logger):
    global shutdown_flask_flag
    while not shutdown_flask_flag:
        time.sleep(1)
    ngrokPidm = getNgrokPid(logger)
    closeNgrokConnection(logger, ngrokPidm)
    # will terminate the flask app
    os._exit(0)

def generate_new_secret_key():
    return secrets.token_hex(16)

def addAssistantIdToSession(self, userId, assistantId):
        session['assistants'][userId] = assistantId

def addOriginalAssistantThreadIdToSession(self, userId, threadId):
    session['originalAssistantThread'][userId] = threadId

def createSessionObjects(self, userId):
    self.__createAgentsSessionObjects()
    self.__checkUserIdInSession(userId)
    self.__createThreadSessionObjects()

def __createAgentsSessionObjects(self):
    if 'assistants' not in session:
        print("Assistants not in session. Creating object..")
        session['assistants'] = {}
    else:
        print("Assistants already in session.")

    if 'suppervisors' not in session:
        print("Supervisors not in session. Creating object..")
        session['supervisors'] = {}
    else:
        print("Supervisors already in session.")

def __createThreadSessionObjects(self):
    if 'originalAssistantThread' not in session:
        print("originalAssistantThread not in session. Creating object..")
        session['originalAssistantThread'] = {}
    else:
        print("originalAssistantThread already in session.")

    if 'originalSupervisorThread' not in session:
        print("originalSupervisorThread not in session. Creating object..")
        session['originalSupervisorThread'] = {}
    else:
        print("originalSupervisorThread already in session.")

def __checkIfAssistantExistsInSession(self, userId):
    assistantId = None
    if 'assistants' in session and userId in session['assistants']:
        assistantId = session['assistants'][userId]
    return assistantId

def __checkUserIdInSession(self, userId):
        if 'user' not in session:
            print("Adding user to session")
            session['user'] = str(userId)
            #session.modified = True
        else:
            print("User already in session")