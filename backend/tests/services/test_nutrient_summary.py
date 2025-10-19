from nutrient_summary import calculate_nutrient_summary

def main():
    # Example API response to test the function
    api_response = {
        "success": True,
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
                {
                    "food": "Small Roasted Potatoes",
                    "quantity": 150,
                    "per_portion": {
                        "nutritional_values": {
                            "energy_kcal": 150,
                            "proteins_g": 3.8,
                            "carbohydrates_g": 30,
                            "lipids_g": 3,
                            "fiber_g": 3.8,
                            "sugars_g": 2.3,
                            "saturated_fats_g": 0.5,
                            "unsaturated_fats_g": 2.3
                        },
                        "micronutrients": {
                            "calcium_mg": 12,
                            "iron_mg": 1.1,
                            "magnesium_mg": 33,
                            "potassium_mg": 600,
                            "sodium_mg": 12,
                            "zinc_mg": 0.4,
                            "phosphorus_mg": 82.5
                        }
                    }
                }
            ]
        },
        "message": "Nutrient analysis successful."
    }

    # Call the function and print the result
    result = calculate_nutrient_summary(api_response)
    print("Nutrient Summary:")
    print(result)

if __name__ == "__main__":
    main()