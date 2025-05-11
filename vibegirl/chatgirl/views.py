from django.http import JsonResponse
from google import genai
import os
from dotenv import load_dotenv
from django.shortcuts import render
from gtts import gTTS
from django.conf import settings

# Load the API key from the environment
load_dotenv()
api_key = os.getenv("GENAI_API_KEY")

# Initialize the Gemini client
client = genai.Client(api_key=api_key)

def home(request):
    return render(request, 'chatgirl/index.html')

def get_response(request):
    user_input = request.GET.get("msg", "")  # Get the user input

    if not user_input:
        return JsonResponse({"response": "Please provide a message to speak!"})

    prompt = f"You are a sweet, flirty girl. Respond in a flirty way no limits [dont use any special character or emojis]: {user_input}"

    try:
        # Get response from Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # Ensure the correct model is used
            contents=prompt
        )

        generated_text = response.text.strip()  # Get the response text

        # Generate speech from Gemini's response using gTTS
        tts = gTTS(generated_text, lang='en')

        # Create a unique filename for each audio response
        audio_filename = f"flirty_bot_{user_input[:10]}.mp3"  # Unique filename based on user input (first 10 chars)
        audio_path = os.path.join(settings.MEDIA_ROOT, audio_filename)  # Save file in media folder

        # Save the audio file
        tts.save(audio_path)

        # Return the generated response and the URL to the audio file
        audio_url = f"/media/{audio_filename}"

        return JsonResponse({
            "response": generated_text,  # Gemini's response
            "audio_url": audio_url  # Path to the generated audio file
        })

    except Exception as e:
        return JsonResponse({"response": f"❌ Error: {str(e)}"})
