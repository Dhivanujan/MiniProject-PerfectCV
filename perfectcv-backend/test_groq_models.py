import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if api_key:
        client = Groq(api_key=api_key)
        
        # Try different models
        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        
        for model in models_to_try:
            try:
                print(f"\nTrying {model}...")
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": "Say hello in one sentence.",
                        }
                    ],
                    model=model,
                    temperature=0.7,
                    max_tokens=50,
                )
                
                response = chat_completion.choices[0].message.content.strip()
                print(f"✓ {model} works! Response: {response}")
                break
            except Exception as e:
                print(f"✗ {model} failed: {str(e)[:100]}")
    else:
        print("Error: GROQ_API_KEY not found")
        
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
