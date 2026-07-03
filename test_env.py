from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
print(os.getenv("GCP_PROJECT_ID"))