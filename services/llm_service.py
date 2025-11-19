import os
from groq import Groq
from dotenv import load_dotenv

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_path, '.env')
load_dotenv(env_path)

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
4. BREATHING TOOL: If the user seems anxious, panicked, or stressed, explicitly say: "Try clicking the 'Relax' button 🌬️ at the top of our chat. It will guide you through a calming breathing exercise."
5. Techniques: Suggest specific things like "5-4-3-2-1 Grounding" or "Pomodoro technique" when relevant.
6. Context: You are talking to a student. They often face exam stress, loneliness, and sleep issues.
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
            model="llama-3.1-8b-instant", 
            temperature=0.7,        
            max_tokens=300,         
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "I'm having a little trouble connecting to my thoughts right now. Could you try saying that again? 🌿"

def generate_zen_story(user_worry):
    """
    Generates a short, calming visualization script based on the specific worry.
    """
    zen_prompt = f"""
    You are a guided meditation expert. The user is stressed about: "{user_worry}".
    Write a SHORT (approx 100 words), soothing, second-person visualization script ("Imagine you are...") to help them relax about this specific topic.
    - Use sensory details (colors, sounds, feelings).
    - Tone: Gentle, slow, hypnotic.
    - Do NOT give advice. Just paint a calming picture.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": zen_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=200,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error generating Zen Story: {e}")
        return "Imagine a calm blue ocean. The waves are gently rolling in and out. Breathe with the waves..."