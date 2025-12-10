import os
from groq import Groq
from dotenv import load_dotenv
import random

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_path, '.env')
load_dotenv(env_path)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

BASE_SYSTEM_PROMPT = """
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

def get_llm_response(user_message, chat_history, language="English"):
    try:
        language_instruction = f"\n\nIMPORTANT INSTRUCTION: You MUST reply in the {language} language/script only. Do not reply in English if {language} is not English."
        
        full_system_prompt = BASE_SYSTEM_PROMPT + language_instruction

        messages = [{"role": "system", "content": full_system_prompt}]
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

def transcribe_audio(audio_file):
    try:
        transcription = client.audio.transcriptions.create(
            file=(audio_file.filename, audio_file.read()),
            model="whisper-large-v3",
            response_format="text",
        )
        return transcription
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

def generate_daily_gift():
    """Generates a random positive affirmation or micro-challenge."""
    type_choice = random.choice(["affirmation", "challenge"])
    
    prompt = ""
    if type_choice == "affirmation":
        prompt = "Generate a short, powerful, and unique positive affirmation for a student who might be stressed. Max 1 sentence. Use an emoji."
    else:
        prompt = "Generate a very small, easy mental health micro-challenge (e.g., drink water, stretch, look out a window) for a student. Max 1 sentence. Use an emoji."

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.9, # High creativity
            max_tokens=50,
        )
        return chat_completion.choices[0].message.content
    except:
        return "Take a deep breath and smile. You are doing great! 🌟"