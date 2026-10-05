"""Gemini Pro - revise an existing plan from user feedback."""
from app.gemini_generator import PRO_MODEL, generate_text


def update_workout_plan(original_plan: str, user_feedback: str) -> str:
    """Return a revised plan. Raises RuntimeError if the API call fails."""
    prompt = f"""
You are a professional fitness trainer assistant.

Here's the original 7-day workout plan:
{original_plan}

User Feedback:
"{user_feedback}"

Based on the feedback, revise the relevant parts of the workout plan. Keep the format and rest of the plan unchanged if not needed.
Return the full updated 7-day plan.
"""
    try:
        return generate_text(PRO_MODEL, prompt).strip()
    except Exception as e:
        raise RuntimeError(f"Could not update plan: {e}") from e
