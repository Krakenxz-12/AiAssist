import json
import os
import traceback
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from google import genai
from google.genai import types
import time
from google.genai import errors

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
        return JsonResponse({"reply": generate_reply(prompt)})
    except errors.APIError as e:
        traceback.print_exc()
        if e.code in (429, 503):
            msg = "The AI is busy right now. Please try again in a moment."
        else:
            msg = "The assistant is unavailable. Try again."
        return JsonResponse({"error": msg}, status=503)
    except Exception:
        traceback.print_exc()
        return JsonResponse({"error": "The assistant is unavailable. Try again."}, status=500)

def manifest(request):
    return render(request, "assistant/manifest.json",
                  content_type="application/manifest+json")

def serviceworker(request):
    response = render(request, "assistant/serviceworker.js",
                      content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    return response

# Tried in order. If one is overloaded or unavailable, the next is used.
MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]   # use the exact IDs shown in AI Studio

def generate_reply(prompt):
    last_error = None
    for model in MODELS:
        for attempt in range(2):
            try:
                response = get_client().models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                return response.text
            except errors.APIError as e:
                last_error = e
                if e.code in (429, 500, 502, 503, 504):
                    time.sleep(2)        # brief pause, then retry
                    continue
                if e.code == 404:        # model not found, so try the next one
                    break
                raise
    raise last_error