"""Gemini Flash - quick nutrition / recovery tips."""
import os

from dotenv import load_dotenv

from app.gemini_generator import generate_text

load_dotenv()

FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")


def generate_nutrition_tip_with_flash(goal: str) -> str:
    """
    Generate a nutrition or recovery tip based on the user's fitness goal.
    Raises RuntimeError if the API call fails.
    """
    prompt = (
        f"Give one clear, helpful nutrition or recovery tip for someone focused on '{goal}'. "
        "The tip should be practical, friendly, and easy to understand. "
        "Keep it under 60 words."
    )
    try:
        return generate_text(FLASH_MODEL, prompt).strip()
    except Exception as e:
        raise RuntimeError(f"Could not generate tip: {e}") from e
