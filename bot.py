# Imports
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import google.generativeai as palm
from pymongo import MongoClient
import json
from documents import DocumentsHandler
from bson import ObjectId

# Creating a path to PaLM
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
palm.configure(api_key=os.environ['palm_key'])

# Creating a class to use PaLM
class palmChat():
    def __init__(self, user_id, status, temp, user_input=''):
        self.user_id = user_id
        self.status = status
        self.temp = temp
        self.user_input = user_input
        self.examples = [
            ('hi', 'Hi, how may I help you?'),
            ('hey', 'Hi, how can I assist you?')
        ]
        self.response = self.palm_response()

    def palm_response(self):
        if self.user_input == 'create a new catalog':
            output = 'A new catalog has been created.'
            self.update_catalogs()  # Update catalogs and create a new conversation
            return output
        else:
            response = palm.chat(
                context='Informative Assistant',
                examples=self.examples,
                messages=self.user_input,
                temperature=self.temp
            )
            output = response.candidates[0]['content']
            return output

    def update_conversations(self):
        document = DocumentsHandler.get_document_by_user(self.user_id)
        if document is not None:
            document['catalogs'][-1]['conversation'].append({'user': self.user_input, 'bot': self.response})
            DocumentsHandler.update_document(self.user_id, document)
        else:
            print(f"User with user_id '{self.user_id}' not found in the database.")

    def update_catalogs(self):
        document = DocumentsHandler.get_document_by_user(self.user_id)
        if document is not None:
            document['catalogs'].append({'conversation': []})
            DocumentsHandler.update_document(self.user_id, document)
        else:
            print(f"User with user_id '{self.user_id}' not found in the database.")

    def __str__(self):
        return self.response

# Serialization JSON data
def convert_objectid_to_string(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, list):
        return [convert_objectid_to_string(item) for item in obj]
    elif isinstance(obj, dict):
        return {convert_objectid_to_string(key): convert_objectid_to_string(value) for key, value in obj.items()}
    return obj

# Interacting with PaLM through the terminal
if __name__ == '__main__':
    user_id = 'DE8U783K0MCV3'
    temperature = 0.7
    status = True

    if status == False:
        print('The bot is set False.\nPaLM will not be triggered upon a False status.\nSet status to True to continue.')

    while status is True:
        document = DocumentsHandler.get_document_by_user(user_id)

        if not DocumentsHandler.check_user_id_exists(user_id):
            new_document = {
                'user_id': user_id,
                'catalogs': [{'conversation': []}]
            }
            new_user_doc = DocumentsHandler.create_document(new_document)
            document = DocumentsHandler.get_document_by_user(user_id)

        user_input = input('Prompt: ')
        if user_input == 'quit':
            break

        chat = palmChat(user_id, status, temperature, user_input)
        chat.update_conversations()
        print(chat)
        
    chat.update_catalogs()
