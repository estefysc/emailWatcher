from assistants.baseAssistant import BaseAssistant
from gmail.actions import Actions

import json
import time

class WhatsAssistant(BaseAssistant):
    def startInteraction(self, userId, sessionManager):
        instruction = "You are a helpful assistant specialized in managing an email account. Make your responses short and concise, and do not exceed 4096 characters in your responses."
        # The assistant currently has a tool called get_generic. Its description states that it is to be used to respond generically to the user's message. 
        # For now This userMessage is indicating to the assistant that it does not need to use any tools as a response to this first message. Otherwise 
        # the assistant tries to use this tool but calling a function for it has not been implemented yet.
        userMessage = "Welcome me to the application. You do not need to use any tools as a response to this first message."
        
        assistantId = self._createAssistant(instruction)
        sessionManager.addAssistantIdToSession(userId, assistantId)
        
        threadId = self._createThread()
        sessionManager.addOriginalAssistantThreadIdToSession(userId, threadId)

        self._addMessageToThread(threadId, userMessage)
        run = self._triggerAssistant(threadId, assistantId)
        # the processed run is not used anywhere because we do not need to check for any tool calls.
        # TODO: create a functin that checks for tool calls??
        processedRun =self._waitForRun(threadId, run)
        response = self._getAssistantResponse(threadId)

        return response

    def processUserInput(self, userInput, assistantId, threadId):
        self._addMessageToThread(threadId, userInput)
        run = self._triggerAssistant(threadId, assistantId)
        # print("This is run: " + str(run))
        # this should be caled completed run
        processedRun = self._waitForRun(threadId, run)
        # print("This is processedRun: " + str(processedRun))

        if processedRun.required_action is not None:
            self.executeTool(processedRun, threadId)

        response = self._getAssistantResponse(threadId)
        # print("Asistants final Response:", response)
        return response
    
    def getEmailSummary(self):
        print("Getting summary")
        gmail = Actions.get_instance()
        summary = gmail.getSummary()
        return summary
    
    def getGenericResponse(self):
        print("Getting generic response")
        return "reply with something generic"
    
    def executeTool(self, processedRun, threadId):
        tool_call = processedRun.required_action.submit_tool_outputs.tool_calls[0]
        # print("This is tool call: " + str(tool_call))
        tool_name = tool_call.function.name
        # print("Tool name repr:", repr(tool_name))  # Shows exact string representation
        # print("Tool name is:", tool_name)  

        if tool_name == "get_summary":
            # print("Entering if branch")  
            contextOutput = self.getEmailSummary()
        elif tool_name == "get_generic":
            # print("Entering elif branch get_generic")
            contextOutput = self.getGenericResponse()

        toolCallId = tool_call.id
        runAfterToolExecution = self._submitToolOutputs(threadId, processedRun.id, toolCallId, contextOutput)
        # print("This is runAfterToolExecution: " + str(runAfterToolExecution))
        self._waitForRun(threadId, runAfterToolExecution)
    
    
    

    