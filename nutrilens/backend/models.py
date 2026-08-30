"""
NutriLens AI - Data Models
Pydantic schemas for User Profile, Food Items, Portions, Analysis & Demo Requests
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    id: str = "default_user"
    name: str = "Aarav Sharma"
    age: int = 21
    gender: str = "male"  # male, female, other
    height_cm: float = 175.0
    weight_kg: float = 68.0
    activity_level: str = "moderate"  # low, light, moderate, high
    fitness_objective: str = "general_fitness"  
    # general_fitness, sports_performance, improve_strength, improve_endurance, maintain_fitness
    dietary_preference: str = "vegetarian"  # vegetarian, non-vegetarian, vegan, eggetarian
    target_calories: Optional[float] = None
    target_protein: Optional[float] = None


class PortionOption(BaseModel):
    size: str  # small, medium, large, custom
    multiplier: float
    grams: float
    description: str


class FoodItem(BaseModel):
    id: str
    name: str
    hindi_name: Optional[str] = None
    category: str  # grain, legume, dairy, meat, vegetable, fruit, snack, mixed
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: float
    default_serving_grams: float
    default_serving_unit: str  # katori, roti, plate, cup, piece, grams
    portion_options: Dict[str, float]  # small: grams, medium: grams, large: grams


class DetectedFood(BaseModel):
    food_id: str
    name: str
    hindi_name: Optional[str] = None
    confidence: float  # 0.0 - 1.0 (e.g. 0.94)
    portion_size: str = "medium"  # small, medium, large, custom
    portion_grams: float
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    user_confirmed: bool = True


class MealScanResponse(BaseModel):
    image_url: Optional[str] = None
    sample_id: Optional[str] = None
    detected_items: List[DetectedFood]
    scan_timestamp: str
    initial_summary: Dict[str, float]


class PlateGapIndicator(BaseModel):
    macro_name: str
    current_pct: float  # Percentage of this meal's calories/weight
    target_pct: float   # Recommended target percentage for this fitness context
    status: str         # optimal, low, high
    insight: str


class PlateGapAnalysis(BaseModel):
    indicators: List[PlateGapIndicator]
    gap_summary: str
    educational_suggestions: List[str]


class MealFitScoreBreakdown(BaseModel):
    base_nutrition_score: float
    goal_alignment_score: float
    activity_context_score: float
    daily_history_context_score: float
    imbalance_penalties: float
    total_score: int  # 0 - 100
    alignment_category: str  # Optimal Alignment, Good Alignment, Moderate Alignment, Needs Adjustment


class MealAnalysisRequest(BaseModel):
    meal_name: str = "My Meal"
    meal_type: str = "lunch"  # breakfast, lunch, snacks, dinner
    items: List[DetectedFood]
    user_profile: Optional[UserProfile] = None
    image_url: Optional[str] = None


class MealAnalysisResult(BaseModel):
    meal_name: str
    meal_type: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    items: List[DetectedFood]
    meal_fit_score: int
    alignment_category: str
    score_breakdown: MealFitScoreBreakdown
    positive_factors: List[str]
    areas_to_consider: List[str]
    plate_gap: PlateGapAnalysis
    personalized_insight: str
    disclaimer: str = "NutriLens AI provides educational nutritional insights and does not provide medical or clinical advice."


class MealLog(BaseModel):
    id: Optional[int] = None
    user_id: str
    meal_name: str
    meal_type: str
    timestamp: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    meal_fit_score: int
    items_json: str
    personalized_insight: str


class DailyContextSummary(BaseModel):
    date: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    meals_logged_count: int
    avg_meal_fit_score: int
    target_calories: float
    target_protein: float
    target_carbs: float
    target_fat: float
    meals: List[Dict[str, Any]]
    daily_balance_insight: str


class DemoComparisonRequest(BaseModel):
    meal_items: List[DetectedFood]
    sample_meal_id: Optional[str] = None


class RecipeIngredient(BaseModel):
    ingredient_name: str
    quantity: float
    unit: str  # g, ml, tsp, tbsp, piece, pinch, katori
    calories: float
    protein: float
    carbohydrates: float
    fat: float
    fiber: float
    notes: Optional[str] = None


class RecipeItem(BaseModel):
    id: str
    name: str
    hindi_name: Optional[str] = None
    image: str
    description: str
    categories: List[str]  # high_protein, pre_workout, post_workout, balanced_meals, vegetarian, breakfast, lunch, dinner, healthy_snacks
    dietary_type: str  # vegetarian, non-vegetarian, vegan, eggetarian
    servings: int = 1
    preparation_time: str  # e.g. "10 min"
    cooking_time: str      # e.g. "15 min"
    difficulty: str        # Easy, Medium, Hard
    ingredients: List[RecipeIngredient]
    instructions: List[str]
    calories: float
    protein: float
    carbohydrates: float
    fat: float
    fiber: float
    recommended_for: List[str] = Field(default_factory=list)  # fitness_objective tags
    disclaimer: str = "Estimated nutritional values. Values may vary depending on ingredients, brands, and preparation methods."

