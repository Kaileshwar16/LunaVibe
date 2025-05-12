from django.http import JsonResponse
from google import genai
import os
from dotenv import load_dotenv
from django.shortcuts import render
from gtts import gTTS
from django.conf import settings
from .models import ChatHistory
from difflib import get_close_matches

# Load the API key from the environment
load_dotenv()
api_key = os.getenv("GENAI_API_KEY")

# Initialize the Gemini client
client = genai.Client(api_key=api_key)

def home(request):
    return render(request, 'chatgirl/index.html')

def get_response(request):
    user_input = request.GET.get("msg", "").strip()

    if not user_input:
        return JsonResponse({"response": "Please provide a message to speak!"})

    # Check if a similar message already exists
    past_inputs = ChatHistory.objects.values_list('user_input', flat=True)
    matches = get_close_matches(user_input, past_inputs, n=1, cutoff=0.8)

    if matches:
        matched_input = matches[0]
        matched_response = ChatHistory.objects.get(user_input=matched_input).bot_response

        return JsonResponse({
            "response": matched_response,
            "audio_url": ""  # Optional: Load pre-saved audio if you want
        })

    # New logic for detecting user-specific info (e.g., name, age)
    user_name = ""
    user_age = None

    if "my name is" in user_input.lower():
        user_name = user_input.split("my name is")[-1].strip()
        ChatHistory.objects.create(user_input=user_input, bot_response=f"Got it, your name is {user_name}!")
        
    elif "i am" in user_input.lower() and "years old" in user_input.lower():
        user_age = [int(s) for s in user_input.split() if s.isdigit()][0]
        ChatHistory.objects.create(user_input=user_input, bot_response=f"Got it, you are {user_age} years old!")

    # Prepare the bot response considering user details
    if user_name:
        prompt = f"You are a sweet, flirty girl. Respond in a flirty way no limits. The user's name is {user_name}. [dont use any special character or emojis]: {user_input}"
    elif user_age:
        prompt = f"You are a sweet, flirty girl. Respond in a flirty way no limits. The user is {user_age} years old. [dont use any special character or emojis]: {user_input}"
    else:
        prompt = f"You are a sweet, flirty girl. Respond in a flirty way no limits [dont use any special character or emojis]: {user_input}"

    try:
        # Get response from Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        generated_text = response.text.strip()

        # Save chat to DB
        ChatHistory.objects.create(user_input=user_input, bot_response=generated_text)

        # Generate audio
        tts = gTTS(generated_text, lang='en')
        audio_filename = f"flirty_bot_{user_input[:10]}.mp3"
        audio_path = os.path.join(settings.MEDIA_ROOT, audio_filename)
        tts.save(audio_path)
        audio_url = f"/media/{audio_filename}"

        return JsonResponse({
            "response": generated_text,
            "audio_url": audio_url
        })

    except Exception as e:
        return JsonResponse({"response": f"❌ Error: {str(e)}"})
