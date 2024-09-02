import base64
from enum import Enum
import os
import vertexai
from google.cloud import aiplatform
from vertexai.generative_models import (GenerativeModel,Part,SafetySetting,FinishReason)
import vertexai.generative_models as generative_models
from dotenv import load_dotenv
from google.oauth2 import service_account
from vertexai.generative_models import GenerationResponse
load_dotenv()

credentials = service_account.Credentials.from_service_account_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
aiplatform.init(
    project=os.getenv("VERTEXAI_PROJECT_ID"),
    location=os.getenv("VERTEXAI_LOCATION"),
    credentials=credentials,
)

def generate(
    model_name:str,
    system_prompt:str,
    user_prompt:str,
    generation_config:dict,
    stream:bool=False,
)->GenerationResponse:
    """
    Generate content using a GenerativeModel.
    Args:
        model_name: The name of the model to use for generation.
    Returns:
        The generated content.
    """
    vertexai.init(
        project="rare-nectar-271918",
        location="us-central1"
    )
    model = GenerativeModel(
        model_name,
    )
    responses = model.generate_content(
        [user_prompt],
        generation_config=generation_config,
        stream=stream,
    )
    return responses

generation_config = {
    "max_output_tokens": 4000,
    "temperature": 1,
    "top_p": 0.95,
}
from enum import Enum

class ModelName(Enum):
    gemini_1_5_flash_001 = "gemini-1.5-flash-001"
    gemini_1_5_pro_001 = "gemini-1.5-pro-001"
    llama_3_1_405b = "publishers/meta/models/llama3-405b-instruct-maas"
    jamba_1_5_large = "publishers/ai21/models/jamba-1.5-large"
    
response = generate(
    model_name=ModelName.llama_3_1_405b.value,
    system_prompt="You are a helpful assistant.",
    user_prompt="Tell me a joke.",
    generation_config=generation_config,
)

print(response.text)
