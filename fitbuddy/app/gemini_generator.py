"""Gemini Pro - 7-day workout plan generator."""
import os

from google import genai
from dotenv import load_dotenv

load_dotenv()
_client = None

PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")


def generate_text(model_name: str, prompt: str) -> str:
    """Single place that talks to Gemini (shared by all generators)."""
    global _client
    if _client is None:
        key = os.getenv("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError("GOOGLE_API_KEY is not set. Add it to your .env file.")
        _client = genai.Client(api_key=key)
    response = _client.models.generate_content(model=model_name, contents=prompt)
    return response.text


def generate_workout_gemini(user_input: dict) -> str:
    """Return a structured 7-day plan. Raises RuntimeError if the API call fails."""
    extra = ""
    if user_input.get("age"):
        extra += f"\nThe person is {user_input['age']} years old"
        if user_input.get("weight"):
            extra += f" and weighs {user_input['weight']} kg"
        extra += ". Keep the plan safe and appropriate for them."

    prompt = f"""
You are a professional fitness trainer.

Create a personalized, structured 7-day workout plan for someone with the goal of **{user_input['goal']}**, and who prefers **{user_input['intensity']}** intensity workouts.{extra}

Each day must include:
- A warm-up (5-10 mins)
- Main workout (targeted exercises, sets & reps)
- Cooldown or recovery tip

Format:
Day 1:
Warm-up: ...
Main Workout: ...
Cooldown: ...
(Repeat for Day 2-7)
"""
    try:
        return generate_text(PRO_MODEL, prompt)
    except Exception as e:
        raise RuntimeError(f"Could not generate workout plan: {e}") from e
