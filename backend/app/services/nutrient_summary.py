def calculate_nutrient_summary(api_response):
    """
    Calculate the sum of nutritional values for a dish based on the API response.

    Args:
        api_response (dict): The response from the nutrient analysis API. Expected format:
            {
                "success": true,
                "nutrients": {
                    "foods_nutrition": [
                        {
                            "food": "Beef",
                            "quantity": 190,
                            "per_portion": {
                                "nutritional_values": {
                                    "energy_kcal": 437,
                                    "proteins_g": 53.2,
                                    "carbohydrates_g": 0,
                                    "lipids_g": 22.8,
                                    "fiber_g": 0,
                                    "sugars_g": 0,
                                    "saturated_fats_g": 9.5,
                                    "unsaturated_fats_g": 13.3
                                },
                                "micronutrients": {
                                    "calcium_mg": 28.5,
                                    "iron_mg": 4.8,
                                    "magnesium_mg": 47.5,
                                    "potassium_mg": 665,
                                    "sodium_mg": 114,
                                    "zinc_mg": 9.5,
                                    "phosphorus_mg": 437
                                }
                            }
                        },
                        ...
                    ]
                }
            }

    Returns:
        dict: A JSON object containing the summed nutritional values.
            {
                "name": "Sum of ingredients",
                "nutritional_values": {
                    "energy_kcal": total_kcal,
                    "proteins_g": total_proteins,
                    "carbohydrates_g": total_carbs,
                    "lipids_g": total_fats,
                    "fiber_g": total_fiber,
                    "sugars_g": total_sugars,
                    "saturated_fats_g": total_saturated_fats,
                    "unsaturated_fats_g": total_unsaturated_fats
                },
                "micronutrients": {
                    "calcium_mg": total_calcium,
                    "iron_mg": total_iron,
                    "magnesium_mg": total_magnesium,
                    "potassium_mg": total_potassium,
                    "sodium_mg": total_sodium,
                    "zinc_mg": total_zinc,
                    "phosphorus_mg": total_phosphorus
                }
            }
    """
    total_nutritional_values = {
        "energy_kcal": 0,
        "proteins_g": 0,
        "carbohydrates_g": 0,
        "lipids_g": 0,
        "fiber_g": 0,
        "sugars_g": 0,
        "saturated_fats_g": 0,
        "unsaturated_fats_g": 0
    }

    total_micronutrients = {
        "calcium_mg": 0,
        "iron_mg": 0,
        "magnesium_mg": 0,
        "potassium_mg": 0,
        "sodium_mg": 0,
        "zinc_mg": 0,
        "phosphorus_mg": 0
    }

    combined_food_names = ""

    for food in api_response.get("nutrients", {}).get("foods_nutrition", []):
        nutritional_values = food.get("per_portion", {}).get("nutritional_values", {})
        micronutrients = food.get("per_portion", {}).get("micronutrients", {})

        for key in total_nutritional_values:
            total_nutritional_values[key] += nutritional_values.get(key, 0)

        for key in total_micronutrients:
            total_micronutrients[key] += micronutrients.get(key, 0)

        # Append the food name to the combined string
        combined_food_names += food.get("food", "") + " "

    return {
        "name": combined_food_names.strip(),
        "nutritional_values": total_nutritional_values,
        "micronutrients": total_micronutrients
    }