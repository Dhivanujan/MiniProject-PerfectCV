"""
Test script to demonstrate the new interactive, conversational chatbot behavior.

Run this after restarting the backend to see the difference.
"""

import os
from dotenv import load_dotenv
load_dotenv()

try:
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    
    # Simulate a conversation with CV context
    cv_excerpt = """
    John Doe
    Software Engineer
    5 years experience in Python, JavaScript, React
    
    Experience:
    - Backend Developer at Tech Corp (2020-2023)
    - Junior Developer at StartupXYZ (2018-2020)
    
    Skills: Python, React, Node.js, MongoDB
    """
    
    # System message (like the bot will use)
    system_message = f"""You are Alex, a friendly CV coach having a casual conversation.

**Your personality:**
- Keep responses SHORT (2-4 sentences max)
- Natural and conversational (like texting a friend)
- Reference previous messages naturally
- Ask follow-up questions

**User's CV:**
{cv_excerpt}

**Guidelines:**
- Give concise, actionable advice
- Use casual language
- Reference their actual CV content
- Keep it conversational"""

    # Simulate conversation
    conversation = []
    
    questions = [
        "how is my cv",
        "what about my experience section?",
        "how can i improve it?",
        "what skills should i add?"
    ]
    
    print("=" * 60)
    print("CONVERSATIONAL CHATBOT DEMO")
    print("=" * 60)
    print()
    
    for question in questions:
        print(f"👤 USER: {question}")
        print()
        
        # Build messages
        messages = [{"role": "system", "content": system_message}]
        messages.extend(conversation)
        messages.append({"role": "user", "content": question})
        
        # Get response
        response = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=300
        )
        
        answer = response.choices[0].message.content.strip()
        
        print(f"🤖 ALEX: {answer}")
        print()
        print("-" * 60)
        print()
        
        # Add to conversation history
        conversation.append({"role": "user", "content": question})
        conversation.append({"role": "assistant", "content": answer})
    
    print("=" * 60)
    print("Notice how:")
    print("1. Responses are SHORT (2-4 sentences)")
    print("2. Bot remembers context ('it' refers to experience)")
    print("3. Natural, conversational tone")
    print("4. Follow-up questions work naturally")
    print("=" * 60)

except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure:")
    print("1. Groq is installed: pip install groq")
    print("2. GROQ_API_KEY is set in .env")
