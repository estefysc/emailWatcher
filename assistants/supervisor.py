from assistants.baseAssistant import BaseAssistant

class Supervisor(BaseAssistant):
    def startInteraction(self, userId, db):
        instruction = "You play the role of user's response supervisor. You will determine if the user is still providing information or if the user has mentioned he or she is done providing information. You will be recieving the user's responses, and you will have to analyze the context of the responses in order to decide which action to take, either to continue gathering information or to input the information in the database and create a buying plan."
        supervisorId = self._createAssistant(instruction)
        db.addSupervisorIdToSession(userId, supervisorId)
        userMessage = "You will analyze the context of the response and respond with two possible words, either continue or stop. That decision will depend on whether the response provided indicates that gathering information should continue or if it is time to stop to store the data in the database and calculate consumption. Make your deciion on the current answer, meaning that expect the user to clearly state he or she is done providing information in orser to stop. Do not assume that just because a user has provided information on the complete consumption of an item, the user has given a full account of their purchases. After providing the word, proide your rationale for choosing the word."
        threadId = self._createThread(userMessage)
        db.addOriginalSupervisorThreadIdToSession(userId, threadId)
        run = self._triggerAssistant(threadId, supervisorId)
        self._waitForRun(threadId, run)
        response = self._getAssistantResponse(threadId)
        print(response)
        
    def analizeResponse(self, response, suppervisorId, threadId):
        modifiedThread = self._modifyThread(threadId, response)
        run = self._triggerAssistant(modifiedThread, suppervisorId)
        self._waitForRun(modifiedThread, run)
        response = self._getAssistantResponse(modifiedThread)
        return response