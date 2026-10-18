import json
import os
import traceback
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
print("KEY ENDS WITH:", (os.getenv("GEMINI_API_KEY") or "MISSING")[-4:])

SYSTEM_PROMPT = (
    "You are a friendly Class Assistant for students. "
    "Explain things simply, use short numbered points, and give examples."
)

def index(request):
    return render(request, "assistant/index.html")

@require_POST
def chat(request):
    try:
        prompt = json.loads(request.body).get("prompt", "").strip()
        if not prompt:
            return JsonResponse({"error": "Please enter a question."}, status=400)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        return JsonResponse({"reply": response.text})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Error: {e}"}, status=500)

def manifest(request):
    return render(request, "assistant/manifest.json",
                  content_type="application/manifest+json")

def serviceworker(request):
    response = render(request, "assistant/serviceworker.js",
                      content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    return response