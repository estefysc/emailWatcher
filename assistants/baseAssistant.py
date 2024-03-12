import openai
import os
import time
import requests
import json

from abc import ABC, abstractmethod
from openai import OpenAI

# api_key = os.environ.get("OPENAI_API_KEY")
 # Defaults to os.environ.get("OPENAI_API_KEY")
# client = OpenAI()

class BaseAssistant(ABC):
    def __init__(self, name, model="gpt-4-1106-preview"):
        # function_json = {
        #     "name": "display_quiz",
        #     "description": "Displays a quiz to the student, and returns the student's response. A single quiz can have multiple questions.",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "title": {"type": "string"},
        #             "questions": {
        #                 "type": "array",
        #                 "description": "An array of questions, each with a title and potentially options (if multiple choice).",
        #                 "items": {
        #                     "type": "object",
        #                     "properties": {
        #                         "question_text": {"type": "string"},
        #                         "question_type": {
        #                             "type": "string",
        #                             "enum": ["MULTIPLE_CHOICE", "FREE_RESPONSE"],
        #                         },
        #                         "choices": {"type": "array", "items": {"type": "string"}},
        #                     },
        #                     "required": ["question_text"],
        #                 },
        #             },
        #         },
        #         "required": ["title", "questions"],
        #     },
        # }
        get_summary_json = {
            "name": "get_summary",
            "description": "Obtains a summary of the user's unread emails. Returns a string. The string will contain the email address of the sender and how many emails from this sender are not read.",
            "parameters": { "type": "object", "properties": {}, "required": [] }
        }
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI()
        self.name = name
        self.model = model
        self.tools = [{"type": "code_interpreter"}, {"type": "function", "function": get_summary_json}]

    def _createAssistant(self, instruction):
        print("Creating assistant from BaseAssistant._createAssistant")
        assistant = self.client.beta.assistants.create(
            name = self.name,
            instructions = instruction,
            tools = self.tools,
            model = self.model
        )
        return assistant.id

    def _createThread(self, userMessage):
        thread = self.client.beta.threads.create()
        message = self.client.beta.threads.messages.create(
            thread_id = thread.id,
            role="user",
            content = userMessage
        )
        return thread.id
    
    def _modifyThread(self, threadId, userMessage):
        message = self.client.beta.threads.messages.create(
            thread_id = threadId,
            role="user",
            content = userMessage
        )
        return threadId

    def _triggerAssistant(self, threadId, assistantId):
        run = self.client.beta.threads.runs.create(
        thread_id = threadId,
        assistant_id = assistantId
        )
        return run

    def _submitToolOutputs(self, threadId, runId, toolCallId, responses):
        print("Submitting tool outputs")
        run = self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=threadId,
            run_id=runId,
            tool_outputs=[
                {
                    "tool_call_id": toolCallId,
                    "output": responses,
                }
            ],
        )
        # print("Run after submitting tool outputs: ", run)
        return run

    def _waitForRun(self, threadId, run):
        print("Waiting for run")
        # print("This is the run: ", run)
        # print("This is the run status: ", run.status)
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
            thread_id = threadId,
            run_id = run.id
            )
        time.sleep(0.5)
        # print("Run after waiting: ", run)
        return run

    def _getAssistantResponse(self, threadId):
        # Display the Assistant's Response
        messages = self.client.beta.threads.messages.list(
        thread_id = threadId
        )
        response = messages.data[0].content[0].text.value
        return response
    
    def _listAssistants(self):
        assistant_object = self.client.beta.assistants.list()
        return assistant_object
    
    def _deleteAssistant(self, assistant_id):
        """Delete an assistant by ID."""
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",  # Replace with your actual API key
            "OpenAI-Beta": "assistants=v1"
        }
        delete_url = f"https://api.openai.com/v1/assistants/{assistant_id}"
        response = requests.delete(delete_url, headers=HEADERS)
        print("Response: ", response)
        if response.status_code == 200:
            print(f"Deleted assistant with ID: {assistant_id}")
        else:
            print(f"Failed to delete assistant with ID: {assistant_id}. Status Code: {response.status_code}")

    def deleteAllAssistants(self):
        """Delete all assistants."""
        assistantsList = self._listAssistants()
        assitantsListData = assistantsList.data
        print("Assistants List length: ", len(assitantsListData))
        for i in range(len(assitantsListData)):
            self._deleteAssistant(assitantsListData[i].id)
        list = self._listAssistants()
        print("List of assistants after deletion: ", list)

    def getListOfAssistants(self):
        list = self._listAssistants()
        print("Assistant list: ", list)

    # def create_assistant(name, instructions, tools, model):
    #     assistant = client.beta.assistants.create(
    #         name=name,
    #         instructions=instructions,
    #         tools=tools,
    #         model=model
    #     )
    #     return assistant.id  # Return the assistant ID

    # Note: I think this function was created for testing purposes. Self is not being used and client is. 
    # def selectAssistant(assistant_id):
    #     assistant = client.beta.assistants.retrieve(assistant_id)
    #     return assistant.id