"""All routes: HTML pages + JSON API endpoints."""
import os

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.database import (
    delete_user, get_all_plans, get_all_users,
    get_current_plan, get_original_plan, get_user, save_plan, save_user, update_plan,
)
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.gemini_generator import generate_workout_gemini
from app.schemas import FeedbackRequest, UserInput, WorkoutRequest
from app.updated_plan import update_workout_plan

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def render(request: Request, name: str, context: dict, status_code: int = 200):
    return templates.TemplateResponse(request, name, context, status_code=status_code)


def result_context(user, plan, tip, **extra):
    return {
        "username": user.name, "user_id": user.id, "age": user.age, "weight": user.weight,
        "goal": user.goal, "intensity": user.intensity.capitalize(),
        "workout_plan": plan, "nutrition_tip": tip, **extra,
    }


# ------------------------------------------------------------------ Web pages
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render(request, "index.html", {"error": None})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: int = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    try:
        data = UserInput(username=username.strip(), user_id=user_id, age=age, weight=weight,
                         goal=goal.strip(), intensity=intensity.lower())
    except ValidationError as e:
        msg = "; ".join(f"{err['loc'][-1]}: {err['msg']}" for err in e.errors())
        return render(request, "index.html", {"error": msg}, status_code=422)

    try:
        plan = generate_workout_gemini({"goal": data.goal, "intensity": data.intensity,
                                        "age": data.age, "weight": data.weight})
        tip = generate_nutrition_tip_with_flash(data.goal)
    except RuntimeError as e:
        return render(request, "index.html", {"error": str(e)}, status_code=502)

    save_user(data.user_id, data.username, data.age, data.weight, data.goal, data.intensity)
    save_plan(data.user_id, plan)

    user = get_user(data.user_id)
    return render(request, "result.html", result_context(user, plan, tip))


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(request: Request, user_id: int = Form(...), feedback: str = Form(...)):
    user = get_user(user_id)
    original = get_original_plan(user_id)
    if not user or not original:
        return render(request, "index.html",
                      {"error": f"No plan found for user ID {user_id}. Generate a plan first."},
                      status_code=404)

    # Iterate on the latest version so several rounds of feedback stack up.
    current = get_current_plan(user_id) or original
    try:
        updated = update_workout_plan(current, feedback.strip())
        tip = generate_nutrition_tip_with_flash(user.goal)
    except RuntimeError as e:
        return render(request, "result.html",
                      result_context(user, current, None, error=str(e)), status_code=502)

    update_plan(user_id, updated)
    return render(request, "result.html",
                  result_context(user, updated, tip,
                                 success="Your plan has been updated based on your feedback!"))


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    users = get_all_users()
    plans = {p.user_id: p for p in get_all_plans()}
    user_data = []
    for u in users:
        p = plans.get(u.id)
        user_data.append({
            "id": u.id, "name": u.name, "age": u.age, "weight": u.weight,
            "goal": u.goal, "intensity": u.intensity,
            "original_plan": p.original_plan if p else "N/A",
            "updated_plan": p.updated_plan if p and p.updated_plan else "Not updated",
        })
    return render(request, "all_users.html", {"users": user_data})


@router.post("/delete-user/{user_id}")
def delete_user_route(user_id: int):
    delete_user(user_id)
    return RedirectResponse("/view-all-users", status_code=303)


# ------------------------------------------------------------------ JSON API
@router.post("/generate-workout/gemini")
async def api_generate_workout(request: WorkoutRequest):
    try:
        result = generate_workout_gemini({"goal": request.goal, "intensity": request.intensity})
        return {"model": "gemini-pro", "workout_plan": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nutrition-tip")
def api_nutrition_tip(goal: str):
    try:
        return {"goal": goal, "nutrition_tip": generate_nutrition_tip_with_flash(goal)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-plan")
def api_generate_plan(user_data: UserInput):
    try:
        plan = generate_workout_gemini({"goal": user_data.goal, "intensity": user_data.intensity,
                                        "age": user_data.age, "weight": user_data.weight})
        save_user(user_data.user_id, user_data.username, user_data.age, user_data.weight,
                  user_data.goal, user_data.intensity)
        save_plan(user_data.user_id, plan)
        return {"message": "Workout plan generated and saved successfully!", "workout_plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {e}")


@router.post("/update-plan/{user_id}", response_model=dict)
def api_update_plan(user_id: int, data: FeedbackRequest):
    current = get_current_plan(user_id)
    if not current:
        raise HTTPException(status_code=404, detail="Original plan not found for this user.")
    try:
        updated = update_workout_plan(current, data.feedback)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    update_plan(user_id, updated)
    return {"updated_plan": updated}
