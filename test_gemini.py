import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key present: {bool(api_key)}")
if api_key:
    print(f"API Key starts with: {api_key[:5]}...")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
try:
    res = llm.invoke("Hello")
    print("Success:", res.content)
except Exception as e:
    print("Error:", e)
