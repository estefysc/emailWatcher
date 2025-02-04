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
        
        # threadId = self._createThread(userMessage)
        threadId = self._createThread()
        sessionManager.addOriginalAssistantThreadIdToSession(userId, threadId)

        self._addMessageToThread(threadId, userMessage)
        run = self._triggerAssistant(threadId, assistantId)
        self._waitForRun(threadId, run)
        response = self._getAssistantResponse(threadId)

        return response

    def processUserInput(self, userInput, assistantId, threadId):
        # modifiedThreadId = self._modifyThread(threadId, userInput)
        #this is the same thread
        # modifiedThreadId = self._addMessageToThread(threadId, userInput)
        self._addMessageToThread(threadId, userInput)
        run = self._triggerAssistant(threadId, assistantId)
        print("This is run: " + str(run))
        # this should be caled completed run
        newRun = self._waitForRun(threadId, run)
        print("This is newRun: " + str(newRun))
        if newRun.required_action is not None:
            print("Accessed required action")
            tool_call = newRun.required_action.submit_tool_outputs.tool_calls[0]
            print("This is tool call: " + str(tool_call))
            tool_name = tool_call.function.name
            print("Tool name repr:", repr(tool_name))  # Shows exact string representation
            print("Tool name is:", tool_name)  # Debug print
            if tool_name == "get_summary":
                print("Entering if branch")  # Debug print
                middle = self.get_summary()
            elif tool_name == "get_generic":
                middle = "reply with something generic"

            newRunId = newRun.id
            toolCallId = tool_call.id
            newRun2 = self._submitToolOutputs(threadId, newRunId, toolCallId, middle)
            print("This is newRun2: " + str(newRun2))
            self._waitForRun(threadId, newRun2)
        else:
            print("Entering else branch")  # Debug print
            middle = "reply with something generic"

        # TODO: looks like the problem is that I am always accesing submitToolOutputs
        # newRunId = newRun.id
        # toolCallId = tool_call.id
        # newRun2 = self._submitToolOutputs(threadId, newRunId, toolCallId, middle)
        # print("This is newRun2: " + str(newRun2))
        # self._waitForRun(threadId, newRun2)
        
        response = self._getAssistantResponse(threadId)
        # print("Asistants final Response:", response)
        return response
    
    def get_summary(self):
        print("Getting summary")
        gmail = Actions.get_instance()
        summary = gmail.getSummary()
        return summary

    
    # def display_quiz(title, questions):
    #     print("Quiz:", title)
    #     print()
    #     responses = []

    #     for q in questions:
    #         print(q["question_text"])
    #         response = ""

    #         # If multiple choice, print options
    #         if q["question_type"] == "MULTIPLE_CHOICE":
    #             for i, choice in enumerate(q["choices"]):
    #                 print(f"{i}. {choice}")
    #             response = get_mock_response_from_user_multiple_choice()

    #         # Otherwise, just get response
    #         elif q["question_type"] == "FREE_RESPONSE":
    #             response = get_mock_response_from_user_free_response()

    #         responses.append(response)
    #         print()

    #     return responses
    # get_summary_json = {
    #     "name": "get_summary",
    #     "description": "Obtains a summary of the user's unread emails. Returns a string. The string will contain the email address of the sender and how many emails from this sender are not read.",
    #     "parameters": { "type": "object", "properties": {}, "required": [] }
    #     # "parameters": {
    #     #     "type": "object",
    #     #     "properties": {
    #     #         "title": {"type": "string"},
    #     #     },
    #     #     "required": [],
    #     # }
    # }
    