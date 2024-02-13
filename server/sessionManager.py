import threading

from flask import session

class SessionManager:
    """
    If SessionManager is meant to provide a centralized way to manage session data that is consistent across the application, 
    and there's no need for different states of session management for different users or contexts, 
    then a Singleton pattern is suitable. However, if the SessionManager needs to handle user-specific data differently for each session, 
    or if you want more flexibility for testing or extending its functionality, then it would be better not to implement it as a Singleton.
    """
    _session_manager_instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._session_manager_instance is None:
                cls._session_manager_instance = super().__new__(cls, *args, **kwargs)
            return cls._session_manager_instance
        
    @classmethod
    def get_session_manager_instance(cls):
        return cls._session_manager_instance

    def addAssistantIdToSession(self, userId, assistantId):
        session['assistants'][userId] = assistantId

    def addOriginalAssistantThreadIdToSession(self, userId, threadId):
        session['originalAssistantThread'][userId] = threadId

    def createSessionObjects(self, userId):
        self.__createAgentsSessionObjects()
        self.__checkUserIdInSession(userId)
        self.__createThreadSessionObjects()

    def checkIfAgentInSession(self, userId):
        assistantId = None
        if 'assistants' in session and userId in session['assistants']:
            assistantId = session['assistants'][userId]
        return assistantId
    
    def getAssistantThreadIdFromSession(self, userId):
        threadId = None
        if 'originalAssistantThread' in session and userId in session['originalAssistantThread']:
            threadId = session['originalAssistantThread'][userId]
        return threadId

    def __createAgentsSessionObjects(self):
        if 'assistants' not in session:
            print("Assistants not in session. Creating object..")
            session['assistants'] = {}
        else:
            print("Assistants already in session.")


    def __createThreadSessionObjects(self):
        if 'originalAssistantThread' not in session:
            print("originalAssistantThread not in session. Creating object..")
            session['originalAssistantThread'] = {}
        else:
            print("originalAssistantThread already in session.")

    # def __checkIfAssistantExistsInSession(self, userId):
    #     assistantId = None
    #     if 'assistants' in session and userId in session['assistants']:
    #         assistantId = session['assistants'][userId]
    #     return assistantId

    def __checkUserIdInSession(self, userId):
            if 'user' not in session:
                print("Adding user to session")
                session['user'] = str(userId)
                #session.modified = True
            else:
                print("User already in session")