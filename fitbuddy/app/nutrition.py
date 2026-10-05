"""Optional nutrition-specific helpers (reserved for future logic)."""
from app.gemini_flash_generator import generate_nutrition_tip_with_flash

VALID_GOALS = ("weight loss", "muscle gain", "general fitness")


def get_tip(goal: str) -> str:
    return generate_nutrition_tip_with_flash(goal)
