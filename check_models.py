import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

print("Checking available models...\n")

try:
    for model in client.models.list():
        if "generateContent" in (model.supported_actions or []):
            print(model.name)

except Exception as e:
    print("Model listing failed:", e)