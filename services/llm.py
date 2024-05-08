from typing import Dict
import ast
import json
import os
import requests
from services.database import build_dbml_schema
from services import strings

def yandex_gpt_query(user_query:str, system_text:str='Ты AI-помощник') -> Dict:
    """
    Sends a user query to YandexGPT via Yandex Cloud API using an API key. 
    Returns a structured response including the model's answer or an error message.

    Parameters
    ----------
    user_query : str
        The user's query in natural language.

    Returns
    -------
    dict
        A dictionary with the processing status, the model's answer, 
        and an error description if applicable.
    """
    API_KEY = os.getenv("YANDEX_API_KEY")
    FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
    model_uri = f"gpt://{FOLDER_ID}/yandexgpt/latest"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "x-folder-id": FOLDER_ID,
            }
    data = {
    "modelUri": model_uri,
    "completionOptions": {
        "stream": False,
        "temperature": 0.7,
        "maxTokens": 2000,
    },
    "messages": [
            {
            "role": "system",
            "text": system_text,
            },
            {
            "role": "user",
            "text": user_query,
            },
        ],
    }
    response = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        headers=headers,
        data=json.dumps(data),
        timeout=30
        )
    res = json.loads(response.text)
    if response.status_code == 200:
        return {'status':'success',
                'answer': res['result']['alternatives'][0]['message']['text'],
                'error': ''}
    return {'status':'failure',
            'answer': '',
            'error': response.text}

def generate_prompt(user_query, schema_data):
    """
    Generates a prompt for LLM, including the database schema and the user query.
    
    Parameters
    ----------
    user_query : str
        The user's query in natural language.
    schema_data : str
        The database schema in DBML format.

    Returns
    -------
    Tuple[str,str]: system prompt and prompt
    """
    system_prompt = strings['system_prompt'].format(schema_data=schema_data)
    
    prompt = strings['user_query'].format(user_question=user_query)

    return system_prompt, prompt
 
def natural_language_to_sql(user_query, schema_data=strings['dbml_schema']):
    """
    Converts a user query from natural language into an SQL query using LLM.

    Parameters
    ----------
    user_query : str
        The user's query in natural language.
    schema_data : str
        The database schema in DBML format.

    Returns
    -------
    dict
        A dictionary with the processing result, including the SQL query or an error description if applicable.
    """
    system_prompt, prompt = generate_prompt(user_query, schema_data)
    answer = yandex_gpt_query(system_text=system_prompt, user_query=prompt)
    if answer['answer']:
        to_return=ast.literal_eval(answer['answer'].replace('`', '').replace('\n', ' ').replace('json', ' '))
        to_return['status'] = 'success'
        to_return['raw_response'] = answer['answer']
        return to_return
    return {'status':'failure', 
            'sql':'', 
            'error_description':'Failed to parse model response',
            'raw_response':answer['answer']}
