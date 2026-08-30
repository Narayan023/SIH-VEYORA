"""
NutriLens AI - FastAPI Application Server
Entrypoint serving the REST API and the modern Single Page Application
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from models import (
    UserProfile,
    DetectedFood,
    MealScanResponse,
    MealAnalysisRequest,
    MealAnalysisResult,
    DailyContextSummary,
    DemoComparisonRequest,
    RecipeItem
)
from database import (
    get_user_profile,
    save_user_profile,
    get_all_foods,
    get_food_by_id,
    save_meal_log,
    get_today_meal_logs,
    clear_today_meals,
    get_all_recipes,
    get_recipe_by_id
)
from context_engine import PersonalContextEngine
from vision_engine import VisionEngine, SAMPLE_MEALS, recalculate_food_nutrition

app = FastAPI(
    title="NutriLens AI",
    description="Personalized Food-to-Fitness Intelligence System - SIH Student Innovation Prototype",
    version="1.0.0"
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo Personas for SIH Judges
DEMO_PERSONAS = [
    {
        "id": "persona_student",
        "name": "Aarav Sharma (College Student)",
        "role": "Hostel Student & Recreational Walker",
        "age": 20,
        "gender": "male",
        "height_cm": 174.0,
        "weight_kg": 65.0,
        "activity_level": "moderate",
        "fitness_objective": "general_fitness",
        "dietary_preference": "vegetarian",
        "avatar": "🎓",
        "bio": "Walks to campus classes daily, studies late, eats hostel mess food, seeks balanced daily energy."
    },
    {
        "id": "persona_athlete",
        "name": "Vikram Rathore (Amateur Athlete)",
        "role": "Track Runner & Football Player",
        "age": 23,
        "gender": "male",
        "height_cm": 178.0,
        "weight_kg": 72.0,
        "activity_level": "high",
        "fitness_objective": "sports_performance",
        "dietary_preference": "non-vegetarian",
        "avatar": "⚡",
        "bio": "2 hours daily sprint and agility drills, needs rapid glycogen replenishment and muscle recovery."
    },
    {
        "id": "persona_gym_beginner",
        "name": "Rohan Gupta (Gym Beginner)",
        "role": "Sedentary Desk Worker / Strength Newbie",
        "age": 24,
        "gender": "male",
        "height_cm": 172.0,
        "weight_kg": 78.0,
        "activity_level": "light",
        "fitness_objective": "improve_strength",
        "dietary_preference": "vegetarian",
        "avatar": "🏋️",
        "bio": "Desk job during the day, just started weightlifting 3x/week, aims to build muscle while avoiding excess fat gain."
    }
]


# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "app": "NutriLens AI",
        "tagline": "Don’t just see your food. Understand what it means for you.",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/profile", response_model=UserProfile)
def get_profile(user_id: str = "default_user"):
    prof = get_user_profile(user_id)
    return UserProfile(**prof)


@app.post("/api/profile", response_model=UserProfile)
def update_profile(profile: UserProfile):
    updated = save_user_profile(profile.model_dump())
    return UserProfile(**updated)


@app.get("/api/foods")
def list_foods():
    return {"foods": get_all_foods()}


@app.get("/api/samples")
def list_samples():
    return {"samples": SAMPLE_MEALS}


@app.get("/api/recipes")
def list_recipes(
    category: Optional[str] = None,
    dietary_type: Optional[str] = None,
    search: Optional[str] = None,
    user_id: Optional[str] = "default_user"
):
    """
    Healthy Food Menu API — Returns curated, nutritious Indian recipes with
    exact ingredient measurements, nutritional breakdowns, and user profile recommendations.
    """
    prof = get_user_profile(user_id) if user_id else None
    fitness_objective = prof.get("fitness_objective") if prof else None

    recipes = get_all_recipes(
        category=category,
        dietary_type=dietary_type,
        search=search,
        fitness_objective=fitness_objective
    )
    return {
        "recipes": recipes,
        "total_count": len(recipes),
        "user_context": {
            "fitness_objective": fitness_objective,
            "dietary_preference": prof.get("dietary_preference") if prof else None
        }
    }


@app.get("/api/recipes/{recipe_id}")
def get_recipe_details(
    recipe_id: str,
    user_id: Optional[str] = "default_user"
):
    """
    Returns full recipe details with exact measurements, ingredient-level nutrition,
    and step-by-step cooking instructions.
    """
    prof = get_user_profile(user_id) if user_id else None
    fitness_objective = prof.get("fitness_objective") if prof else None

    recipe = get_recipe_by_id(recipe_id, fitness_objective=fitness_objective)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found in Healthy Food Menu")
    return {"recipe": recipe}



@app.post("/api/scan")
async def scan_meal(
    sample_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Scans a meal image (uploaded file or curated sample).
    Returns multi-item food detections with confidence ratings.
    """
    boxes = []
    if sample_id:
        sample_meta = VisionEngine.get_sample_by_id(sample_id)
        image_url = sample_meta["image_url"] if sample_meta else "/static/assets/images/thali_meal.jpg"
        detected_items = VisionEngine.scan_sample_meal(sample_id)
        if sample_meta and "detected_items" in sample_meta:
            boxes = [item.get("box") for item in sample_meta["detected_items"] if item.get("box")]
    elif file:
        content = await file.read()
        import base64
        image_url = f"data:{file.content_type};base64,{base64.b64encode(content).decode('utf-8')}"
        detected_items = VisionEngine.scan_image_bytes(content)
        # Generate simulated visual bounding boxes for custom upload
        boxes = [
            {"top": 20, "left": 20, "width": 35, "height": 35, "label": detected_items[0].name if len(detected_items) > 0 else "Main"},
            {"top": 20, "left": 55, "width": 35, "height": 35, "label": detected_items[1].name if len(detected_items) > 1 else "Side"},
            {"top": 55, "left": 30, "width": 40, "height": 35, "label": detected_items[2].name if len(detected_items) > 2 else "Grain"}
        ]
    else:
        sample_meta = VisionEngine.get_sample_by_id("north_indian_thali")
        image_url = sample_meta["image_url"] if sample_meta else "/static/assets/images/thali_meal.jpg"
        detected_items = VisionEngine.scan_sample_meal("north_indian_thali")
        boxes = [item.get("box") for item in sample_meta["detected_items"] if item.get("box")]

    total_cal = sum(it.calories for it in detected_items)
    total_prot = sum(it.protein for it in detected_items)
    total_carbs = sum(it.carbs for it in detected_items)
    total_fat = sum(it.fat for it in detected_items)
    total_fiber = sum(it.fiber for it in detected_items)

    return {
        "sample_id": sample_id,
        "image_url": image_url,
        "boxes": boxes,
        "scan_timestamp": datetime.now().isoformat(),
        "detected_items": detected_items,
        "initial_summary": {
            "calories": round(total_cal, 1),
            "protein": round(total_prot, 1),
            "carbs": round(total_carbs, 1),
            "fat": round(total_fat, 1),
            "fiber": round(total_fiber, 1)
        }
    }


@app.post("/api/portion/recalculate")
def recalculate_portion(
    food_id: str,
    portion_size: str,
    custom_grams: Optional[float] = None
):
    """Recalculates food item nutrition when the user adjusts portions in the UI"""
    item = recalculate_food_nutrition(food_id, portion_size, custom_grams)
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    return item


@app.post("/api/analyze-meal", response_model=MealAnalysisResult)
def analyze_meal(payload: MealAnalysisRequest):
    """
    Executes the Personal Context Engine on the user's confirmed meal items.
    """
    profile = payload.user_profile
    if not profile:
        prof_data = get_user_profile("default_user")
        profile = UserProfile(**prof_data)

    today_meals = get_today_meal_logs(profile.id)
    
    result = PersonalContextEngine.analyze(
        items=payload.items,
        profile=profile,
        meal_name=payload.meal_name,
        meal_type=payload.meal_type,
        today_meals=today_meals
    )
    return result


@app.post("/api/meals/log")
def log_meal(payload: Dict[str, Any]):
    user_id = payload.get("user_id", "default_user")
    meal_data = payload.get("meal_data", {})
    log_id = save_meal_log(user_id, meal_data)
    return {"status": "success", "log_id": log_id, "message": "Meal saved to today's nutrition log"}


@app.get("/api/meals/today")
def get_today_context(user_id: str = "default_user"):
    prof = get_user_profile(user_id)
    profile = UserProfile(**prof)
    today_meals = get_today_meal_logs(user_id)

    tot_cal = sum(m["calories"] for m in today_meals)
    tot_prot = sum(m["protein"] for m in today_meals)
    tot_carbs = sum(m["carbs"] for m in today_meals)
    tot_fat = sum(m["fat"] for m in today_meals)
    tot_fiber = sum(m["fiber"] for m in today_meals)

    avg_fit = int(round(sum(m["meal_fit_score"] for m in today_meals) / len(today_meals))) if today_meals else 0

    target_cal = profile.target_calories or 2200.0
    target_prot = profile.target_protein or 75.0
    target_carbs = round((target_cal * 0.52) / 4.0, 1)
    target_fat = round((target_cal * 0.28) / 9.0, 1)

    if not today_meals:
        balance_insight = "No meals logged yet today. Scan or log your breakfast to start tracking your daily fitness context."
    elif tot_prot >= target_prot * 0.8:
        balance_insight = f"Outstanding daily pacing! You've achieved {tot_prot:.0f}g of protein toward your {target_prot:.0f}g target."
    elif tot_cal > target_cal * 1.1:
        balance_insight = "You have reached your estimated energy target for today. Lighter, hydrating evening snacks are recommended."
    else:
        balance_insight = f"Logged {len(today_meals)} meals today with a healthy average Meal Fit Score of {avg_fit}/100."

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_calories": round(tot_cal, 1),
        "total_protein": round(tot_prot, 1),
        "total_carbs": round(tot_carbs, 1),
        "total_fat": round(tot_fat, 1),
        "total_fiber": round(tot_fiber, 1),
        "meals_logged_count": len(today_meals),
        "avg_meal_fit_score": avg_fit,
        "target_calories": target_cal,
        "target_protein": target_prot,
        "target_carbs": target_carbs,
        "target_fat": target_fat,
        "meals": today_meals,
        "daily_balance_insight": balance_insight
    }


@app.post("/api/meals/clear-today")
def reset_today_log(user_id: str = "default_user"):
    clear_today_meals(user_id)
    return {"status": "success", "message": "Today's meal history reset for demo"}


# -------------------------------------------------------------
# SIH Judge Live Demo Matrix Endpoints
# -------------------------------------------------------------

@app.get("/api/demo/personas")
def get_demo_personas():
    return {"personas": DEMO_PERSONAS}


@app.post("/api/demo/compare")
def compare_meal_across_personas(request: DemoComparisonRequest):
    """
    Feeds the EXACT SAME meal through the Personal Context Engine for each persona,
    demonstrating the core innovation to SIH judges.
    """
    if request.sample_meal_id and not request.meal_items:
        items = VisionEngine.scan_sample_meal(request.sample_meal_id)
    else:
        items = request.meal_items

    comparison_results = []

    for p in DEMO_PERSONAS:
        prof = UserProfile(
            id=p["id"],
            name=p["name"],
            age=p["age"],
            gender=p["gender"],
            height_cm=p["height_cm"],
            weight_kg=p["weight_kg"],
            activity_level=p["activity_level"],
            fitness_objective=p["fitness_objective"],
            dietary_preference=p["dietary_preference"]
        )

        analysis = PersonalContextEngine.analyze(
            items=items,
            profile=prof,
            meal_name="Demo Evaluation Meal",
            meal_type="lunch",
            today_meals=[]
        )

        comparison_results.append({
            "persona": p,
            "meal_fit_score": analysis.meal_fit_score,
            "alignment_category": analysis.alignment_category,
            "score_breakdown": analysis.score_breakdown,
            "positive_factors": analysis.positive_factors[:3],
            "areas_to_consider": analysis.areas_to_consider[:2],
            "personalized_insight": analysis.personalized_insight,
            "plate_gap_summary": analysis.plate_gap.gap_summary
        })

    # Summary of the innovation demonstration
    same_meal_macros = {
        "calories": round(sum(i.calories for i in items), 1),
        "protein": round(sum(i.protein for i in items), 1),
        "carbs": round(sum(i.carbs for i in items), 1),
        "fat": round(sum(i.fat for i in items), 1)
    }

    sample_meta = VisionEngine.get_sample_by_id(request.sample_meal_id) if request.sample_meal_id else None

    return {
        "sample_meal": {
            "title": sample_meta["title"] if sample_meta else "Custom Meal",
            "image_url": sample_meta["image_url"] if sample_meta else "/static/assets/images/thali_meal.jpg",
            "description": sample_meta["description"] if sample_meta else "Balanced Indian Meal"
        } if sample_meta else None,
        "meal_macros": same_meal_macros,
        "comparisons": comparison_results,
        "innovation_takeaway": (
            "Notice how the EXACT SAME meal produces different Meal Fit Scores, positive factors, "
            "and suggestions. The nutritional facts remain identical, but their physiological relevance "
            "adapts completely to the individual's activity level and athletic goal."
        )
    }


# -------------------------------------------------------------
# Static Files & Single Page App Serving
# -------------------------------------------------------------
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "NutriLens AI Backend Running. Frontend assets loading..."}
