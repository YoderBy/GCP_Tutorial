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

START_PAGE_MAPPING = {
    1: 0,
    2: 15,
    3: 26,
    4: 51,
    5: 83,
    6: 97,
    7: 113
}

REQUEST_LIMIT = 4
request_semaphore = asyncio.Semaphore(REQUEST_LIMIT)

async def generate(
    document_path: str,
    model_name: str = ModelName.gemini_1_5_pro_001.value,
    existing_content: str = None
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
        user_message = user_prompt
        if existing_content:
            user_message += f"\n\nThose are the existing questions, do not repeat questions from it:\n{existing_content}. REMEMBER, DO NOT REPEAT QUESTIONS FROM THE EXAMPLES!"
        
        max_retries = 3
        initial_temperature = generation_config["temperature"]
        
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    model.generate_content,
                    [document, user_message],
                    generation_config=generation_config,
                )
                test_content = response.text
                
                # Check if the response is valid JSON
                if test_content.startswith("```json"):
                    test_content = test_content[8:-3]
                json.loads(test_content)  # This will raise JSONDecodeError if not valid JSON
                
                print(f"Test generated successfully for {document_name[::-1]}")
                await asyncio.sleep(15)  # 15 seconds delay to ensure we don't exceed 4 requests per minute
                return test_content
            
            except json.JSONDecodeError:
                if attempt < max_retries - 1:
                    generation_config["temperature"] = min(initial_temperature + 0.1 * (attempt + 1), 1.0)
                    print(f"Retry {attempt + 1} with temperature {generation_config['temperature']}")
                else:
                    print(f"Failed to generate valid JSON after {max_retries} attempts")
                    return test_content  # Return the last generated content even if it's not valid JSON
        
        # Reset temperature for future calls
        generation_config["temperature"] = initial_temperature
        return test_content

#######################
# Configuration and Helpers
#######################
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.5,
    "top_p": 0.9,
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
    # extract the lecture number
    try:
        lecture_number = document_name.split(" ")[1]
    except IndexError:
        lecture_number = ""
    output_path = os.path.join(OUTPUT_DIR, document_name, f"{lecture_number}_test_{current_time}.json")
    
    try:
        if test.startswith("```json"):
            test = test[8:-3]
        test_json = json.loads(test)
        
        async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
            test_json["name"] = lecture_number + "_" + test_json["name"]
            test_json["start_page"] = START_PAGE_MAPPING[int(lecture_number)]
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

async def get_existing_content(document_name):
    document_dir = os.path.join(OUTPUT_DIR, document_name)
    merged_content = {}

    if os.path.exists(document_dir):
        for file_name in os.listdir(document_dir):
            if file_name.endswith(('.json', '.txt')):
                file_path = os.path.join(document_dir, file_name)
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                    
                    if file_name.endswith('.json'):
                        content_json = json.loads(content)
                        if isinstance(content_json, dict):
                            merged_content.update(content_json)
                        elif isinstance(content_json, list):
                            merged_content.setdefault('questions', []).extend(content_json)
                    else:  # .txt file
                        merged_content.setdefault('text_content', []).append(content)
                    
                    print(f"Loaded and merged content from {file_path}")
                except json.JSONDecodeError:
                    print(f"Error parsing JSON from {file_path}")
                except Exception as e:
                    print(f"Error reading file {file_path}: {str(e)}")

    if merged_content:
        print(f"Loaded {len(merged_content)} questions from {document_name}")
    else:
        print(f"No existing content found for {document_name}")
    
    str_content = json.dumps(merged_content, indent=4, ensure_ascii=False)
    return str_content if str_content else None

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
    existing_content = await get_existing_content(document_name)
    test = await generate(file_path, model_name=model_name, existing_content=existing_content)
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
            tasks.append(asyncio.create_task(process_file(file_path, model_name=ModelName.gemini_1_5_pro_001.value)))
    
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")
    print(f"Processed {len(tasks)} files")
if __name__ == "__main__":
    asyncio.run(main())