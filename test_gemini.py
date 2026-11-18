'''import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(override=True)

model_name = os.getenv("GEMINI_MODEL")

print("Testing model:", model_name)

llm = ChatGoogleGenerativeAI(
    model=model_name,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    max_retries=2,
    timeout=60,
)

try:
    response = llm.invoke("Say Hello in Telugu.")

    print("\nSUCCESS!")
    print(response.content)

except Exception as e:
    print("\nFAILED!")
    print(type(e).__name__)
    print(e)'''
from agent import get_llm

try:
    response = get_llm().invoke("Say Hello!")
    print("SUCCESS!")
    print(response.content)

except Exception as e:
    print("FAILED!")
    print(e)