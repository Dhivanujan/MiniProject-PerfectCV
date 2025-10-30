import google.generativeai as genai
from config.config import Config

def setup_gemini():
    genai.configure(api_key=Config.API_KEY)
    
def get_valid_model():
    for m in genai.list_models():
        name = getattr(m, "name", None)
        methods = getattr(m, "supported_generation_methods", [])
        if methods and "generateContent" in methods:
            return name
    raise RuntimeError("No valid model found that supports generateContent!")

MODEL_NAME = get_valid_model()