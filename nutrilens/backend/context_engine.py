"""
NutriLens AI - Personal Context Engine
The central intelligence module that transforms raw nutrition into personalized,
explainable, fitness-oriented insights based on individual user context.
"""

from typing import List, Dict, Any, Optional
from models import (
    UserProfile,
    DetectedFood,
    MealFitScoreBreakdown,
    PlateGapAnalysis,
    PlateGapIndicator,
    MealAnalysisResult
)


class PersonalContextEngine:
    """
    Algorithmic intelligence engine mapping:
    (Meal Nutrition + Composition + Portions) + (User Profile + Activity + Goal + Today's History)
    --> (Meal Fit Score + Explainable Factors + PlateGap Analysis + Contextual Insight)
    """

    @staticmethod
    def analyze(
        items: List[DetectedFood],
        profile: UserProfile,
        meal_name: str = "Scanned Meal",
        meal_type: str = "lunch",
        today_meals: Optional[List[Dict[str, Any]]] = None
    ) -> MealAnalysisResult:
        if today_meals is None:
            today_meals = []

        # 1. Calculate Meal Aggregate Macros
        total_calories = sum(item.calories for item in items)
        total_protein = sum(item.protein for item in items)
        total_carbs = sum(item.carbs for item in items)
        total_fat = sum(item.fat for item in items)
        total_fiber = sum(item.fiber for item in items)

        # 2. Cumulative Today Macros
        today_logged_cal = sum(m.get("calories", 0.0) for m in today_meals)
        today_logged_prot = sum(m.get("protein", 0.0) for m in today_meals)
        today_logged_carbs = sum(m.get("carbs", 0.0) for m in today_meals)
        today_logged_fat = sum(m.get("fat", 0.0) for m in today_meals)

        # Profile Targets
        weight = profile.weight_kg or 68.0
        target_cal = profile.target_calories or 2200.0
        target_prot = profile.target_protein or (weight * 1.3)
        activity = profile.activity_level.lower()
        objective = profile.fitness_objective.lower()

        # Macro Calorie Contributions (Prot: 4 kcal/g, Carbs: 4 kcal/g, Fat: 9 kcal/g)
        meal_cal_from_prot = total_protein * 4.0
        meal_cal_from_carbs = total_carbs * 4.0
        meal_cal_from_fat = total_fat * 9.0
        effective_cal = max(total_calories, 1.0)

        prot_pct = (meal_cal_from_prot / effective_cal) * 100.0
        carb_pct = (meal_cal_from_carbs / effective_cal) * 100.0
        fat_pct = (meal_cal_from_fat / effective_cal) * 100.0

        # Check Food Group Categories present
        item_names = [it.name.lower() for it in items]
        has_legume_or_dairy = any("dal" in n or "paneer" in n or "rajma" in n or "chana" in n or "curd" in n or "dahi" in n for n in item_names)
        has_meat_or_egg = any("chicken" in n or "egg" in n for n in item_names)
        has_veggies_or_salad = any("sabzi" in n or "salad" in n or "sambar" in n or "bhindi" in n or "gobi" in n for n in item_names)
        has_grains = any("roti" in n or "rice" in n or "poha" in n or "idli" in n or "dosa" in n or "upma" in n for n in item_names)
        has_fruit = any("banana" in n or "apple" in n for n in item_names)

        # -------------------------------------------------------------
        # Factor A: Base Nutritional Balance Score (Max 30 pts)
        # -------------------------------------------------------------
        base_score = 20.0
        positive_factors = []
        areas_to_consider = []

        # Diversity check
        group_count = sum([has_grains, (has_legume_or_dairy or has_meat_or_egg), has_veggies_or_salad, has_fruit])
        if group_count >= 3:
            base_score += 6.0
            positive_factors.append("Includes balanced representation from multiple food groups (grains, proteins, vegetables/fruits).")
        elif group_count == 2:
            base_score += 3.0
        else:
            areas_to_consider.append("Meal variety is concentrated in one primary food group.")

        # Fiber presence
        if total_fiber >= 4.5:
            base_score += 4.0
            positive_factors.append(f"Rich in dietary fiber (~{total_fiber:.1f}g) supporting steady digestion.")
        elif total_fiber < 1.5:
            base_score -= 2.0
            areas_to_consider.append("Fiber content is comparatively low (<1.5g); consider adding a fresh salad or whole vegetable side.")

        # -------------------------------------------------------------
        # Factor B: Goal Alignment Score (Max 30 pts)
        # -------------------------------------------------------------
        goal_score = 20.0

        if objective == "improve_strength":
            # Demands higher protein density (>20g per main meal or >20% prot cal)
            if total_protein >= 25.0:
                goal_score += 10.0
                positive_factors.append(f"Excellent protein supply (~{total_protein:.1f}g) strongly aligned with your strength & muscle recovery objective.")
            elif total_protein >= 16.0:
                goal_score += 5.0
                positive_factors.append(f"Moderate protein content (~{total_protein:.1f}g) supports muscle maintenance.")
            else:
                goal_score -= 6.0
                areas_to_consider.append(f"Protein yield (~{total_protein:.1f}g) is below optimal threshold for muscle hypertrophy goals.")

        elif objective == "sports_performance":
            # Demands glycogen-fueling carbs + solid protein + controlled heavy fats
            if total_carbs >= 40.0 and total_protein >= 18.0:
                goal_score += 10.0
                positive_factors.append("Provides sustained carbohydrate fuel combined with recovery protein suited for athletic output.")
            elif total_carbs >= 30.0:
                goal_score += 6.0
                positive_factors.append("Good carbohydrate base to support training endurance.")
            else:
                goal_score -= 4.0
                areas_to_consider.append("Energy and carbohydrate availability may be modest for high-intensity sports output.")

        elif objective == "improve_endurance":
            # Demands complex carbs, steady energy, hydration/veggies
            if carb_pct >= 50.0 and carb_pct <= 70.0 and total_fiber >= 3.0:
                goal_score += 10.0
                positive_factors.append("Optimal carbohydrate-to-fiber ratio for steady, long-lasting aerobic endurance.")
            else:
                goal_score += 4.0

        elif objective == "maintain_fitness":
            # Demands balanced 45-55% carb, 18-25% prot, 25-30% fat
            if 15.0 <= prot_pct <= 30.0 and 40.0 <= carb_pct <= 65.0:
                goal_score += 9.0
                positive_factors.append("Macronutrient distribution is harmoniously balanced for everyday fitness maintenance.")
            else:
                goal_score += 4.0

        else:  # general_fitness
            if total_protein >= 14.0 and total_calories <= 750:
                goal_score += 8.0
                positive_factors.append("Good portion and protein presence for everyday health and vitality.")
            else:
                goal_score += 4.0

        # -------------------------------------------------------------
        # Factor C: Activity Context Score (Max 25 pts)
        # -------------------------------------------------------------
        act_score = 18.0

        if activity == "high":
            # High activity requires higher caloric allowance and carb replenishment
            if total_calories >= 550:
                act_score += 7.0
                positive_factors.append("Caloric density (~{:.0f} kcal) effectively matches your high daily activity expenditure.".format(total_calories))
            else:
                act_score += 3.0
                areas_to_consider.append("Caloric portion is relatively light for a high-intensity training regimen.")
        elif activity == "moderate":
            if 400 <= total_calories <= 700:
                act_score += 7.0
                positive_factors.append("Portion size is well-calibrated for moderate daily activity.")
            elif total_calories > 850:
                act_score -= 3.0
                areas_to_consider.append("Heavy energy density relative to moderate expenditure.")
            else:
                act_score += 4.0
        elif activity in ["light", "low"]:
            # Sedentary/light activity needs lighter carb/calorie loads
            if total_calories <= 550 and carb_pct <= 60.0:
                act_score += 7.0
                positive_factors.append("Moderate portion size aligns with lower daily metabolic demand.")
            elif total_calories > 750 or carb_pct > 68.0:
                act_score -= 5.0
                areas_to_consider.append("High carbohydrate and calorie load may exceed expenditure for light activity levels.")
            else:
                act_score += 3.0

        # -------------------------------------------------------------
        # Factor D: Daily History Context Score (Max 15 pts)
        # -------------------------------------------------------------
        daily_score = 12.0
        projected_day_cal = today_logged_cal + total_calories
        projected_day_prot = today_logged_prot + total_protein
        projected_day_carbs = today_logged_carbs + total_carbs

        if len(today_meals) > 0:
            # Check if carbs are already high today
            if today_logged_carbs > (target_cal * 0.55 / 4.0) and carb_pct > 65.0:
                daily_score -= 4.0
                areas_to_consider.append(f"Cumulative carbohydrate intake is already elevated ({today_logged_carbs:.0f}g logged today).")
            
            # Check if protein was lacking and this meal helps
            if today_logged_prot < (target_prot * 0.45) and total_protein >= 18.0:
                daily_score += 3.0
                positive_factors.append("Helps bridge a significant protein deficit from earlier meals today.")
            
            # Calorie ceiling check
            if projected_day_cal > (target_cal * 1.15):
                daily_score -= 3.0
                areas_to_consider.append("Pushes projected daily energy intake slightly above estimated maintenance.")
            else:
                daily_score += 2.0
        else:
            # First meal of the day
            positive_factors.append(f"Provides a solid nutritional baseline as today's logged {meal_type}.")

        # -------------------------------------------------------------
        # Factor E: Identified Imbalance Penalties (0 to -15 pts)
        # -------------------------------------------------------------
        penalties = 0.0
        if fat_pct > 45.0:
            penalties += 4.0
            areas_to_consider.append("Fat percentage is on the higher side (>45% of meal calories).")
        if prot_pct < 8.0 and objective in ["improve_strength", "sports_performance"]:
            penalties += 5.0
            areas_to_consider.append("Protein ratio (<8% of calories) is notably low for athletic recovery.")

        # Compute Raw Score
        raw_score = base_score + goal_score + act_score + daily_score - penalties
        total_score = max(10, min(98, int(round(raw_score))))

        # Alignment Category
        if total_score >= 85:
            alignment_category = "Optimal Alignment"
        elif total_score >= 70:
            alignment_category = "Good Alignment"
        elif total_score >= 50:
            alignment_category = "Moderate Alignment"
        else:
            alignment_category = "Needs Adjustment"

        # -------------------------------------------------------------
        # PlateGap AI Analysis
        # -------------------------------------------------------------
        # Target macro percentages based on fitness objective
        if objective == "improve_strength":
            target_prot_pct = 28.0
            target_carb_pct = 45.0
            target_fat_pct = 27.0
        elif objective == "sports_performance":
            target_prot_pct = 22.0
            target_carb_pct = 55.0
            target_fat_pct = 23.0
        elif objective == "improve_endurance":
            target_prot_pct = 18.0
            target_carb_pct = 60.0
            target_fat_pct = 22.0
        else:  # general_fitness & maintain
            target_prot_pct = 20.0
            target_carb_pct = 52.0
            target_fat_pct = 28.0

        # Build indicators
        def get_status(current, target):
            diff = current - target
            if abs(diff) <= 6.0:
                return "optimal", "Well proportioned"
            elif diff < -6.0:
                return "low", f"Below target by {abs(diff):.0f}%"
            else:
                return "high", f"Above target by {diff:.0f}%"

        p_status, p_ins = get_status(prot_pct, target_prot_pct)
        c_status, c_ins = get_status(carb_pct, target_carb_pct)
        f_status, f_ins = get_status(fat_pct, target_fat_pct)

        indicators = [
            PlateGapIndicator(
                macro_name="Protein",
                current_pct=round(prot_pct, 1),
                target_pct=target_prot_pct,
                status=p_status,
                insight=f"Current: {prot_pct:.1f}% vs Target: {target_prot_pct:.0f}% ({p_ins})"
            ),
            PlateGapIndicator(
                macro_name="Carbohydrates",
                current_pct=round(carb_pct, 1),
                target_pct=target_carb_pct,
                status=c_status,
                insight=f"Current: {carb_pct:.1f}% vs Target: {target_carb_pct:.0f}% ({c_ins})"
            ),
            PlateGapIndicator(
                macro_name="Healthy Fats",
                current_pct=round(fat_pct, 1),
                target_pct=target_fat_pct,
                status=f_status,
                insight=f"Current: {fat_pct:.1f}% vs Target: {target_fat_pct:.0f}% ({f_ins})"
            )
        ]

        # Educational Suggestions (strictly non-medical)
        educational_suggestions = []
        if p_status == "low":
            if profile.dietary_preference == "vegetarian":
                educational_suggestions.append("Consider pairing with a katori of curd (dahi), sprouted moong, or paneer to elevate protein density.")
            elif profile.dietary_preference == "vegan":
                educational_suggestions.append("Consider adding roasted chana, soy chunks, or tofu to complement plant protein.")
            else:
                educational_suggestions.append("Adding a boiled egg or lean chicken side can help meet your fitness protein priorities.")
        
        if not has_veggies_or_salad:
            educational_suggestions.append("Adding a simple katori of cucumber-tomato salad or steamed sabzi increases fiber and micronutrient variety.")
        
        if c_status == "high" and activity in ["low", "light"]:
            educational_suggestions.append("Since activity expenditure is lighter today, swapping one portion of refined grains for extra lentils or veggies can balance energy release.")

        if not educational_suggestions:
            educational_suggestions.append("Great plate composition! Continue drinking adequate water and maintaining consistent meal timings.")

        gap_summary = (
            f"Your current meal is {c_status} in carbohydrates ({carb_pct:.0f}%) and {p_status} in protein ({prot_pct:.0f}%) "
            f"relative to your {profile.fitness_objective.replace('_', ' ')} goals."
        )

        plate_gap = PlateGapAnalysis(
            indicators=indicators,
            gap_summary=gap_summary,
            educational_suggestions=educational_suggestions
        )

        # -------------------------------------------------------------
        # Personalized Contextual Insight (Natural Language Summary)
        # -------------------------------------------------------------
        act_phrase = "high physical activity" if activity == "high" else ("moderate routine" if activity == "moderate" else "light daily movement")
        goal_phrase = objective.replace("_", " ")

        if total_score >= 82:
            insight_text = (
                f"This meal fits remarkably well with your {goal_phrase} priorities and {act_phrase}. "
                f"The ~{total_protein:.1f}g of protein and ~{total_calories:.0f} kcal provide sustained energy without creating an extreme macro imbalance."
            )
        elif total_score >= 68:
            insight_text = (
                f"A nourishing meal providing ~{total_calories:.0f} kcal. For your selected goal of {goal_phrase}, "
                f"{'increasing protein slightly' if p_status == 'low' else 'adjusting carbohydrate portions'} would optimize your daily fitness alignment."
            )
        else:
            insight_text = (
                f"While satisfying in energy (~{total_calories:.0f} kcal), the current macro distribution is skewed toward {c_status} carbohydrates "
                f"relative to your {act_phrase} and {goal_phrase} targets. Small tweaks like adding legumes or salad can enhance fit."
            )

        score_breakdown = MealFitScoreBreakdown(
            base_nutrition_score=round(base_score, 1),
            goal_alignment_score=round(goal_score, 1),
            activity_context_score=round(act_score, 1),
            daily_history_context_score=round(daily_score, 1),
            imbalance_penalties=round(penalties, 1),
            total_score=total_score,
            alignment_category=alignment_category
        )

        return MealAnalysisResult(
            meal_name=meal_name,
            meal_type=meal_type,
            total_calories=round(total_calories, 1),
            total_protein=round(total_protein, 1),
            total_carbs=round(total_carbs, 1),
            total_fat=round(total_fat, 1),
            total_fiber=round(total_fiber, 1),
            items=items,
            meal_fit_score=total_score,
            alignment_category=alignment_category,
            score_breakdown=score_breakdown,
            positive_factors=positive_factors,
            areas_to_consider=areas_to_consider,
            plate_gap=plate_gap,
            personalized_insight=insight_text
        )
