import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY")
    print(f"GROQ_API_KEY found: {api_key[:20]}..." if api_key else "GROQ_API_KEY not found")
    
    if api_key:
        client = Groq(api_key=api_key)
        
        print("\nTesting Groq API with llama-3.3-70b-versatile...")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Analyze this CV excerpt: 'Software Engineer with 5 years of experience in Python and React.' What's missing?",
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=200,
        )
        
        response = chat_completion.choices[0].message.content.strip()
        print(f"\n✓ Success! Groq response:\n{response}")
    else:
        print("\n✗ Error: GROQ_API_KEY not found in environment")
        
except ImportError:
    print("✗ Error: Groq library not installed. Run: pip install groq")
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {str(e)}")
