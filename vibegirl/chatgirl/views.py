from django.http import JsonResponse
from google import genai
import os
from dotenv import load_dotenv
from django.shortcuts import render

def home(request):
    return render(request, 'chatgirl/index.html')

# Load the API key from the environment
load_dotenv()
api_key = os.getenv("GENAI_API_KEY")

# Initialize the Gemini client
client = genai.Client(api_key=api_key)

def get_response(request):
    user_input = request.GET.get("msg", "")  # Get user input
    prompt = f"You are a sweet, flirty girl. Respond in a flirty but friendly way to: {user_input}"

    try:
        # Generate response from Gemini model
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # Ensure the correct model is used
            contents=prompt
        )

        generated_text = response.text.strip()  # Get the response text
        return JsonResponse({"response": generated_text})

    except Exception as e:
        return JsonResponse({"response": f"❌ Error: {str(e)}"})
