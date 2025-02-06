import openai
import os
import time
import requests
import json
import configparser
from abc import ABC, abstractmethod
from openai import OpenAI

class BaseAssistant(ABC):
    def __init__(self, name, model="gpt-4-1106-preview"):
    # def __init__(self, name, model="gpt-4o-mini-2024-07-18"):
        # Note: To see the complete structure of a tool function, see the notes.md file.
        get_summary_json = {
            "name": "get_summary",
            "description": "Obtains a summary of the user's unread emails. Returns a string. The string will contain the email address of the sender and how many emails from this sender are not read.",
            "parameters": { "type": "object", "properties": {}, "required": [] }
        }
        get_generic_json = {
            "name": "get_generic",
            "description": "Generic response to the user's message.",
            "parameters": { "type": "object", "properties": {}, "required": [] }
        }

        config = configparser.ConfigParser()
        config.read('config.cfg')
        
        self.api_key = config['OpenAI']['OPENAI_API_KEY']
        self.client = OpenAI(api_key=self.api_key)
        self.name = name
        self.model = model
        # self.tools = [{"type": "code_interpreter"}, {"type": "function", "function": get_summary_json}]
        self.tools = [
            # {"type": "code_interpreter"}, 
            {"type": "function", "function": get_summary_json},
            {"type": "function", "function": get_generic_json}
        ]

    def _createAssistant(self, instruction):
        print("Creating assistant from BaseAssistant._createAssistant\n")
        assistant = self.client.beta.assistants.create(
            name = self.name,
            instructions = instruction,
            tools = self.tools,
            model = self.model
        )
        print("from baseAssistant._createAssistant: This is the assistantID: ", assistant.id, "\n")
        return assistant.id

    def _createThread(self):
        thread = self.client.beta.threads.create()
        return thread.id

    def _addMessageToThread(self, threadId, userMessage):
        message = self.client.beta.threads.messages.create(
            thread_id = threadId,
            role="user",
            content = userMessage
        )
        print("from baseAssistant._addMessageToThread: This is the message: ", message, "\n")
        return threadId

    def _triggerAssistant(self, threadId, assistantId):
        run = self.client.beta.threads.runs.create(
            thread_id = threadId,
            assistant_id = assistantId
        )
        print("from baseAssistant._triggerAssistant: This is the run: ", run, "\n")
        return run

    def _submitToolOutputs(self, threadId, runId, toolCallId, responses):
        print("Submitting tool outputs\n")
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

    def _waitForRun(self, threadId, run, timeout=300):
        # Returns the run object when its status is not queued or in_progress
        
        print("Waiting for run\n")
        start_time = time.time()
        print("From baseAssistant._waitForRun: This is the run before waiting: ", run, "\n")
        while run.status == "queued" or run.status == "in_progress":
            # Check for timeout
            if time.time() - start_time > timeout:
                raise TimeoutError(f"From baseAssistant._waitForRun: Run timed out after {timeout} seconds")
            
            time.sleep(1)
            
            run = self.client.beta.threads.runs.retrieve(
                thread_id = threadId,
                run_id = run.id
            )
            print("From baseAssistant._waitForRun: This is the run after retrieving: ", run, "\n")
        print("From baseAssistant._waitForRun: Run after waiting: ", run, "\n")
        
        return run

    def _getAssistantResponse(self, threadId):
        # NOTE: When the assitant responds with the user message, the assistant_id
        # in the message object is None.
        messages = self.client.beta.threads.messages.list(
            thread_id = threadId
        )
        print("from baseAssistant._getAssistantResponse: This is the messages: ", messages, "\n")
        response = messages.data[0].content[0].text.value
        return response
    
    def _listAssistants(self):
        assistant_object = self.client.beta.assistants.list()
        return assistant_object
    
    def _deleteAssistant(self, assistant_id):
        """Delete an assistant by ID."""
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",  
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
