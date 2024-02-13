from assistants.baseAssistant import BaseAssistant

class WhatsAssistant(BaseAssistant):
    def startInteraction(self, userId, sessionManager):
        instruction = "You are a helpful assistant specialized in managing an email account."
        assistantId = self._createAssistant(instruction)
        sessionManager.addAssistantIdToSession(userId, assistantId)
        userMessage = "Welcome me to the application."
        threadId = self._createThread(userMessage)
        sessionManager.addOriginalAssistantThreadIdToSession(userId, threadId)
        run = self._triggerAssistant(threadId, assistantId)
        self._waitForRun(threadId, run)
        response = self._getAssistantResponse(threadId)
        return response

    def processUserInput(self, userInput, assistantId, threadId):
        modifiedThread = self._modifyThread(threadId, userInput)
        run = self._triggerAssistant(modifiedThread, assistantId)
        self._waitForRun(modifiedThread, run)
        response = self._getAssistantResponse(modifiedThread)
        return response