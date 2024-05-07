from typing import Dict
import time
from dotenv import load_dotenv
import replicate
load_dotenv()

def replicate_query(user_query:str) -> Dict:
    """
    Sends a user query to a pre-defined LLM model via Replicate API 
    using an API token for authentication. Returns a structured response 
    including the model's answer or an error message.

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
    input = {
    "top_k": 50,
    "top_p": 0.9,
    "prompt": user_query,
    "temperature": 0.6,
    "max_new_tokens": 512,
    "prompt_template": "<s>[INST] {prompt} [/INST] "
}
    prediction = replicate.models.predictions.create(
                    "mistralai/mistral-7b-instruct-v0.2",
                    input=input
                        )

    while prediction.status not in {"succeeded", "failed", "canceled"}:
        time.sleep(2)
        prediction.reload()
        if prediction.error:
            return {"status": "failed", 'error': prediction.error, 'answer':''}

    return {"status": "failed", 'error': '', 'answer':''.join(prediction.output)}