
import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

print("Step 1: Loading environment...", flush=True)

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key or api_key == "your_gemini_api_key":
    raise ValueError("Gemini API key is missing or invalid.")

print("Step 2: API key found.", flush=True)

print("Step 3: Initializing Gemini...", flush=True)

llm = ChatGoogleGenerativeAI(
    # model="gemini-3.8-flash",
    model="gemini-3.5-flash-lite",
    temperature=0.2,
    google_api_key=api_key,
)

print("Step 4: Sending request to Gemini...", flush=True)

start = time.time()

response = llm.invoke(
    "Explain RAG in two sentences."
)

print("Step 5: Response received!", flush=True)
print(response.content)

print(f"Time taken: {time.time() - start:.2f} seconds")
