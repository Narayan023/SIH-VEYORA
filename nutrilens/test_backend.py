"""
NutriLens AI - Automated Backend & Context Engine Verification Test
"""

import sys
import os

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from database import get_user_profile, save_user_profile, get_all_foods, get_today_meal_logs, clear_today_meals
from models import UserProfile, DetectedFood
from context_engine import PersonalContextEngine
from vision_engine import VisionEngine, SAMPLE_MEALS


def run_tests():
    print("=== [1] Testing Database & Food Catalog ===")
    foods = get_all_foods()
    print(f"✓ Loaded {len(foods)} Indian foods into catalog.")
    assert len(foods) >= 15, "Food catalog should have at least 15 items"

    roti = next((f for f in foods if f["id"] == "roti"), None)
    assert roti is not None, "Roti should exist in catalog"
    print(f"✓ Verified Roti: {roti['name']} ({roti['calories_per_100g']} kcal/100g)")

    print("\n=== [2] Testing AI Vision Engine Sample Detections ===")
    sample_items = VisionEngine.scan_sample_meal("north_indian_thali")
    print(f"✓ Detected {len(sample_items)} items in North Indian Thali:")
    for it in sample_items:
        print(f"   - {it.name}: {it.portion_grams}g -> {it.calories} kcal, {it.protein}g P, {it.carbs}g C, {it.fat}g F (Confidence: {int(it.confidence*100)}%)")
    assert len(sample_items) >= 4, "Thali should have at least 4 items"

    print("\n=== [3] Testing Personal Context Engine (The Core Innovation) ===")
    
    # Persona A: College Student (Moderate Activity, General Fitness)
    student_profile = UserProfile(
        id="student_1",
        name="Aarav (Student)",
        age=20,
        gender="male",
        height_cm=174.0,
        weight_kg=65.0,
        activity_level="moderate",
        fitness_objective="general_fitness",
        dietary_preference="vegetarian"
    )

    # Persona B: Amateur Athlete (High Activity, Sports Performance)
    athlete_profile = UserProfile(
        id="athlete_1",
        name="Vikram (Athlete)",
        age=23,
        gender="male",
        height_cm=178.0,
        weight_kg=72.0,
        activity_level="high",
        fitness_objective="sports_performance",
        dietary_preference="non-vegetarian"
    )

    # Persona C: Gym Beginner (Light Activity, Improve Strength)
    beginner_profile = UserProfile(
        id="beginner_1",
        name="Rohan (Gym Beginner)",
        age=24,
        gender="male",
        height_cm=172.0,
        weight_kg=78.0,
        activity_level="light",
        fitness_objective="improve_strength",
        dietary_preference="vegetarian"
    )

    # Run the EXACT SAME meal through all three contexts
    result_student = PersonalContextEngine.analyze(sample_items, student_profile, "North Indian Thali", "lunch")
    result_athlete = PersonalContextEngine.analyze(sample_items, athlete_profile, "North Indian Thali", "lunch")
    result_beginner = PersonalContextEngine.analyze(sample_items, beginner_profile, "North Indian Thali", "lunch")

    print(f"▶ SAME MEAL SCORES:")
    print(f"   1. College Student (Moderate/General Fit): Score = {result_student.meal_fit_score}/100 [{result_student.alignment_category}]")
    print(f"      Insight: {result_student.personalized_insight}")
    print(f"   2. Amateur Athlete (High/Sports Perf):     Score = {result_athlete.meal_fit_score}/100 [{result_athlete.alignment_category}]")
    print(f"      Insight: {result_athlete.personalized_insight}")
    print(f"   3. Gym Beginner (Light/Improve Strength):  Score = {result_beginner.meal_fit_score}/100 [{result_beginner.alignment_category}]")
    print(f"      Insight: {result_beginner.personalized_insight}")

    print("\n✓ Positive Factors for Athlete:")
    for factor in result_athlete.positive_factors:
        print(f"   ✓ {factor}")

    print("\n✓ PlateGap AI Indicators for Student:")
    for ind in result_student.plate_gap.indicators:
        print(f"   - {ind.macro_name}: {ind.current_pct}% vs Target {ind.target_pct}% ({ind.status})")

    print("\n=== [4] Testing Daily Meal Logging & Contextual Memory ===")
    clear_today_meals("test_user")
    from database import save_meal_log
    
    save_meal_log("test_user", {
        "meal_name": "Breakfast Poha",
        "meal_type": "breakfast",
        "calories": 350.0,
        "protein": 7.0,
        "carbs": 58.0,
        "fat": 8.0,
        "fiber": 4.0,
        "meal_fit_score": 78,
        "items": [],
        "personalized_insight": "Energizing morning start"
    })
    
    today_logs = get_today_meal_logs("test_user")
    assert len(today_logs) == 1, "Should have 1 logged meal"
    print("\n=== [5] Testing Healthy Food Menu Feature ===")
    from database import get_all_recipes, get_recipe_by_id

    all_recipes = get_all_recipes()
    print(f"✓ Loaded {len(all_recipes)} curated Indian recipes in Healthy Food Menu.")
    assert len(all_recipes) >= 15, "Healthy Food Menu should have at least 15 recipes"

    paneer_bowl = get_recipe_by_id("paneer_protein_bowl")
    assert paneer_bowl is not None, "High Protein Paneer Bowl should exist"
    assert len(paneer_bowl["ingredients"]) >= 5, "Paneer Bowl should have detailed exact ingredients"
    assert len(paneer_bowl["instructions"]) >= 4, "Paneer Bowl should have step-by-step instructions"
    print(f"✓ Verified Recipe: {paneer_bowl['name']} ({paneer_bowl['calories']} kcal, {paneer_bowl['protein']}g protein)")
    print(f"   - Ingredients with exact measurements: {len(paneer_bowl['ingredients'])} items")
    for ing in paneer_bowl["ingredients"][:3]:
        print(f"     • {ing['ingredient_name']}: {ing['quantity']} {ing['unit']} -> {ing['calories']} kcal, {ing['protein']}g P")

    # Test category filtering
    high_protein_recipes = get_all_recipes(category="high_protein")
    print(f"✓ High Protein Filter: Found {len(high_protein_recipes)} recipes.")
    assert len(high_protein_recipes) >= 6, "Should find multiple high protein recipes"

    # Test search by ingredient / name
    paneer_search = get_all_recipes(search="paneer")
    print(f"✓ Search 'paneer': Found {len(paneer_search)} recipes matching paneer.")
    assert len(paneer_search) >= 2, "Search for paneer should return at least 2 paneer recipes"

    # Test user objective recommendation
    strength_recs = get_all_recipes(fitness_objective="improve_strength", category="recommended")
    print(f"✓ Profile Recommendation Filter: Found {len(strength_recs)} recommended recipes for Strength Objective.")
    assert len(strength_recs) >= 3, "Strength objective should have recommendations"

    print("\n🎉 ALL BACKEND, CONTEXT ENGINE & HEALTHY FOOD MENU TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    run_tests()

