## Setting up Google Cloud Credentials

1. Obtain a service account key:
   - Go to the Google Cloud Console (https://console.cloud.google.com/)
   - Navigate to "IAM & Admin" > "Service Accounts"
   - Create a new service account or select an existing one
   - Go to the "Keys" tab and click "Add Key" > "Create new key"
   - Choose JSON as the key type and click "Create"
   - Save the downloaded JSON file

2. In your project root, create a `.env` file:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/downloaded-key.json
   ```
   Replace `path/to/your/downloaded-key.json` with the actual path to your key file.

3. Add `.env` to your `.gitignore`:
   ```
   .env
   ```

4. Install the requirement:
   ```
   pip install -r requirement.txt
   ```

5. In your Python code, use:
   ```python
   import os
   from dotenv import load_dotenv
   from google.oauth2 import service_account

   load_dotenv()  # Load environment variables from .env file

   credentials = service_account.Credentials.from_service_account_file(
       os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
   )
   ```

Never commit or share your service account key. The `.env` file helps keep your credentials secure and separate from your code.