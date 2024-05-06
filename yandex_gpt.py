import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

def yandex_gpt_query(user_query):
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
        "Authorization": f"Api-Key {API_KEY}",
        "x-folder-id": FOLDER_ID,
            }
    data = {
    "modelUri": model_uri,
    "completionOptions": {
        "stream": False,
        "temperature": 0.3,
        "maxTokens": 2000,
    },
    "messages": [
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
