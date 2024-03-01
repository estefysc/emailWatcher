from assistants.baseAssistant import BaseAssistant
from gmail.actions import Actions

import json
import time

class WhatsAssistant(BaseAssistant):
    def startInteraction(self, userId, sessionManager):
        instruction = "You are a helpful assistant specialized in managing an email account. Make your responses short and concise, and do not exceed 4096 characters in your responses."
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
        modifiedThreadId = self._modifyThread(threadId, userInput)
        run = self._triggerAssistant(modifiedThreadId, assistantId)
        newRun = self._waitForRun(modifiedThreadId, run)
        # if newRun.required_action is not None:
        print("Accessed required action")
        tool_call = newRun.required_action.submit_tool_outputs.tool_calls[0]
        name = tool_call.function.name
        # arguments = json.loads(tool_call.function.arguments)
        # responses = self.get_summary(arguments["title"], arguments["questions"])
        # if name == "get_summary":
        #     print("Accessed if statement")
        responses = self.get_summary()
        newRunId = newRun.id
        toolCallId = tool_call.id
        newRun2 = self._submitToolOutputs(modifiedThreadId, newRunId, toolCallId, responses)
        self._waitForRun(modifiedThreadId, newRun2)
        response = 'This is a test response'
        # response = self._getAssistantResponse(modifiedThreadId)
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
    