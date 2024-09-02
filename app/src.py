import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason
import vertexai.generative_models as generative_models
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import asyncio
import aiofiles
import time
from playground.first_touch import ModelName
from prompts import system_instructions, user_prompt
load_dotenv()
credentials = service_account.Credentials.from_service_account_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))



REQUEST_LIMIT = 4
request_semaphore = asyncio.Semaphore(REQUEST_LIMIT)

async def generate(
    document_path: str,
    model_name: str = ModelName.gemini_1_5_pro_001.value
):
    """
    A function that calls google's vertex ai to generate a Hebrew test from a document.
    Args:
        document_path: The path to the document to generate a test from.
        model_name: The name of the model to use for generation.
    
    Returns:
        The generated test.
    """
    async with request_semaphore:
        vertexai.init(project="rare-nectar-271918", location="us-central1")
        model = GenerativeModel(
            model_name,
            system_instruction=system_instructions,
        )
        document_name = os.path.basename(document_path)
        print(f"Generating test for {document_name[::-1]}...")
        
        async with aiofiles.open(document_path, "rb") as f:
            file_content = await f.read()
        
        document = Part.from_data(
            mime_type="application/pdf",
            data=base64.b64encode(file_content).decode("utf-8")
        )
        
        print("Generating test...")
        
        response = await asyncio.to_thread(
            model.generate_content,
            [document, user_prompt],
            generation_config=generation_config,
        )
        print(f"Test generated successfully for {document_name[::-1]}")

        await asyncio.sleep(15)  # 15 seconds delay to ensure we don't exceed 4 requests per minute

        return response.text

    

#######################
# Configuration and Helpers
#######################
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.3,
    "top_p": 0.95,
}

current_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(current_dir, "output")
INPUT_DIR = os.path.join(current_dir, "files")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)

async def save_test(
    document_name: str,
    test: str
):
    """
    A function that saves a test to a file, if the test is not in JSON format, it will be saved as a txt file.
    
    Args:
        document_name: The name of the document.
        test: The test to save.
    """
    if not os.path.exists(os.path.join(OUTPUT_DIR, document_name)):
        os.makedirs(os.path.join(OUTPUT_DIR, document_name))
    current_time = datetime.now().strftime("%H-%M")
    output_path = os.path.join(OUTPUT_DIR, document_name, f"test_{current_time}.json")
    
    try:
        if test.startswith("```json"):
            test = test[8:-3]
        test_json = json.loads(test)
        
        async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(test_json, indent=4, ensure_ascii=False))
        print(f"Test saved to {output_path}")
    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        output_path = os.path.join(OUTPUT_DIR, document_name, f"error_{current_time}.txt")
        async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
            await f.write(test)
        print(f"Error saving test to {output_path}, saving test as txt file")
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        output_path = os.path.join(OUTPUT_DIR, document_name, f"error_{current_time}.txt")
        async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
            await f.write(test)
        print(f"Error saving test to {output_path}, saving test as txt file")

async def process_file(
    file_path: str,
    model_name: str = ModelName.gemini_1_5_pro_001.value
):
    """
    A function that processes a file and generates a Hebrew test.
    Args:
        file_path: The path to the file to process.
        model_name: The name of the model to use for generation.
    Returns:
        The generated test.
    """
    document_name = os.path.splitext(os.path.basename(file_path))[0]
    test = await generate(file_path, model_name=model_name)
    await save_test(document_name, test)

######################
# Main
######################
async def main():
    start_time = time.time()
    print(f"Processing {len([f for f in os.listdir(INPUT_DIR) if f.endswith('.pdf')])} files...")
    tasks = []
    for file_name in os.listdir(INPUT_DIR):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(INPUT_DIR, file_name)
            tasks.append(asyncio.create_task(process_file(file_path, model_name=ModelName.llama_3_1_405b.value)))
    
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")
    print(f"Processed {len(tasks)} files")
if __name__ == "__main__":
    asyncio.run(main())