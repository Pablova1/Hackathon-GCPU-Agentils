def calculate_nutrient_summary(api_response):
    """
    Calculate the sum of nutritional values for a dish based on the API response.
    
    Args:
        api_response (dict): The response from the nutrient analysis API.
        Can be either:
        - Direct response: {'foods_nutrition': [...]}
        - Wrapped response: {'nutrients': {'foods_nutrition': [...]}}
    
    Returns:
        dict: A JSON object containing the summed nutritional values.
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
    
    combined_food_names = []
    
    
    # Gérer les deux formats possibles
    # Format 1: {'nutrients': {'foods_nutrition': [...]}}
    # Format 2: {'foods_nutrition': [...]}
    if "nutrients" in api_response:
        foods_list = api_response.get("nutrients", {}).get("foods_nutrition", [])
    else:
        foods_list = api_response.get("foods_nutrition", [])
    
    
    # Parcourir les aliments
    for food in foods_list:
        per_portion = food.get("per_portion", {})
        nutritional_values = per_portion.get("nutritional_values", {})
        micronutrients = per_portion.get("micronutrients", {})
        
        
        # Additionner les valeurs nutritionnelles
        for key in total_nutritional_values:
            value = nutritional_values.get(key, 0)
            total_nutritional_values[key] += value
        
        # Additionner les micronutriments
        for key in total_micronutrients:
            value = micronutrients.get(key, 0)
            total_micronutrients[key] += value
        
        # Ajouter le nom de l'aliment
        food_name = food.get("food", "").strip()
        if food_name:
            combined_food_names.append(food_name)
    
    
    return {
        "name": ", ".join(combined_food_names),
        "nutritional_values": total_nutritional_values,
        "micronutrients": total_micronutrients
    }