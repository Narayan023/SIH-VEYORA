"""
NutriLens AI - Database & Indian Food Catalog
SQLite storage + Pre-seeded Indian Food Nutrition Database
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "nutrilens.db")

# Comprehensive Indian Food Nutrition Dataset (per 100g)
INDIAN_FOODS_DATA = [
    {
        "id": "roti",
        "name": "Roti (Whole Wheat Chapati)",
        "hindi_name": "रोटी / चपाती",
        "category": "grain",
        "calories_per_100g": 264.0,
        "protein_per_100g": 9.0,
        "carbs_per_100g": 52.0,
        "fat_per_100g": 2.5,
        "fiber_per_100g": 6.5,
        "default_serving_grams": 40.0,  # ~1 roti = 40g (105 kcal, 3.6g P, 20.8g C)
        "default_serving_unit": "piece (medium)",
        "portion_options": {"small": 30.0, "medium": 40.0, "large": 80.0} # 1 small, 1 med, 2 rotis
    },
    {
        "id": "rice",
        "name": "Cooked White Rice",
        "hindi_name": "चावल / भात",
        "category": "grain",
        "calories_per_100g": 130.0,
        "protein_per_100g": 2.7,
        "carbs_per_100g": 28.2,
        "fat_per_100g": 0.3,
        "fiber_per_100g": 0.4,
        "default_serving_grams": 150.0,  # ~1 katori cooked rice
        "default_serving_unit": "katori (cup)",
        "portion_options": {"small": 100.0, "medium": 150.0, "large": 250.0}
    },
    {
        "id": "brown_rice",
        "name": "Brown Rice",
        "hindi_name": "ब्राउन राइस",
        "category": "grain",
        "calories_per_100g": 111.0,
        "protein_per_100g": 2.6,
        "carbs_per_100g": 23.0,
        "fat_per_100g": 0.9,
        "fiber_per_100g": 1.8,
        "default_serving_grams": 150.0,
        "default_serving_unit": "katori",
        "portion_options": {"small": 100.0, "medium": 150.0, "large": 250.0}
    },
    {
        "id": "dal_tadka",
        "name": "Dal Tadka (Yellow Lentils)",
        "hindi_name": "दाल तड़का",
        "category": "legume",
        "calories_per_100g": 115.0,
        "protein_per_100g": 6.8,
        "carbs_per_100g": 15.2,
        "fat_per_100g": 3.4,
        "fiber_per_100g": 3.8,
        "default_serving_grams": 160.0,  # 1 standard katori
        "default_serving_unit": "katori (bowl)",
        "portion_options": {"small": 100.0, "medium": 160.0, "large": 250.0}
    },
    {
        "id": "rajma",
        "name": "Rajma Masala (Kidney Beans)",
        "hindi_name": "राजमा मसाला",
        "category": "legume",
        "calories_per_100g": 140.0,
        "protein_per_100g": 7.5,
        "carbs_per_100g": 19.5,
        "fat_per_100g": 4.0,
        "fiber_per_100g": 5.2,
        "default_serving_grams": 180.0,
        "default_serving_unit": "katori (bowl)",
        "portion_options": {"small": 120.0, "medium": 180.0, "large": 260.0}
    },
    {
        "id": "chana_masala",
        "name": "Chana Masala (Chickpeas)",
        "hindi_name": "चना मसाला / छोले",
        "category": "legume",
        "calories_per_100g": 155.0,
        "protein_per_100g": 8.0,
        "carbs_per_100g": 21.0,
        "fat_per_100g": 4.5,
        "fiber_per_100g": 6.0,
        "default_serving_grams": 180.0,
        "default_serving_unit": "katori (bowl)",
        "portion_options": {"small": 120.0, "medium": 180.0, "large": 260.0}
    },
    {
        "id": "paneer",
        "name": "Paneer Sabzi / Bhurji",
        "hindi_name": "पनीर सब्जी / भुर्जी",
        "category": "dairy",
        "calories_per_100g": 265.0,
        "protein_per_100g": 16.5,
        "carbs_per_100g": 4.8,
        "fat_per_100g": 20.0,
        "fiber_per_100g": 0.8,
        "default_serving_grams": 120.0,
        "default_serving_unit": "katori (serving)",
        "portion_options": {"small": 80.0, "medium": 120.0, "large": 180.0}
    },
    {
        "id": "curd",
        "name": "Curd / Plain Dahi",
        "hindi_name": "दही",
        "category": "dairy",
        "calories_per_100g": 60.0,
        "protein_per_100g": 3.5,
        "carbs_per_100g": 4.7,
        "fat_per_100g": 3.1,
        "fiber_per_100g": 0.0,
        "default_serving_grams": 100.0,
        "default_serving_unit": "katori (cup)",
        "portion_options": {"small": 60.0, "medium": 100.0, "large": 180.0}
    },
    {
        "id": "chicken_curry",
        "name": "Indian Chicken Curry",
        "hindi_name": "चिकन करी",
        "category": "meat",
        "calories_per_100g": 185.0,
        "protein_per_100g": 19.2,
        "carbs_per_100g": 4.0,
        "fat_per_100g": 10.5,
        "fiber_per_100g": 0.8,
        "default_serving_grams": 160.0,
        "default_serving_unit": "katori (bowl)",
        "portion_options": {"small": 100.0, "medium": 160.0, "large": 240.0}
    },
    {
        "id": "egg_boiled",
        "name": "Boiled Eggs",
        "hindi_name": "उबले अंडे",
        "category": "meat",
        "calories_per_100g": 155.0,
        "protein_per_100g": 13.0,
        "carbs_per_100g": 1.1,
        "fat_per_100g": 11.0,
        "fiber_per_100g": 0.0,
        "default_serving_grams": 100.0,  # ~2 eggs = 100g
        "default_serving_unit": "2 whole eggs",
        "portion_options": {"small": 50.0, "medium": 100.0, "large": 150.0} # 1, 2, 3 eggs
    },
    {
        "id": "egg_curry",
        "name": "Egg Curry (2 Eggs + Gravy)",
        "hindi_name": "अंडा करी",
        "category": "meat",
        "calories_per_100g": 160.0,
        "protein_per_100g": 11.0,
        "carbs_per_100g": 5.5,
        "fat_per_100g": 10.5,
        "fiber_per_100g": 1.0,
        "default_serving_grams": 160.0,
        "default_serving_unit": "katori",
        "portion_options": {"small": 100.0, "medium": 160.0, "large": 220.0}
    },
    {
        "id": "sabzi_mix",
        "name": "Mixed Vegetable Sabzi",
        "hindi_name": "मिक्स वेज सब्जी",
        "category": "vegetable",
        "calories_per_100g": 90.0,
        "protein_per_100g": 2.8,
        "carbs_per_100g": 11.2,
        "fat_per_100g": 4.0,
        "fiber_per_100g": 3.8,
        "default_serving_grams": 140.0,
        "default_serving_unit": "katori (bowl)",
        "portion_options": {"small": 90.0, "medium": 140.0, "large": 200.0}
    },
    {
        "id": "green_salad",
        "name": "Indian Salad (Cucumber, Tomato, Onion)",
        "hindi_name": "सलाद",
        "category": "vegetable",
        "calories_per_100g": 22.0,
        "protein_per_100g": 0.9,
        "carbs_per_100g": 4.5,
        "fat_per_100g": 0.2,
        "fiber_per_100g": 1.8,
        "default_serving_grams": 80.0,
        "default_serving_unit": "plate",
        "portion_options": {"small": 50.0, "medium": 80.0, "large": 150.0}
    },
    {
        "id": "poha",
        "name": "Kanda Poha (Flattened Rice)",
        "hindi_name": "कांदा पोहा",
        "category": "grain",
        "calories_per_100g": 170.0,
        "protein_per_100g": 3.8,
        "carbs_per_100g": 28.5,
        "fat_per_100g": 4.6,
        "fiber_per_100g": 2.2,
        "default_serving_grams": 180.0,
        "default_serving_unit": "plate",
        "portion_options": {"small": 120.0, "medium": 180.0, "large": 260.0}
    },
    {
        "id": "idli",
        "name": "Steamed Idli (2 pieces)",
        "hindi_name": "इडली (2 पीस)",
        "category": "grain",
        "calories_per_100g": 140.0,
        "protein_per_100g": 4.2,
        "carbs_per_100g": 28.0,
        "fat_per_100g": 0.5,
        "fiber_per_100g": 1.5,
        "default_serving_grams": 100.0,  # ~2 standard idlis
        "default_serving_unit": "2 pieces",
        "portion_options": {"small": 50.0, "medium": 100.0, "large": 150.0} # 1, 2, 3 idlis
    },
    {
        "id": "dosa",
        "name": "Plain / Masala Dosa",
        "hindi_name": "डोसा",
        "category": "grain",
        "calories_per_100g": 190.0,
        "protein_per_100g": 4.5,
        "carbs_per_100g": 29.0,
        "fat_per_100g": 6.2,
        "fiber_per_100g": 1.8,
        "default_serving_grams": 140.0,
        "default_serving_unit": "1 piece",
        "portion_options": {"small": 90.0, "medium": 140.0, "large": 220.0}
    },
    {
        "id": "sambar",
        "name": "Vegetable Sambar",
        "hindi_name": "सांभर",
        "category": "legume",
        "calories_per_100g": 65.0,
        "protein_per_100g": 2.8,
        "carbs_per_100g": 10.5,
        "fat_per_100g": 1.4,
        "fiber_per_100g": 2.2,
        "default_serving_grams": 150.0,
        "default_serving_unit": "katori (bowl)",
        "portion_options": {"small": 100.0, "medium": 150.0, "large": 220.0}
    },
    {
        "id": "upma",
        "name": "Rava Upma with Veggies",
        "hindi_name": "उपमा",
        "category": "grain",
        "calories_per_100g": 160.0,
        "protein_per_100g": 3.6,
        "carbs_per_100g": 25.0,
        "fat_per_100g": 5.0,
        "fiber_per_100g": 2.0,
        "default_serving_grams": 160.0,
        "default_serving_unit": "plate",
        "portion_options": {"small": 110.0, "medium": 160.0, "large": 240.0}
    },
    {
        "id": "banana",
        "name": "Fresh Banana",
        "hindi_name": "केला",
        "category": "fruit",
        "calories_per_100g": 89.0,
        "protein_per_100g": 1.1,
        "carbs_per_100g": 22.8,
        "fat_per_100g": 0.3,
        "fiber_per_100g": 2.6,
        "default_serving_grams": 100.0,
        "default_serving_unit": "1 medium fruit",
        "portion_options": {"small": 70.0, "medium": 100.0, "large": 150.0}
    },
    {
        "id": "apple",
        "name": "Fresh Apple",
        "hindi_name": "सेब",
        "category": "fruit",
        "calories_per_100g": 52.0,
        "protein_per_100g": 0.3,
        "carbs_per_100g": 13.8,
        "fat_per_100g": 0.2,
        "fiber_per_100g": 2.4,
        "default_serving_grams": 120.0,
        "default_serving_unit": "1 medium fruit",
        "portion_options": {"small": 80.0, "medium": 120.0, "large": 180.0}
    },
    {
        "id": "sprouts_salad",
        "name": "Moong Sprout Salad",
        "hindi_name": "अंकुरित मूंग सलाद",
        "category": "legume",
        "calories_per_100g": 105.0,
        "protein_per_100g": 7.0,
        "carbs_per_100g": 16.0,
        "fat_per_100g": 1.2,
        "fiber_per_100g": 4.5,
        "default_serving_grams": 100.0,
        "default_serving_unit": "katori",
        "portion_options": {"small": 60.0, "medium": 100.0, "large": 160.0}
    }
]

# Comprehensive Indian Healthy Food Menu Dataset with Exact Ingredient Measurements & Step-by-Step Cooking Guide
INDIAN_RECIPES_DATA = [
    {
        "id": "paneer_protein_bowl",
        "name": "High Protein Paneer Bowl",
        "hindi_name": "हाई प्रोटीन पनीर बाउल",
        "image": "/static/assets/images/paneer_roti_meal.jpg",
        "description": "Golden pan-seared paneer cubes over warm steamed brown rice with refreshing cucumber, diced tomatoes, seasoned dahi, and a zesty lemon drizzle.",
        "categories": ["high_protein", "lunch", "dinner", "vegetarian", "post_workout", "balanced_meals"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "10 min",
        "cooking_time": "15 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Fresh Low-Fat Paneer (Cubes)",
                "quantity": 100.0,
                "unit": "g",
                "calories": 265.0,
                "protein": 18.0,
                "carbohydrates": 4.0,
                "fat": 20.0,
                "fiber": 0.5,
                "notes": "Lightly pan-tossed in non-stick pan"
            },
            {
                "ingredient_name": "Cooked Brown Rice",
                "quantity": 120.0,
                "unit": "g",
                "calories": 133.2,
                "protein": 3.1,
                "carbohydrates": 27.6,
                "fat": 1.1,
                "fiber": 2.2,
                "notes": "Steamed whole grain"
            },
            {
                "ingredient_name": "Fresh Diced Cucumber",
                "quantity": 50.0,
                "unit": "g",
                "calories": 8.0,
                "protein": 0.3,
                "carbohydrates": 1.8,
                "fat": 0.1,
                "fiber": 0.5,
                "notes": "Crisp salad base"
            },
            {
                "ingredient_name": "Chopped Tomatoes",
                "quantity": 50.0,
                "unit": "g",
                "calories": 9.0,
                "protein": 0.4,
                "carbohydrates": 2.0,
                "fat": 0.1,
                "fiber": 0.6,
                "notes": "Rich in lycopene"
            },
            {
                "ingredient_name": "Fresh Curd / Plain Dahi",
                "quantity": 80.0,
                "unit": "g",
                "calories": 48.0,
                "protein": 2.8,
                "carbohydrates": 3.8,
                "fat": 2.5,
                "fiber": 0.0,
                "notes": "Probiotic digestive support"
            },
            {
                "ingredient_name": "Fresh Lemon Juice",
                "quantity": 1.0,
                "unit": "tsp (5 ml)",
                "calories": 1.5,
                "protein": 0.0,
                "carbohydrates": 0.4,
                "fat": 0.0,
                "fiber": 0.1,
                "notes": "Vitamin C boost"
            },
            {
                "ingredient_name": "Roasted Cumin & Chaat Masala",
                "quantity": 0.5,
                "unit": "tsp (2 g)",
                "calories": 6.0,
                "protein": 0.2,
                "carbohydrates": 0.9,
                "fat": 0.3,
                "fiber": 0.2,
                "notes": "Aromatic digestive spice blend"
            }
        ],
        "instructions": [
            "Cut 100g fresh paneer into bite-sized cubes and dust lightly with roasted cumin powder and a pinch of black salt.",
            "Heat a non-stick pan over medium flame and sear paneer cubes for 2-3 minutes until golden brown.",
            "Place 120g warm cooked brown rice at the base of your serving bowl.",
            "Arrange the pan-seared paneer, diced cucumber, and chopped tomatoes neatly around the rice.",
            "Whisk 80g curd with chaat masala and spoon over the top.",
            "Finish with a squeeze of 1 tsp fresh lemon juice and serve immediately."
        ],
        "calories": 470.7,
        "protein": 24.8,
        "carbohydrates": 40.5,
        "fat": 24.1,
        "fiber": 4.1,
        "recommended_for": ["improve_strength", "sports_performance", "general_fitness", "maintain_fitness"]
    },
    {
        "id": "moong_dal_chilla",
        "name": "Moong Dal Chilla (High-Protein Lentil Crepe)",
        "hindi_name": "मूंग दाल चीला",
        "image": "/static/assets/images/thali_meal.jpg",
        "description": "Crispy golden crepes crafted from protein-packed soaked yellow lentils, seasoned with cumin, ginger, and fresh green herbs.",
        "categories": ["high_protein", "breakfast", "vegetarian", "pre_workout", "balanced_meals"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "15 min (excl. soaking)",
        "cooking_time": "10 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Yellow Moong Dal (Ground Batter)",
                "quantity": 80.0,
                "unit": "g",
                "calories": 278.0,
                "protein": 19.2,
                "carbohydrates": 48.0,
                "fat": 1.0,
                "fiber": 6.4,
                "notes": "Soaked 2 hours & blended smooth"
            },
            {
                "ingredient_name": "Finely Chopped Onions",
                "quantity": 30.0,
                "unit": "g",
                "calories": 12.0,
                "protein": 0.3,
                "carbohydrates": 2.8,
                "fat": 0.0,
                "fiber": 0.5,
                "notes": "Adds sweet crunch"
            },
            {
                "ingredient_name": "Green Chilli & Ginger Paste",
                "quantity": 1.0,
                "unit": "tsp (5 g)",
                "calories": 4.0,
                "protein": 0.1,
                "carbohydrates": 0.9,
                "fat": 0.0,
                "fiber": 0.2,
                "notes": "Metabolism booster"
            },
            {
                "ingredient_name": "Fresh Coriander Leaves",
                "quantity": 10.0,
                "unit": "g",
                "calories": 2.3,
                "protein": 0.2,
                "carbohydrates": 0.4,
                "fat": 0.0,
                "fiber": 0.3,
                "notes": "Rich in phytonutrients"
            },
            {
                "ingredient_name": "Cold-Pressed Mustard / Olive Oil",
                "quantity": 1.0,
                "unit": "tsp (5 ml)",
                "calories": 44.0,
                "protein": 0.0,
                "carbohydrates": 0.0,
                "fat": 5.0,
                "fiber": 0.0,
                "notes": "For non-stick tawa pan roasting"
            },
            {
                "ingredient_name": "Cumin & Turmeric Spice Mix",
                "quantity": 0.5,
                "unit": "tsp (2 g)",
                "calories": 6.0,
                "protein": 0.2,
                "carbohydrates": 0.9,
                "fat": 0.2,
                "fiber": 0.4,
                "notes": "Anti-inflammatory golden spices"
            }
        ],
        "instructions": [
            "Blend 80g soaked moong dal with ginger, green chilli, and 3-4 tbsp water to make a smooth pourable batter.",
            "Stir in chopped onions, fresh coriander, cumin seeds, turmeric, and rock salt.",
            "Heat a flat non-stick tawa or cast-iron skillet on medium flame and brush with 1/2 tsp oil.",
            "Pour a ladle of batter (approx 2 chillas) onto center and swirl outwards into a thin round crepe.",
            "Cook for 2-3 minutes until golden crisp edges appear, flip and cook the other side for 1-2 minutes.",
            "Serve hot alongside mint chutney or seasoned curd."
        ],
        "calories": 346.3,
        "protein": 20.0,
        "carbohydrates": 53.0,
        "fat": 6.2,
        "fiber": 7.8,
        "recommended_for": ["general_fitness", "sports_performance", "improve_strength", "maintain_fitness"]
    },
    {
        "id": "vegetable_poha",
        "name": "Vegetable Poha with Roasted Peanuts",
        "hindi_name": "वेजिटेबल कांदा पोहा",
        "image": "/static/assets/images/poha_curd_meal.jpg",
        "description": "Light and fluffy flattened rice sautéed with crisp peanuts, tender green peas, onions, mustard seeds, curry leaves, and a squeeze of fresh lime.",
        "categories": ["breakfast", "vegetarian", "pre_workout", "balanced_meals"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "5 min",
        "cooking_time": "10 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Flattened Rice (Thick Poha)",
                "quantity": 70.0,
                "unit": "g",
                "calories": 245.0,
                "protein": 4.6,
                "carbohydrates": 54.0,
                "fat": 1.4,
                "fiber": 2.0,
                "notes": "Rinsed and drained"
            },
            {
                "ingredient_name": "Roasted Peanuts",
                "quantity": 20.0,
                "unit": "g",
                "calories": 113.4,
                "protein": 5.2,
                "carbohydrates": 3.2,
                "fat": 9.8,
                "fiber": 1.7,
                "notes": "Rich in healthy plant fats & protein"
            },
            {
                "ingredient_name": "Chopped Onion & Green Chilli",
                "quantity": 40.0,
                "unit": "g",
                "calories": 16.0,
                "protein": 0.5,
                "carbohydrates": 3.6,
                "fat": 0.1,
                "fiber": 0.7,
                "notes": "Aromatic base"
            },
            {
                "ingredient_name": "Boiled Green Peas",
                "quantity": 30.0,
                "unit": "g",
                "calories": 24.0,
                "protein": 1.6,
                "carbohydrates": 4.3,
                "fat": 0.1,
                "fiber": 1.5,
                "notes": "Adds natural sweetness & fiber"
            },
            {
                "ingredient_name": "Mustard Seeds & Curry Leaves",
                "quantity": 0.5,
                "unit": "tsp (3 g)",
                "calories": 12.0,
                "protein": 0.6,
                "carbohydrates": 0.8,
                "fat": 0.8,
                "fiber": 0.4,
                "notes": "Classic South/West Indian tadka"
            },
            {
                "ingredient_name": "Sunflower / Peanut Oil",
                "quantity": 1.0,
                "unit": "tsp (5 ml)",
                "calories": 44.0,
                "protein": 0.0,
                "carbohydrates": 0.0,
                "fat": 5.0,
                "fiber": 0.0,
                "notes": "Healthy cooking fat"
            },
            {
                "ingredient_name": "Fresh Lemon Juice",
                "quantity": 1.0,
                "unit": "tsp (5 ml)",
                "calories": 1.5,
                "protein": 0.0,
                "carbohydrates": 0.3,
                "fat": 0.0,
                "fiber": 0.1,
                "notes": "Bright citrus finish"
            }
        ],
        "instructions": [
            "Rinse 70g poha in a strainer under cold water for 30 seconds and set aside to drain and soften.",
            "Heat 1 tsp oil in a kadai/pan, add mustard seeds and curry leaves until they crackle.",
            "Add 20g peanuts and roast until aromatic and golden (1-2 mins).",
            "Add chopped onions, green peas, and green chilli with a pinch of turmeric and salt; sauté for 3 minutes.",
            "Gently fold in the rinsed poha, cover with lid on low flame for 2 minutes to steam through.",
            "Turn off heat, drizzle 1 tsp lemon juice, garnish with coriander, and enjoy."
        ],
        "calories": 455.9,
        "protein": 12.5,
        "carbohydrates": 66.2,
        "fat": 17.2,
        "fiber": 6.4,
        "recommended_for": ["general_fitness", "improve_endurance", "maintain_fitness"]
    },
    {
        "id": "besan_chilla_paneer",
        "name": "Besan Chilla with Grated Paneer",
        "hindi_name": "बेसन चीला पनीर स्टफिंग",
        "image": "/static/assets/images/masala_dosa_meal.jpg",
        "description": "High-fiber chickpea flour savory pancake stuffed with fresh grated paneer, juicy tomatoes, and carom seeds for easy digestion.",
        "categories": ["high_protein", "breakfast", "vegetarian", "post_workout", "healthy_snacks"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "8 min",
        "cooking_time": "10 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Gram Flour (Pure Besan)",
                "quantity": 60.0,
                "unit": "g",
                "calories": 232.2,
                "protein": 13.4,
                "carbohydrates": 34.7,
                "fat": 3.2,
                "fiber": 6.5,
                "notes": "Gluten-free protein flour"
            },
            {
                "ingredient_name": "Grated Fresh Paneer (Filling)",
                "quantity": 40.0,
                "unit": "g",
                "calories": 106.0,
                "protein": 6.6,
                "carbohydrates": 1.9,
                "fat": 8.0,
                "fiber": 0.3,
                "notes": "Creamy protein stuffing"
            },
            {
                "ingredient_name": "Finely Diced Onion",
                "quantity": 30.0,
                "unit": "g",
                "calories": 12.0,
                "protein": 0.3,
                "carbohydrates": 2.8,
                "fat": 0.0,
                "fiber": 0.5,
                "notes": "Crunchy texture"
            },
            {
                "ingredient_name": "Finely Diced Tomato",
                "quantity": 30.0,
                "unit": "g",
                "calories": 5.4,
                "protein": 0.3,
                "carbohydrates": 1.2,
                "fat": 0.1,
                "fiber": 0.4,
                "notes": "Juicy filling"
            },
            {
                "ingredient_name": "Ajwain (Carom Seeds) & Spices",
                "quantity": 0.5,
                "unit": "tsp (2 g)",
                "calories": 7.0,
                "protein": 0.3,
                "carbohydrates": 0.9,
                "fat": 0.3,
                "fiber": 0.4,
                "notes": "Aids gastric digestion"
            },
            {
                "ingredient_name": "Olive / Mustard Oil",
                "quantity": 1.0,
                "unit": "tsp (5 ml)",
                "calories": 44.0,
                "protein": 0.0,
                "carbohydrates": 0.0,
                "fat": 5.0,
                "fiber": 0.0,
                "notes": "Tawa roasting"
            }
        ],
        "instructions": [
            "In a bowl, mix 60g besan with ajwain, turmeric, chilli powder, salt, and 1/3 cup water to form smooth batter.",
            "In a small side bowl, toss 40g grated paneer with chopped onion, tomato, and a pinch of chaat masala.",
            "Heat a tawa on medium, grease with 1/2 tsp oil, and spread half the batter into a round pancake.",
            "Cook for 2 minutes, flip and cook the other side for 1 minute.",
            "Place half the paneer filling on one half of the chilla and fold over like a taco.",
            "Repeat for the second chilla and serve warm."
        ],
        "calories": 406.6,
        "protein": 20.9,
        "carbohydrates": 41.5,
        "fat": 16.6,
        "fiber": 8.1,
        "recommended_for": ["improve_strength", "sports_performance", "general_fitness"]
    },
    {
        "id": "oats_veg_upma",
        "name": "Oats & Vegetable Upma",
        "hindi_name": "ओट्स वेज उपमा",
        "image": "/static/assets/images/poha_curd_meal.jpg",
        "description": "Nutrient-dense rolled oats tempered with mustard, curry leaves, carrots, beans, and crunchy cashews for slow-release morning energy.",
        "categories": ["breakfast", "vegetarian", "healthy_snacks", "balanced_meals"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "5 min",
        "cooking_time": "10 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Whole Rolled Oats",
                "quantity": 60.0,
                "unit": "g",
                "calories": 233.4,
                "protein": 8.0,
                "carbohydrates": 40.0,
                "fat": 4.2,
                "fiber": 6.4,
                "notes": "Beta-glucan soluble fiber"
            },
            {
                "ingredient_name": "Diced Carrots & French Beans",
                "quantity": 60.0,
                "unit": "g",
                "calories": 22.0,
                "protein": 1.0,
                "carbohydrates": 4.5,
                "fat": 0.2,
                "fiber": 2.0,
                "notes": "Vitamins & micronutrients"
            },
            {
                "ingredient_name": "Chopped Red Onion",
                "quantity": 30.0,
                "unit": "g",
                "calories": 12.0,
                "protein": 0.3,
                "carbohydrates": 2.8,
                "fat": 0.0,
                "fiber": 0.5,
                "notes": "Flavor base"
            },
            {
                "ingredient_name": "Roasted Cashews / Peanuts",
                "quantity": 10.0,
                "unit": "g",
                "calories": 58.0,
                "protein": 2.0,
                "carbohydrates": 3.0,
                "fat": 4.6,
                "fiber": 0.4,
                "notes": "Healthy fats & crunch"
            },
            {
                "ingredient_name": "Mustard, Curry Leaves & Ginger",
                "quantity": 1.0,
                "unit": "tsp (5 g)",
                "calories": 14.0,
                "protein": 0.5,
                "carbohydrates": 1.5,
                "fat": 0.7,
                "fiber": 0.5,
                "notes": "Traditional tempering"
            },
            {
                "ingredient_name": "Cold-Pressed Cooking Oil",
                "quantity": 1.0,
                "unit": "tsp (5 ml)",
                "calories": 44.0,
                "protein": 0.0,
                "carbohydrates": 0.0,
                "fat": 5.0,
                "fiber": 0.0,
                "notes": "Heart-healthy oil"
            }
        ],
        "instructions": [
            "Dry roast 60g oats in a pan on low flame for 3 minutes until slightly fragrant, then transfer to a plate.",
            "In the same pan, heat 1 tsp oil and add mustard seeds, curry leaves, minced ginger, and cashews.",
            "Add chopped onions, carrots, and beans with 1/4 tsp salt; sauté for 3 minutes.",
            "Pour in 1 cup (200 ml) water and bring to a boil.",
            "Gradually stir in the roasted oats, reduce heat, cover with lid, and cook for 2-3 minutes until water is absorbed.",
            "Fluff with a fork and serve hot."
        ],
        "calories": 383.4,
        "protein": 11.8,
        "carbohydrates": 51.8,
        "fat": 14.7,
        "fiber": 9.8,
        "recommended_for": ["general_fitness", "improve_endurance", "maintain_fitness"]
    },
    {
        "id": "paneer_bhurji_roti",
        "name": "Paneer Bhurji with Whole Wheat Roti",
        "hindi_name": "पनीर भुर्जी और चपाती",
        "image": "/static/assets/images/paneer_roti_meal.jpg",
        "description": "Scrambled fresh cottage cheese cooked with onions, ripe tomatoes, green peas, and fragrant spices, served with two soft whole wheat rotis.",
        "categories": ["high_protein", "lunch", "dinner", "vegetarian", "post_workout"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "10 min",
        "cooking_time": "15 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Fresh Crumbled Paneer",
                "quantity": 120.0,
                "unit": "g",
                "calories": 318.0,
                "protein": 19.8,
                "carbohydrates": 5.8,
                "fat": 24.0,
                "fiber": 1.0,
                "notes": "High biological value protein"
            },
            {
                "ingredient_name": "Whole Wheat Roti (2 medium)",
                "quantity": 80.0,
                "unit": "g",
                "calories": 211.2,
                "protein": 7.2,
                "carbohydrates": 41.6,
                "fat": 2.0,
                "fiber": 5.2,
                "notes": "Complex whole grain carbohydrate"
            },
            {
                "ingredient_name": "Diced Red Onions",
                "quantity": 40.0,
                "unit": "g",
                "calories": 16.0,
                "protein": 0.5,
                "carbohydrates": 3.7,
                "fat": 0.1,
                "fiber": 0.7,
                "notes": "Sautéed base"
            },
            {
                "ingredient_name": "Diced Ripe Tomatoes",
                "quantity": 40.0,
                "unit": "g",
                "calories": 7.2,
                "protein": 0.4,
                "carbohydrates": 1.6,
                "fat": 0.1,
                "fiber": 0.5,
                "notes": "Natural gravy acidity"
            },
            {
                "ingredient_name": "Green Peas",
                "quantity": 30.0,
                "unit": "g",
                "calories": 24.0,
                "protein": 1.6,
                "carbohydrates": 4.3,
                "fat": 0.1,
                "fiber": 1.5,
                "notes": "Adds sweetness & fiber"
            },
            {
                "ingredient_name": "Cooking Oil & Masala Spices",
                "quantity": 6.0,
                "unit": "g",
                "calories": 48.6,
                "protein": 0.3,
                "carbohydrates": 1.2,
                "fat": 5.1,
                "fiber": 0.4,
                "notes": "1 tsp oil + turmeric, cumin & garam masala"
            }
        ],
        "instructions": [
            "Heat 1 tsp oil in a pan, add 1/2 tsp cumin seeds until they splutter.",
            "Add chopped onions and green chillies; sauté for 3 minutes until translucent.",
            "Add diced tomatoes, green peas, turmeric, coriander powder, and salt; cook until tomatoes turn soft.",
            "Add 120g crumbled paneer and toss well on medium flame for 3 minutes (avoid overcooking).",
            "Garnish with chopped fresh coriander leaves.",
            "Serve hot with 2 whole wheat rotis."
        ],
        "calories": 625.0,
        "protein": 29.8,
        "carbohydrates": 58.2,
        "fat": 31.4,
        "fiber": 9.3,
        "recommended_for": ["improve_strength", "sports_performance", "general_fitness"]
    },
    {
        "id": "dal_tadka_brown_rice",
        "name": "Dal Tadka & Brown Rice Protein Bowl",
        "hindi_name": "दाल तड़का और ब्राउन राइस",
        "image": "/static/assets/images/thali_meal.jpg",
        "description": "Homestyle yellow lentil soup tempered with garlic, cumin, and desi ghee, served over unpolished brown rice and a fresh side salad.",
        "categories": ["lunch", "dinner", "vegetarian", "balanced_meals"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "10 min",
        "cooking_time": "20 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Cooked Yellow Toor Dal",
                "quantity": 180.0,
                "unit": "g",
                "calories": 207.0,
                "protein": 12.2,
                "carbohydrates": 27.4,
                "fat": 6.1,
                "fiber": 6.8,
                "notes": "Rich in essential amino acids"
            },
            {
                "ingredient_name": "Cooked Brown Rice",
                "quantity": 140.0,
                "unit": "g",
                "calories": 155.4,
                "protein": 3.6,
                "carbohydrates": 32.2,
                "fat": 1.3,
                "fiber": 2.5,
                "notes": "Low glycemic whole grain"
            },
            {
                "ingredient_name": "Desi Ghee (Tempering)",
                "quantity": 1.0,
                "unit": "tsp (5 g)",
                "calories": 45.0,
                "protein": 0.0,
                "carbohydrates": 0.0,
                "fat": 5.0,
                "fiber": 0.0,
                "notes": "Fat-soluble vitamin assimilation"
            },
            {
                "ingredient_name": "Cucumber & Tomato Salad",
                "quantity": 60.0,
                "unit": "g",
                "calories": 12.6,
                "protein": 0.5,
                "carbohydrates": 2.7,
                "fat": 0.1,
                "fiber": 0.8,
                "notes": "Enzyme-rich raw veggies"
            }
        ],
        "instructions": [
            "Pressure cook 60g raw toor dal with 1.5 cups water, turmeric, and salt for 4 whistles.",
            "In a small tadka pan, heat 1 tsp desi ghee. Add cumin seeds, minced garlic, and a pinch of hing.",
            "Pour sizzling tadka over the hot cooked dal and cover for 2 minutes to infuse aromas.",
            "Plate 140g cooked brown rice alongside the dal.",
            "Add 60g sliced cucumber and tomato with lemon juice on the side."
        ],
        "calories": 420.0,
        "protein": 16.3,
        "carbohydrates": 62.3,
        "fat": 12.5,
        "fiber": 10.1,
        "recommended_for": ["general_fitness", "maintain_fitness", "improve_endurance"]
    },
    {
        "id": "vegetable_khichdi",
        "name": "Nutritious Moong Dal Vegetable Khichdi",
        "hindi_name": "पौष्टिक मूंग दाल खिचड़ी",
        "image": "/static/assets/images/thali_meal.jpg",
        "description": "One-pot Ayurvedic superfood combining yellow lentils, rice, chopped spinach, and sweet carrots, tempered lightly in pure desi ghee.",
        "categories": ["dinner", "vegetarian", "balanced_meals"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "5 min",
        "cooking_time": "15 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Yellow Moong Dal (Cooked)",
                "quantity": 100.0,
                "unit": "g",
                "calories": 115.0,
                "protein": 7.8,
                "carbohydrates": 19.5,
                "fat": 0.5,
                "fiber": 3.5,
                "notes": "Gentle on stomach"
            },
            {
                "ingredient_name": "Cooked White / Brown Rice",
                "quantity": 100.0,
                "unit": "g",
                "calories": 130.0,
                "protein": 2.7,
                "carbohydrates": 28.2,
                "fat": 0.3,
                "fiber": 0.4,
                "notes": "Easily digestible starch"
            },
            {
                "ingredient_name": "Chopped Spinach & Carrots",
                "quantity": 70.0,
                "unit": "g",
                "calories": 20.0,
                "protein": 1.5,
                "carbohydrates": 3.8,
                "fat": 0.2,
                "fiber": 2.1,
                "notes": "Iron & Vitamin A"
            },
            {
                "ingredient_name": "Pure Desi Ghee",
                "quantity": 1.0,
                "unit": "tsp (5 g)",
                "calories": 45.0,
                "protein": 0.0,
                "carbohydrates": 0.0,
                "fat": 5.0,
                "fiber": 0.0,
                "notes": "Butyric acid for gut health"
            },
            {
                "ingredient_name": "Hing, Cumin & Turmeric",
                "quantity": 0.5,
                "unit": "tsp (2 g)",
                "calories": 6.0,
                "protein": 0.2,
                "carbohydrates": 0.9,
                "fat": 0.2,
                "fiber": 0.3,
                "notes": "Digestive spices"
            }
        ],
        "instructions": [
            "Wash 50g moong dal and 50g rice together in water.",
            "In a pressure cooker, heat 1 tsp ghee; add cumin seeds and hing until sizzling.",
            "Add chopped spinach, carrots, turmeric powder, and salt; stir for 1 minute.",
            "Add the washed dal-rice mixture and 2.5 cups of water.",
            "Cook for 3-4 whistles on medium flame until soft and comforting.",
            "Serve warm with a side of plain curd or pickle."
        ],
        "calories": 316.0,
        "protein": 12.2,
        "carbohydrates": 52.4,
        "fat": 6.2,
        "fiber": 6.3,
        "recommended_for": ["general_fitness", "maintain_fitness"]
    },
    {
        "id": "probiotic_curd_rice",
        "name": "Tempered Probiotic Curd Rice",
        "hindi_name": "तड़का कर्ड राइस (दही भात)",
        "image": "/static/assets/images/poha_curd_meal.jpg",
        "description": "Cooling South Indian comfort food made with fluffy rice, live probiotic yogurt, ruby pomegranate seeds, and tempered mustard seeds.",
        "categories": ["lunch", "dinner", "vegetarian", "healthy_snacks"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "5 min",
        "cooking_time": "5 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Steamed White Rice (Slightly Mashed)",
                "quantity": 140.0,
                "unit": "g",
                "calories": 182.0,
                "protein": 3.8,
                "carbohydrates": 39.5,
                "fat": 0.4,
                "fiber": 0.6,
                "notes": "Cooling carb base"
            },
            {
                "ingredient_name": "Fresh Low-Fat Curd (Dahi)",
                "quantity": 120.0,
                "unit": "g",
                "calories": 72.0,
                "protein": 4.2,
                "carbohydrates": 5.6,
                "fat": 3.7,
                "fiber": 0.0,
                "notes": "Lactobacillus probiotics"
            },
            {
                "ingredient_name": "Fresh Pomegranate Arils",
                "quantity": 20.0,
                "unit": "g",
                "calories": 16.6,
                "protein": 0.3,
                "carbohydrates": 3.8,
                "fat": 0.2,
                "fiber": 0.8,
                "notes": "Polyphenol antioxidants"
            },
            {
                "ingredient_name": "Mustard, Curry Leaves & Ginger Tadka",
                "quantity": 1.0,
                "unit": "tsp (4 g)",
                "calories": 26.4,
                "protein": 0.2,
                "carbohydrates": 0.6,
                "fat": 2.6,
                "fiber": 0.2,
                "notes": "1/2 tsp oil + tempering spices"
            }
        ],
        "instructions": [
            "In a bowl, gently mash 140g warm cooked rice with a fork.",
            "Allow to cool to room temperature, then mix in 120g fresh curd and 1/4 tsp rock salt.",
            "Heat 1/2 tsp oil in a small pan; add mustard seeds, curry leaves, minced ginger, and 1 green chilli.",
            "Pour hot tadka over curd rice and stir gently.",
            "Top with 20g fresh pomegranate arils and chill for 10 minutes before serving."
        ],
        "calories": 297.0,
        "protein": 8.5,
        "carbohydrates": 49.5,
        "fat": 6.9,
        "fiber": 1.6,
        "recommended_for": ["general_fitness", "maintain_fitness"]
    },
    {
        "id": "sprouts_chaat",
        "name": "Moong & Black Chana Sprouts Chaat",
        "hindi_name": "अंकुरित मूंग व चना चाट",
        "image": "/static/assets/images/thali_meal.jpg",
        "description": "Energizing raw sprout bowl loaded with living enzymes, crunchy onions, juicy tomatoes, fresh lemon juice, and tangy Indian spices.",
        "categories": ["high_protein", "healthy_snacks", "vegetarian", "pre_workout", "balanced_meals"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "8 min",
        "cooking_time": "0 min (No Cook)",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Sprouted Moong Beans",
                "quantity": 80.0,
                "unit": "g",
                "calories": 84.0,
                "protein": 5.6,
                "carbohydrates": 12.8,
                "fat": 1.0,
                "fiber": 3.6,
                "notes": "High bio-availability vitamins"
            },
            {
                "ingredient_name": "Boiled Black Chana (Kala Chana)",
                "quantity": 60.0,
                "unit": "g",
                "calories": 98.4,
                "protein": 5.3,
                "carbohydrates": 16.4,
                "fat": 1.6,
                "fiber": 4.6,
                "notes": "Sustained fiber & protein"
            },
            {
                "ingredient_name": "Diced Red Onion & Tomato",
                "quantity": 50.0,
                "unit": "g",
                "calories": 14.0,
                "protein": 0.5,
                "carbohydrates": 3.0,
                "fat": 0.1,
                "fiber": 0.7,
                "notes": "Crisp vegetables"
            },
            {
                "ingredient_name": "Fresh Lemon Juice & Chaat Masala",
                "quantity": 1.0,
                "unit": "tbsp (15 ml)",
                "calories": 8.0,
                "protein": 0.2,
                "carbohydrates": 1.8,
                "fat": 0.1,
                "fiber": 0.3,
                "notes": "Tangy dressing"
            },
            {
                "ingredient_name": "Chopped Green Coriander & Chillies",
                "quantity": 10.0,
                "unit": "g",
                "calories": 3.0,
                "protein": 0.2,
                "carbohydrates": 0.5,
                "fat": 0.0,
                "fiber": 0.3,
                "notes": "Herbal garnish"
            }
        ],
        "instructions": [
            "In a mixing bowl, combine 80g moong sprouts and 60g boiled black chana.",
            "Add finely chopped onion, tomato, green chillies, and fresh coriander.",
            "Sprinkle 1/2 tsp chaat masala, 1/4 tsp roasted cumin powder, and black salt.",
            "Squeeze 1 tbsp fresh lemon juice generously over the mixture.",
            "Toss vigorously until well coated and enjoy fresh immediately as an active snack."
        ],
        "calories": 207.4,
        "protein": 11.8,
        "carbohydrates": 34.5,
        "fat": 2.8,
        "fiber": 9.5,
        "recommended_for": ["general_fitness", "sports_performance", "improve_strength", "maintain_fitness"]
    },
    {
        "id": "egg_bhurji_roti",
        "name": "Spiced Egg Bhurji with Roti",
        "hindi_name": "अंडा भुर्जी और रोटी",
        "image": "/static/assets/images/chicken_rice_meal.jpg",
        "description": "Desi scrambled eggs whipped with onions, ripe tomatoes, green chillies, and fragrant garam masala, accompanied by 2 whole wheat rotis.",
        "categories": ["high_protein", "breakfast", "dinner", "eggetarian", "post_workout"],
        "dietary_type": "eggetarian",
        "servings": 1,
        "preparation_time": "5 min",
        "cooking_time": "8 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Whole Fresh Eggs (2 large)",
                "quantity": 100.0,
                "unit": "g",
                "calories": 155.0,
                "protein": 13.0,
                "carbohydrates": 1.1,
                "fat": 11.0,
                "fiber": 0.0,
                "notes": "Complete protein with choline"
            },
            {
                "ingredient_name": "Whole Wheat Roti (2 pcs)",
                "quantity": 80.0,
                "unit": "g",
                "calories": 211.2,
                "protein": 7.2,
                "carbohydrates": 41.6,
                "fat": 2.0,
                "fiber": 5.2,
                "notes": "Complex slow-digesting fuel"
            },
            {
                "ingredient_name": "Diced Onion & Tomato",
                "quantity": 60.0,
                "unit": "g",
                "calories": 17.0,
                "protein": 0.6,
                "carbohydrates": 3.7,
                "fat": 0.1,
                "fiber": 0.8,
                "notes": "Flavor base"
            },
            {
                "ingredient_name": "Green Chillies & Coriander",
                "quantity": 10.0,
                "unit": "g",
                "calories": 3.0,
                "protein": 0.2,
                "carbohydrates": 0.5,
                "fat": 0.0,
                "fiber": 0.3,
                "notes": "Zesty herbs"
            },
            {
                "ingredient_name": "Cooking Oil",
                "quantity": 1.0,
                "unit": "tsp (5 ml)",
                "calories": 44.0,
                "protein": 0.0,
                "carbohydrates": 0.0,
                "fat": 5.0,
                "fiber": 0.0,
                "notes": "Pan sautéing"
            },
            {
                "ingredient_name": "Turmeric, Garam Masala & Salt",
                "quantity": 0.5,
                "unit": "tsp (2 g)",
                "calories": 6.0,
                "protein": 0.2,
                "carbohydrates": 0.9,
                "fat": 0.2,
                "fiber": 0.4,
                "notes": "Warm spices"
            }
        ],
        "instructions": [
            "Whisk 2 eggs with a pinch of salt and turmeric in a small bowl.",
            "Heat 1 tsp oil in a pan, sauté chopped onions and green chillies for 2 minutes.",
            "Add chopped tomatoes and garam masala; cook for 1 minute until fragrant.",
            "Pour the beaten eggs into the pan and stir continuously on medium heat for 2 minutes until softly scrambled.",
            "Remove from heat, sprinkle fresh coriander, and serve with 2 warm whole wheat rotis."
        ],
        "calories": 436.2,
        "protein": 21.2,
        "carbohydrates": 47.8,
        "fat": 18.3,
        "fiber": 6.7,
        "recommended_for": ["improve_strength", "sports_performance", "general_fitness"]
    },
    {
        "id": "chicken_rice_bowl",
        "name": "High-Protein Chicken & Rice Bowl",
        "hindi_name": "हाई प्रोटीन चिकन और राइस",
        "image": "/static/assets/images/chicken_rice_meal.jpg",
        "description": "Pan-grilled lean chicken breast seasoned in ginger, garlic, and cracked pepper, served over steamed basmati rice and crisp broccoli florets.",
        "categories": ["high_protein", "lunch", "dinner", "non-vegetarian", "post_workout"],
        "dietary_type": "non-vegetarian",
        "servings": 1,
        "preparation_time": "10 min",
        "cooking_time": "12 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Lean Chicken Breast (Boneless)",
                "quantity": 150.0,
                "unit": "g",
                "calories": 247.5,
                "protein": 46.5,
                "carbohydrates": 0.0,
                "fat": 5.4,
                "fiber": 0.0,
                "notes": "Ultra-lean high-protein meat"
            },
            {
                "ingredient_name": "Steamed White Basmati Rice",
                "quantity": 120.0,
                "unit": "g",
                "calories": 156.0,
                "protein": 3.2,
                "carbohydrates": 33.8,
                "fat": 0.4,
                "fiber": 0.5,
                "notes": "Clean carbohydrate source"
            },
            {
                "ingredient_name": "Steamed Broccoli & Carrot Florets",
                "quantity": 80.0,
                "unit": "g",
                "calories": 28.0,
                "protein": 2.1,
                "carbohydrates": 5.4,
                "fat": 0.3,
                "fiber": 2.4,
                "notes": "Micronutrients & fiber"
            },
            {
                "ingredient_name": "Olive Oil / Mustard Oil",
                "quantity": 1.0,
                "unit": "tsp (5 ml)",
                "calories": 44.0,
                "protein": 0.0,
                "carbohydrates": 0.0,
                "fat": 5.0,
                "fiber": 0.0,
                "notes": "Pan searing"
            },
            {
                "ingredient_name": "Garlic, Ginger, Black Pepper & Salt",
                "quantity": 1.0,
                "unit": "tsp (5 g)",
                "calories": 8.0,
                "protein": 0.3,
                "carbohydrates": 1.6,
                "fat": 0.1,
                "fiber": 0.3,
                "notes": "Aromatic marinade"
            }
        ],
        "instructions": [
            "Cut 150g chicken breast into strips and rub with minced garlic, ginger paste, black pepper, and salt.",
            "Heat 1 tsp olive oil in a grill pan or skillet over medium-high heat.",
            "Cook chicken strips for 4-5 minutes per side until nicely browned and cooked through (internal temp 75°C).",
            "Steam 80g broccoli and carrots for 3-4 minutes until tender-crisp.",
            "Assemble bowl with 120g steamed rice, grilled chicken strips, and steamed veggies."
        ],
        "calories": 483.5,
        "protein": 52.1,
        "carbohydrates": 40.8,
        "fat": 11.2,
        "fiber": 3.2,
        "recommended_for": ["sports_performance", "improve_strength", "general_fitness"]
    },
    {
        "id": "idli_sambar",
        "name": "Steamed Idli with Protein Vegetable Sambar",
        "hindi_name": "इडली और वेजिटेबल सांभर",
        "image": "/static/assets/images/idli_sambar_meal.jpg",
        "description": "Pillowy steamed fermented rice-lentil idlis served with piping hot toor dal sambar enriched with drumstick, pumpkin, and fresh coconut chutney.",
        "categories": ["breakfast", "lunch", "vegetarian", "pre_workout", "balanced_meals"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "10 min",
        "cooking_time": "15 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Steamed Idlis (3 medium pieces)",
                "quantity": 150.0,
                "unit": "g",
                "calories": 210.0,
                "protein": 6.3,
                "carbohydrates": 42.0,
                "fat": 0.8,
                "fiber": 2.3,
                "notes": "Fermented easily digestible carbs"
            },
            {
                "ingredient_name": "Vegetable Toor Dal Sambar",
                "quantity": 180.0,
                "unit": "g",
                "calories": 117.0,
                "protein": 5.0,
                "carbohydrates": 18.9,
                "fat": 2.5,
                "fiber": 4.0,
                "notes": "Lentil broth with vegetables"
            },
            {
                "ingredient_name": "Fresh Coconut Mint Chutney",
                "quantity": 30.0,
                "unit": "g",
                "calories": 55.0,
                "protein": 0.8,
                "carbohydrates": 2.1,
                "fat": 5.1,
                "fiber": 1.2,
                "notes": "Healthy MCT fats"
            }
        ],
        "instructions": [
            "Steam 3 idlis in an idli steamer for 10-12 minutes until soft and fluffy.",
            "Simmer 180g prepared toor dal sambar with drumstick and tomatoes for 5 minutes.",
            "Grind 2 tbsp grated fresh coconut with mint leaves, green chilli, and roasted gram for chutney.",
            "Serve hot idlis dipped in steaming sambar with coconut chutney on the side."
        ],
        "calories": 382.0,
        "protein": 12.1,
        "carbohydrates": 63.0,
        "fat": 8.4,
        "fiber": 7.5,
        "recommended_for": ["general_fitness", "improve_endurance", "maintain_fitness"]
    },
    {
        "id": "vegetable_oats_dosa",
        "name": "Crispy Vegetable Oats Dosa",
        "hindi_name": "ओट्स वेजिटेबल डोसा",
        "image": "/static/assets/images/masala_dosa_meal.jpg",
        "description": "Crispy golden crepe prepared with ground oats and urad dal, topped with grated carrots, bell peppers, and served with cool coriander yogurt dip.",
        "categories": ["breakfast", "dinner", "vegetarian", "balanced_meals"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "10 min",
        "cooking_time": "8 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Oats & Urad Dal Dosa (1 large)",
                "quantity": 140.0,
                "unit": "g",
                "calories": 245.0,
                "protein": 7.5,
                "carbohydrates": 39.2,
                "fat": 6.8,
                "fiber": 4.2,
                "notes": "Crispy wholesome crepe"
            },
            {
                "ingredient_name": "Grated Carrots, Capsicum & Onion",
                "quantity": 60.0,
                "unit": "g",
                "calories": 19.0,
                "protein": 0.7,
                "carbohydrates": 4.0,
                "fat": 0.2,
                "fiber": 1.5,
                "notes": "Vegetable topping"
            },
            {
                "ingredient_name": "Mint-Coriander Yogurt Dip",
                "quantity": 40.0,
                "unit": "g",
                "calories": 28.0,
                "protein": 1.6,
                "carbohydrates": 2.4,
                "fat": 1.4,
                "fiber": 0.4,
                "notes": "Refreshing side"
            },
            {
                "ingredient_name": "Oil for Roasting",
                "quantity": 1.0,
                "unit": "tsp (5 ml)",
                "calories": 44.0,
                "protein": 0.0,
                "carbohydrates": 0.0,
                "fat": 5.0,
                "fiber": 0.0,
                "notes": "Crispy finish"
            }
        ],
        "instructions": [
            "Blend 50g powdered oats with 20g rice flour, 2 tbsp curd, salt, and water to make a thin pouring batter.",
            "Heat a seasoned cast-iron or non-stick tawa on high heat, then reduce to medium.",
            "Pour batter from outside in to form a lacy crepe.",
            "Sprinkle 60g finely grated carrots, capsicum, and onions over the wet surface.",
            "Drizzle 1 tsp oil around edges, cook until crisp and golden brown (3-4 minutes).",
            "Fold in half and serve hot with yogurt mint dip."
        ],
        "calories": 336.0,
        "protein": 9.8,
        "carbohydrates": 45.6,
        "fat": 13.4,
        "fiber": 6.1,
        "recommended_for": ["general_fitness", "maintain_fitness"]
    },
    {
        "id": "hung_curd_fruit_bowl",
        "name": "Greek/Hung Curd & Fruit Power Bowl",
        "hindi_name": "हंग कर्ड फ्रूट पावर बाउल",
        "image": "/static/assets/images/poha_curd_meal.jpg",
        "description": "Velvety thick hung dahi layered with sliced banana, crisp apples, soaked chia seeds, and a golden drizzle of raw honey.",
        "categories": ["high_protein", "breakfast", "pre_workout", "healthy_snacks", "vegetarian"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "5 min",
        "cooking_time": "0 min (No Cook)",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Thick Hung Curd / Greek-Style Dahi",
                "quantity": 150.0,
                "unit": "g",
                "calories": 120.0,
                "protein": 12.0,
                "carbohydrates": 6.0,
                "fat": 5.2,
                "fiber": 0.0,
                "notes": "Concentrated dairy protein"
            },
            {
                "ingredient_name": "Sliced Fresh Banana (1 medium)",
                "quantity": 100.0,
                "unit": "g",
                "calories": 89.0,
                "protein": 1.1,
                "carbohydrates": 22.8,
                "fat": 0.3,
                "fiber": 2.6,
                "notes": "Potassium & fast glycogen"
            },
            {
                "ingredient_name": "Diced Fresh Crisp Apple",
                "quantity": 60.0,
                "unit": "g",
                "calories": 31.2,
                "protein": 0.2,
                "carbohydrates": 8.3,
                "fat": 0.1,
                "fiber": 1.4,
                "notes": "Pectin fiber & crunch"
            },
            {
                "ingredient_name": "Raw Chia Seeds",
                "quantity": 1.0,
                "unit": "tsp (5 g)",
                "calories": 24.3,
                "protein": 0.9,
                "carbohydrates": 2.1,
                "fat": 1.5,
                "fiber": 1.7,
                "notes": "Plant omega-3 alpha-linolenic acid"
            },
            {
                "ingredient_name": "Raw Forest Honey",
                "quantity": 1.0,
                "unit": "tsp (7 g)",
                "calories": 21.0,
                "protein": 0.0,
                "carbohydrates": 5.8,
                "fat": 0.0,
                "fiber": 0.0,
                "notes": "Natural unrefined sweetener"
            }
        ],
        "instructions": [
            "Spoon 150g thick chilled hung curd into your breakfast bowl.",
            "Arrange sliced banana and diced apple neatly over the yogurt base.",
            "Scatter 1 tsp chia seeds evenly across the fruit.",
            "Drizzle 1 tsp pure honey in a zigzag pattern over the bowl.",
            "Serve immediately as a pre-workout fuel or refreshing breakfast."
        ],
        "calories": 285.5,
        "protein": 14.2,
        "carbohydrates": 45.0,
        "fat": 7.1,
        "fiber": 5.7,
        "recommended_for": ["general_fitness", "sports_performance", "maintain_fitness"]
    },
    {
        "id": "chana_masala_bowl",
        "name": "Chana Masala Protein Rice Bowl",
        "hindi_name": "चना मसाला राइस बाउल",
        "image": "/static/assets/images/rajma_chawal_meal.jpg",
        "description": "Tender white chickpeas stewed in an aromatic onion, tomato, and pomegranate-amchur masala, served over steamed basmati rice with cucumber salad.",
        "categories": ["high_protein", "lunch", "dinner", "vegetarian", "balanced_meals"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "10 min",
        "cooking_time": "20 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Cooked White Chickpeas (Kabuli Chana)",
                "quantity": 160.0,
                "unit": "g",
                "calories": 248.0,
                "protein": 12.8,
                "carbohydrates": 33.6,
                "fat": 7.2,
                "fiber": 9.6,
                "notes": "Fiber & iron dense legume"
            },
            {
                "ingredient_name": "Cooked Basmati Rice",
                "quantity": 120.0,
                "unit": "g",
                "calories": 156.0,
                "protein": 3.2,
                "carbohydrates": 33.8,
                "fat": 0.4,
                "fiber": 0.5,
                "notes": "Clean grain pairing"
            },
            {
                "ingredient_name": "Onion-Tomato Spiced Masala Gravy",
                "quantity": 50.0,
                "unit": "g",
                "calories": 42.0,
                "protein": 1.1,
                "carbohydrates": 4.8,
                "fat": 2.2,
                "fiber": 1.2,
                "notes": "Aromatic curry base"
            },
            {
                "ingredient_name": "Fresh Sliced Cucumber & Onion Salad",
                "quantity": 50.0,
                "unit": "g",
                "calories": 12.0,
                "protein": 0.4,
                "carbohydrates": 2.5,
                "fat": 0.1,
                "fiber": 0.7,
                "notes": "Cooling salad"
            }
        ],
        "instructions": [
            "Boil 60g dry chickpeas with a tea bag, bay leaf, and salt until tender.",
            "Heat 1 tsp oil, sauté ginger-garlic paste and onions until golden.",
            "Add tomato puree, chole masala, coriander powder, and amchur; cook until oil separates.",
            "Add boiled chana with cooking broth; simmer on medium flame for 10 minutes until thick.",
            "Serve over 120g warm cooked rice with fresh cucumber slices."
        ],
        "calories": 458.0,
        "protein": 17.5,
        "carbohydrates": 74.7,
        "fat": 9.9,
        "fiber": 12.0,
        "recommended_for": ["general_fitness", "improve_strength", "sports_performance"]
    },
    {
        "id": "soya_chunks_stirfry",
        "name": "High-Fiber Soya Chunks Stir-Fry with Roti",
        "hindi_name": "सोया चंक्स भुर्जी और रोटी",
        "image": "/static/assets/images/thali_meal.jpg",
        "description": "High-protein plant meal made with juicy rehydrated soya chunks stir-fried with bell peppers, onions, ginger, and cumin, served with 2 wheat rotis.",
        "categories": ["high_protein", "lunch", "dinner", "vegetarian", "post_workout"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "10 min",
        "cooking_time": "12 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Soya Chunks (Boiled & Squeezed)",
                "quantity": 120.0,
                "unit": "g",
                "calories": 175.0,
                "protein": 24.0,
                "carbohydrates": 14.0,
                "fat": 0.8,
                "fiber": 6.2,
                "notes": "52% protein density dry weight"
            },
            {
                "ingredient_name": "Sliced Bell Peppers & Onions",
                "quantity": 80.0,
                "unit": "g",
                "calories": 25.0,
                "protein": 1.1,
                "carbohydrates": 5.2,
                "fat": 0.2,
                "fiber": 1.8,
                "notes": "Crunch & Vitamin C"
            },
            {
                "ingredient_name": "Whole Wheat Roti (2 pcs)",
                "quantity": 80.0,
                "unit": "g",
                "calories": 211.2,
                "protein": 7.2,
                "carbohydrates": 41.6,
                "fat": 2.0,
                "fiber": 5.2,
                "notes": "Whole grain carbs"
            },
            {
                "ingredient_name": "Mustard Oil & Ginger-Garlic Masala",
                "quantity": 1.0,
                "unit": "tsp (6 g)",
                "calories": 48.0,
                "protein": 0.3,
                "carbohydrates": 1.2,
                "fat": 5.0,
                "fiber": 0.3,
                "notes": "Aromatic cooking oil"
            }
        ],
        "instructions": [
            "Boil 45g dry soya chunks in salted water for 5 minutes; rinse in cold water and squeeze out all excess moisture thoroughly.",
            "Roughly chop the squeezed soya chunks.",
            "Heat 1 tsp mustard oil in a kadai; add cumin seeds, sliced onions, and ginger-garlic paste.",
            "Add bell peppers, turmeric, chilli powder, and garam masala; sauté on high flame for 2 minutes.",
            "Add chopped soya chunks, 2 tbsp water, and stir-fry for 4-5 minutes until flavors coat evenly.",
            "Serve hot with 2 fresh whole wheat rotis."
        ],
        "calories": 459.2,
        "protein": 32.6,
        "carbohydrates": 62.0,
        "fat": 8.0,
        "fiber": 13.5,
        "recommended_for": ["improve_strength", "sports_performance", "general_fitness"]
    },
    {
        "id": "rajma_masala_jeera_rice",
        "name": "Rajma Masala & Jeera Rice",
        "hindi_name": "राजमा मसाला और जीरा राइस",
        "image": "/static/assets/images/rajma_chawal_meal.jpg",
        "description": "Slow-cooked Punjabi red kidney beans in rich spiced tomato-onion gravy, paired with aromatic cumin rice and a crisp green salad.",
        "categories": ["lunch", "dinner", "vegetarian", "balanced_meals"],
        "dietary_type": "vegetarian",
        "servings": 1,
        "preparation_time": "15 min",
        "cooking_time": "25 min",
        "difficulty": "Easy",
        "ingredients": [
            {
                "ingredient_name": "Cooked Red Kidney Beans (Rajma)",
                "quantity": 160.0,
                "unit": "g",
                "calories": 224.0,
                "protein": 12.0,
                "carbohydrates": 31.2,
                "fat": 6.4,
                "fiber": 8.3,
                "notes": "Classic Punjabi protein staple"
            },
            {
                "ingredient_name": "Cooked Jeera Rice",
                "quantity": 140.0,
                "unit": "g",
                "calories": 185.0,
                "protein": 3.8,
                "carbohydrates": 39.5,
                "fat": 1.5,
                "fiber": 0.8,
                "notes": "Basmati rice tempered with cumin"
            },
            {
                "ingredient_name": "Onion-Tomato Spiced Gravy",
                "quantity": 50.0,
                "unit": "g",
                "calories": 42.0,
                "protein": 1.1,
                "carbohydrates": 4.8,
                "fat": 2.2,
                "fiber": 1.2,
                "notes": "Rich homestyle masala"
            },
            {
                "ingredient_name": "Green Salad with Lemon",
                "quantity": 40.0,
                "unit": "g",
                "calories": 10.0,
                "protein": 0.4,
                "carbohydrates": 2.0,
                "fat": 0.1,
                "fiber": 0.6,
                "notes": "Fresh radish, onion & cucumber"
            }
        ],
        "instructions": [
            "Soak 60g dry rajma overnight and pressure cook with 2 cups water and salt for 5-6 whistles until melt-in-mouth tender.",
            "Heat 1 tsp oil in a pan; sauté finely chopped onions until golden brown.",
            "Add ginger-garlic paste, pureed tomatoes, rajma masala powder, and turmeric; cook until oil glazes.",
            "Add boiled rajma with broth; lightly mash a few beans with the ladle back to thicken gravy.",
            "Simmer for 10-12 minutes on low flame until rich and creamy.",
            "Serve hot over 140g jeera rice with lemon wedges and fresh onions."
        ],
        "calories": 461.0,
        "protein": 17.3,
        "carbohydrates": 77.5,
        "fat": 10.2,
        "fiber": 10.9,
        "recommended_for": ["general_fitness", "improve_endurance", "maintain_fitness"]
    }
]


def init_db():
    """Initialize SQLite tables for NutriLens AI"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        gender TEXT,
        height_cm REAL,
        weight_kg REAL,
        activity_level TEXT,
        fitness_objective TEXT,
        dietary_preference TEXT,
        target_calories REAL,
        target_protein REAL,
        created_at TEXT
    )
    """)

    # Meals Log Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meal_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        meal_name TEXT,
        meal_type TEXT,
        timestamp TEXT,
        calories REAL,
        protein REAL,
        carbs REAL,
        fat REAL,
        fiber REAL,
        meal_fit_score INTEGER,
        items_json TEXT,
        personalized_insight TEXT
    )
    """)

    # Food Items Catalog Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_catalog (
        id TEXT PRIMARY KEY,
        name TEXT,
        hindi_name TEXT,
        category TEXT,
        calories_per_100g REAL,
        protein_per_100g REAL,
        carbs_per_100g REAL,
        fat_per_100g REAL,
        fiber_per_100g REAL,
        default_serving_grams REAL,
        default_serving_unit TEXT,
        portion_options_json TEXT
    )
    """)

    # Recipes Table for Healthy Food Menu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recipes (
        id TEXT PRIMARY KEY,
        name TEXT,
        hindi_name TEXT,
        image TEXT,
        description TEXT,
        categories_json TEXT,
        dietary_type TEXT,
        servings INTEGER,
        preparation_time TEXT,
        cooking_time TEXT,
        difficulty TEXT,
        ingredients_json TEXT,
        instructions_json TEXT,
        calories REAL,
        protein REAL,
        carbohydrates REAL,
        fat REAL,
        fiber REAL,
        recommended_for_json TEXT
    )
    """)

    # Seed default user if not exists
    cursor.execute("SELECT id FROM users WHERE id = 'default_user'")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO users (id, name, age, gender, height_cm, weight_kg, activity_level, fitness_objective, dietary_preference, target_calories, target_protein, created_at)
        VALUES ('default_user', 'Aarav Sharma', 21, 'male', 175.0, 68.0, 'moderate', 'general_fitness', 'vegetarian', 2200.0, 75.0, ?)
        """, (datetime.now().isoformat(),))

    # Seed Indian food catalog
    for item in INDIAN_FOODS_DATA:
        cursor.execute("""
        INSERT OR REPLACE INTO food_catalog 
        (id, name, hindi_name, category, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, fiber_per_100g, default_serving_grams, default_serving_unit, portion_options_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["id"],
            item["name"],
            item["hindi_name"],
            item["category"],
            item["calories_per_100g"],
            item["protein_per_100g"],
            item["carbs_per_100g"],
            item["fat_per_100g"],
            item["fiber_per_100g"],
            item["default_serving_grams"],
            item["default_serving_unit"],
            json.dumps(item["portion_options"])
        ))

    # Seed Healthy Recipes catalog
    for r in INDIAN_RECIPES_DATA:
        cursor.execute("""
        INSERT OR REPLACE INTO recipes
        (id, name, hindi_name, image, description, categories_json, dietary_type, servings, preparation_time, cooking_time, difficulty, ingredients_json, instructions_json, calories, protein, carbohydrates, fat, fiber, recommended_for_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["id"],
            r["name"],
            r.get("hindi_name", ""),
            r["image"],
            r["description"],
            json.dumps(r["categories"]),
            r["dietary_type"],
            r.get("servings", 1),
            r["preparation_time"],
            r["cooking_time"],
            r["difficulty"],
            json.dumps(r["ingredients"]),
            json.dumps(r["instructions"]),
            r["calories"],
            r["protein"],
            r["carbohydrates"],
            r["fat"],
            r["fiber"],
            json.dumps(r.get("recommended_for", []))
        ))

    conn.commit()
    conn.close()


def get_user_profile(user_id: str = "default_user") -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, gender, height_cm, weight_kg, activity_level, fitness_objective, dietary_preference, target_calories, target_protein FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "name": row[1],
            "age": row[2],
            "gender": row[3],
            "height_cm": row[4],
            "weight_kg": row[5],
            "activity_level": row[6],
            "fitness_objective": row[7],
            "dietary_preference": row[8],
            "target_calories": row[9] or 2200.0,
            "target_protein": row[10] or 75.0,
        }
    return {
        "id": "default_user",
        "name": "Aarav Sharma",
        "age": 21,
        "gender": "male",
        "height_cm": 175.0,
        "weight_kg": 68.0,
        "activity_level": "moderate",
        "fitness_objective": "general_fitness",
        "dietary_preference": "vegetarian",
        "target_calories": 2200.0,
        "target_protein": 75.0,
    }


def save_user_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    user_id = data.get("id", "default_user")
    
    # Calculate estimated targets based on Mifflin-St Jeor equation if not provided
    weight = float(data.get("weight_kg", 68.0))
    height = float(data.get("height_cm", 175.0))
    age = int(data.get("age", 21))
    gender = data.get("gender", "male")
    activity = data.get("activity_level", "moderate")
    objective = data.get("fitness_objective", "general_fitness")

    # BMR
    if gender == "female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

    # Activity Multiplier
    multipliers = {"low": 1.2, "light": 1.375, "moderate": 1.55, "high": 1.725}
    act_mult = multipliers.get(activity, 1.4)
    tdee = bmr * act_mult

    # Adjust for objective
    if objective == "improve_strength":
        target_cal = round(tdee + 250, 0)
        target_prot = round(weight * 1.8, 1)
    elif objective == "improve_endurance":
        target_cal = round(tdee + 150, 0)
        target_prot = round(weight * 1.5, 1)
    elif objective == "sports_performance":
        target_cal = round(tdee + 300, 0)
        target_prot = round(weight * 1.7, 1)
    elif objective == "maintain_fitness":
        target_cal = round(tdee, 0)
        target_prot = round(weight * 1.2, 1)
    else:  # general_fitness
        target_cal = round(tdee, 0)
        target_prot = round(weight * 1.3, 1)

    data["target_calories"] = target_cal
    data["target_protein"] = target_prot

    cursor.execute("""
    INSERT OR REPLACE INTO users 
    (id, name, age, gender, height_cm, weight_kg, activity_level, fitness_objective, dietary_preference, target_calories, target_protein, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        data.get("name", "User"),
        age,
        gender,
        height,
        weight,
        activity,
        objective,
        data.get("dietary_preference", "vegetarian"),
        target_cal,
        target_prot,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    return get_user_profile(user_id)


def get_all_foods() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, hindi_name, category, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, fiber_per_100g, default_serving_grams, default_serving_unit, portion_options_json FROM food_catalog")
    rows = cursor.fetchall()
    conn.close()

    foods = []
    for r in rows:
        foods.append({
            "id": r[0],
            "name": r[1],
            "hindi_name": r[2],
            "category": r[3],
            "calories_per_100g": r[4],
            "protein_per_100g": r[5],
            "carbs_per_100g": r[6],
            "fat_per_100g": r[7],
            "fiber_per_100g": r[8],
            "default_serving_grams": r[9],
            "default_serving_unit": r[10],
            "portion_options": json.loads(r[11]) if r[11] else {}
        })
    return foods


def get_food_by_id(food_id: str) -> Optional[Dict[str, Any]]:
    foods = get_all_foods()
    for f in foods:
        if f["id"] == food_id:
            return f
    return None


def save_meal_log(user_id: str, meal_data: Dict[str, Any]) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO meal_logs 
    (user_id, meal_name, meal_type, timestamp, calories, protein, carbs, fat, fiber, meal_fit_score, items_json, personalized_insight)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        meal_data.get("meal_name", "Meal"),
        meal_data.get("meal_type", "lunch"),
        meal_data.get("timestamp", datetime.now().isoformat()),
        float(meal_data.get("calories", 0.0)),
        float(meal_data.get("protein", 0.0)),
        float(meal_data.get("carbs", 0.0)),
        float(meal_data.get("fat", 0.0)),
        float(meal_data.get("fiber", 0.0)),
        int(meal_data.get("meal_fit_score", 75)),
        json.dumps(meal_data.get("items", [])),
        meal_data.get("personalized_insight", "")
    ))
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def get_today_meal_logs(user_id: str = "default_user") -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    SELECT id, user_id, meal_name, meal_type, timestamp, calories, protein, carbs, fat, fiber, meal_fit_score, items_json, personalized_insight
    FROM meal_logs
    WHERE user_id = ? AND timestamp LIKE ?
    ORDER BY id ASC
    """, (user_id, f"{today_str}%"))
    
    rows = cursor.fetchall()
    conn.close()

    logs = []
    for r in rows:
        logs.append({
            "id": r[0],
            "user_id": r[1],
            "meal_name": r[2],
            "meal_type": r[3],
            "timestamp": r[4],
            "calories": r[5],
            "protein": r[6],
            "carbs": r[7],
            "fat": r[8],
            "fiber": r[9],
            "meal_fit_score": r[10],
            "items": json.loads(r[11]) if r[11] else [],
            "personalized_insight": r[12]
        })
    return logs


def clear_today_meals(user_id: str = "default_user"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("DELETE FROM meal_logs WHERE user_id = ? AND timestamp LIKE ?", (user_id, f"{today_str}%"))
    conn.commit()
    conn.close()


def get_all_recipes(
    category: Optional[str] = None,
    dietary_type: Optional[str] = None,
    search: Optional[str] = None,
    fitness_objective: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves all healthy food menu recipes with optional filtering by category,
    dietary preference, full-text search, and personal fitness objective matching.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, name, hindi_name, image, description, categories_json, dietary_type, servings, preparation_time, cooking_time, difficulty, ingredients_json, instructions_json, calories, protein, carbohydrates, fat, fiber, recommended_for_json
    FROM recipes
    """)
    rows = cursor.fetchall()
    conn.close()

    recipes = []
    for r in rows:
        categories = json.loads(r[5]) if r[5] else []
        ingredients = json.loads(r[11]) if r[11] else []
        instructions = json.loads(r[12]) if r[12] else []
        recommended_for = json.loads(r[18]) if r[18] else []

        recipe_item = {
            "id": r[0],
            "name": r[1],
            "hindi_name": r[2],
            "image": r[3],
            "description": r[4],
            "categories": categories,
            "dietary_type": r[6],
            "servings": r[7] or 1,
            "preparation_time": r[8],
            "cooking_time": r[9],
            "difficulty": r[10],
            "ingredients": ingredients,
            "instructions": instructions,
            "calories": round(r[13], 1),
            "protein": round(r[14], 1),
            "carbohydrates": round(r[15], 1),
            "fat": round(r[16], 1),
            "fiber": round(r[17], 1),
            "recommended_for": recommended_for,
            "is_recommended": False,
            "disclaimer": "Estimated nutritional values. Values may vary depending on ingredients, brands, and preparation methods."
        }

        # Check fitness objective recommendation
        if fitness_objective and fitness_objective in recommended_for:
            recipe_item["is_recommended"] = True

        # Category filter (e.g. high_protein, pre_workout, breakfast, etc.)
        if category and category != "all":
            if category == "recommended":
                if not recipe_item["is_recommended"]:
                    continue
            elif category not in categories:
                continue

        # Dietary type filter
        if dietary_type and dietary_type != "all":
            if recipe_item["dietary_type"] != dietary_type:
                continue

        # Text search (recipe name, hindi name, description, ingredients)
        if search:
            query = search.strip().lower()
            name_match = query in recipe_item["name"].lower()
            hindi_match = query in recipe_item.get("hindi_name", "").lower()
            desc_match = query in recipe_item["description"].lower()
            cat_match = any(query in c.lower() for c in categories)
            ing_match = any(query in ing.get("ingredient_name", "").lower() for ing in ingredients)

            if not (name_match or hindi_match or desc_match or cat_match or ing_match):
                continue

        recipes.append(recipe_item)

    return recipes


def get_recipe_by_id(recipe_id: str, fitness_objective: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves a single recipe with full ingredient measurements and step-by-step cooking steps"""
    recipes = get_all_recipes(fitness_objective=fitness_objective)
    for r in recipes:
        if r["id"] == recipe_id:
            return r
    return None


# Initialize SQLite database immediately upon import
init_db()

