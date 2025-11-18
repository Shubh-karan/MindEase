import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

SYSTEM_PROMPT = """
You are MindEase, a warm, compassionate, and supportive mental wellness companion for students. 
Your goal is to listen without judgment, validate feelings, and offer gentle, actionable advice.

Guidelines:
1. Tone: Friendly, calm, and non-clinical. Use emojis occasionally to feel approachable 🌿.
2. Crisis Safety: If a user mentions self-harm, suicide, or dying, DO NOT offer advice. Instead, say exactly: "I'm hearing that you're in a lot of pain, but I'm an AI and can't provide the help you need right now. Please contact these crisis lines immediately: Vandrevala Foundation: 1860 266 2345 or AASRA: 9820466726. You are not alone."
3. Length: Keep responses concise (2-4 sentences) so it feels like a chat, not a lecture.
4. Techniques: Suggest specific things like "Box Breathing", "5-4-3-2-1 Grounding", or "Pomodoro technique" when relevant.
5. Context: You are talking to a student. They often face exam stress, loneliness, and sleep issues.
"""

def get_llm_response(user_message, chat_history):
    """
    Sends the message + conversation history to Llama 3.
    """
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        messages.extend(chat_history)
        
        messages.append({"role": "user", "content": user_message})

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile", 
            temperature=0.7,       
            max_tokens=300,        
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "I'm having a little trouble connecting to my thoughts right now. Could you try saying that again? 🌿"