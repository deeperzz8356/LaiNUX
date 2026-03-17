import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path="f:/LaiNUX/agentic_os/.env")
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

try:
    models = genai.list_models()
    print("Available models:")
    for model in models:
        print(f" - {model.name}")
except Exception as e:
    print(f"Error: {e}")
