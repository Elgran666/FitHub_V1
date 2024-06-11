from datetime import datetime
from flask import redirect, session, flash
from functools import wraps

# Constants for validation
MIN_AGE = 14
MAX_AGE = 100
MIN_KG = 30
MAX_KG = 200
MIN_CM = 100
MAX_CM = 250
MIN_LB = 65
MAX_LB = 450
MIN_FT = 3
MAX_FT = 8
MIN_IN = 0
MAX_IN = 11
MIN_TOTAL_IN = 39 # subject to change
MAX_TOTAL_IN = 98 #subject to change


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You must be logged in to view this page.", "warning")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def calculate_age(birthday):
    today = datetime.today()
    birthdate = datetime.strptime(birthday, '%Y-%m-%d')
    age = today.year - birthdate.year - \
        ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

from datetime import datetime
from datetime import datetime

def validate_signup_data(username, password, confirmed_password, birthday, gender, activity_level, unit_system, current_weight_kg, height_cm, current_weight_lb, height_ft, height_in, body_fat_percentage):
    errors = []

    # Check password match
    if password != confirmed_password:
        errors.append("Passwords do not match.")

    # Ensure the unit system is either metric or imperial
    if unit_system not in ["metric", "imperial"]:
        errors.append("Invalid unit system. Must be 'metric' or 'imperial'.")

    # Check required fields based on unit system
    required_fields = [username, password, confirmed_password, birthday, gender, activity_level]
    if unit_system == "metric":
        required_fields.extend([current_weight_kg, height_cm])
    elif unit_system == "imperial":
        required_fields.extend([current_weight_lb, height_ft])

    if not all(required_fields):
        errors.append("All fields are required.")

    # Age validation
    try:
        birthday_date = datetime.strptime(birthday, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birthday_date.year - ((today.month, today.day) < (birthday_date.month, birthday_date.day))
        if age < MIN_AGE:
            errors.append(f"You must be at least {MIN_AGE} years old to sign up.")
        if age > MAX_AGE:
            errors.append(f"You cannot be more than {MAX_AGE} years old to sign up.")
    except ValueError:
        errors.append("Invalid date format. Please enter your birthday as YYYY-MM-DD.")

    # Validate weights and heights based on unit system
    if unit_system == "metric":
        try:
            current_weight_kg = float(current_weight_kg)
            height_cm = float(height_cm)
            if not (MIN_KG <= current_weight_kg <= MAX_KG):
                errors.append(f"Weight must be between {MIN_KG} kg and {MAX_KG} kg.")
            if not (MIN_CM <= height_cm <= MAX_CM):
                errors.append(f"Height must be between {MIN_CM} cm and {MAX_CM} cm.")
        except (TypeError, ValueError):
            errors.append("Weight and height must be numbers.")
    elif unit_system == "imperial":
        try:
            current_weight_lb = float(current_weight_lb)
            height_ft = float(height_ft)
            height_in = float(height_in)
            if not (MIN_LB <= current_weight_lb <= MAX_LB):
                errors.append(f"Weight must be between {MIN_LB} lb and {MAX_LB} lb.")
            if not (MIN_FT <= height_ft <= MAX_FT):
                errors.append(f"Height feet value must be between {MIN_FT} ft and {MAX_FT} ft.")
            if not (MIN_IN <= height_in <= MAX_IN):
                errors.append(f"Height inches value must be between {MIN_IN} in and {MAX_IN} in.")
        except (TypeError, ValueError):
            errors.append("Weight and height must be numbers.")

    # Validate body fat percentage if provided
    if body_fat_percentage is not None:
        try:
            body_fat_percentage = float(body_fat_percentage)
            if not (0 <= body_fat_percentage <= 100):
                errors.append("Body fat percentage must be between 0 and 100.")
        except (TypeError, ValueError):
            errors.append("Body fat percentage must be a number.")

    return errors


def validate_caloriehub_input(unit_system, weight_kg, weight_lb, height_cm, height_ft, height_in, age, gender, activity_level, body_fat_percentage):
    # Define valid activity levels for validation
    VALID_ACTIVITY_LEVELS = {
        'sedentary': "Little or no exercise",
        'light': "Exercise/sports 1-3 days/week",
        'moderate': "Exercise/sports 3-5 days/week",
        'active': "Exercise/sports 6-7 days/week",
        'very_active': "Exercise/sports & physical job or 2x training/day",
    }
    errors = []

    # Ensure the unit system is either metric or imperial
    if unit_system not in ["metric", "imperial"]:
        errors.append("Invalid unit system. Must be 'metric' or 'imperial'.")

    # Check required fields based on unit system
    required_fields = [age, gender, activity_level]
    if unit_system == "metric":
        required_fields.extend([weight_kg, height_cm])
    elif unit_system == "imperial":
        required_fields.extend([weight_lb, height_ft, height_in])
    # Check if all necessary fields are provided
    if not all(required_fields):
        errors.append("All fields are required.")

    # Age validation
    try:
        age = int(age)
        if not (MIN_AGE <= age <= MAX_AGE):
            errors.append(f"Age must be between {MIN_AGE} and {MAX_AGE}.")
    except ValueError:
        errors.append("Invalid age value.")

    # Gender validation
    if gender not in ["male", "female"]:
        errors.append("Invalid gender. Must be 'male' or 'female'.")

    # Activity level validation
    if activity_level not in VALID_ACTIVITY_LEVELS:
        errors.append("Invalid activity level.")

    # Validate weights and heights based on unit system
    if unit_system == "metric":
        try:
            weight_kg = float(weight_kg)
            height_cm = float(height_cm)
            if not (MIN_KG <= weight_kg <= MAX_KG):
                errors.append(f"Weight must be between {MIN_KG} kg and {MAX_KG} kg.")
            if not (MIN_CM <= height_cm <= MAX_CM):
                errors.append(f"Height must be between {MIN_CM} cm and {MAX_CM} cm.")
        except (TypeError, ValueError):
            errors.append("Weight and height must be numbers.")
    elif unit_system == "imperial":
        try:
            weight_lb = float(weight_lb)
            height_ft = float(height_ft)
            height_in = float(height_in)
            if not (MIN_LB <= weight_lb <= MAX_LB):
                errors.append(f"Weight must be between {MIN_LB} lb and {MAX_LB} lb.")
            if not (MIN_FT <= height_ft <= MAX_FT):
                errors.append(f"Height feet value must be between {MIN_FT} ft and {MAX_FT} ft.")
            if not (MIN_IN <= height_in <= MAX_IN):
                errors.append(f"Height inches value must be between {MIN_IN} in and {MAX_IN} in.")
        except (TypeError, ValueError):
            errors.append("Weight and height must be numbers.")

    # Validate body fat percentage if provided
    if body_fat_percentage is not None:
        try:
            body_fat_percentage = float(body_fat_percentage)
            if not (0 <= body_fat_percentage <= 100):
                errors.append("Body fat percentage must be between 0 and 100.")
        except (TypeError, ValueError):
            errors.append("Body fat percentage must be a number.")

    return errors


"""
This module provides functions to calculate Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE)
using various equations including the Mifflin-St Jeor and Revised Harris-Benedict equations.
"""


def calculate_bmr_mifflin_st_jeor(weight, height, age, gender):
    """
    Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation.

    Parameters:
    weight (kg): Weight in kilograms
    height (cm): Height in centimeters
    age (years): Age in years
    gender (str): 'male' or 'female'

    Returns:
    float: BMR value
    """
    if gender == 'male':
        return 10 * weight + 6.25 * height - 5 * age + 5
    elif gender == 'female':
        return 10 * weight + 6.25 * height - 5 * age - 161
    else:
        raise ValueError("Gender must be 'male' or 'female'")


def calculate_bmr_harris_benedict(weight, height, age, gender):
    """
    Calculate Basal Metabolic Rate (BMR) using the Revised Harris-Benedict Equation.

    Parameters:
    weight (kg): Weight in kilograms
    height (cm): Height in centimeters
    age (years): Age in years
    gender (str): 'male' or 'female'

    Returns:
    float: BMR value
    """
    if gender == 'male':
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    elif gender == 'female':
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    else:
        raise ValueError("Gender must be 'male' or 'female'")


def calculate_bmr_katch_mcardle(weight, body_fat_percentage):
    """
    Calculate Basal Metabolic Rate (BMR) using the Katch-McArdle Equation.

    Parameters:
    weight (kg): Weight in kilograms
    body_fat_percentage (%): Body fat percentage

    Returns:
    float: BMR value
    """
    lbm = weight * (1 - body_fat_percentage / 100)
    return 370 + (21.6 * lbm)


def calculate_tdee(bmr, activity_level):
    """
    Calculate Total Daily Energy Expenditure (TDEE).

    Parameters:
    bmr (float): Basal Metabolic Rate
    activity_level (str): One of 'sedentary', 'light', 'moderate', 'active', 'very active'

    Returns:
    float: TDEE value
    """
    # Dictionary to hold activity multipliers
    activity_factors = {
        'sedentary': 1.2,           # Little or no exercise
        'light': 1.375,             # Light exercise/sports 1-3 days/week
        'moderate': 1.55,           # Moderate exercise/sports 3-5 days/week
        'active': 1.725,            # Hard exercise/sports 6-7 days/week
        'very_active': 1.9          # Very hard exercise/sports & physical job or 2x training
    }

    # Check if the activity level is valid
    if activity_level not in activity_factors:
        raise ValueError(
            "Activity level must be one of 'sedentary', 'light', 'moderate', 'active', 'very_active'")

    # Calculate and return TDEE
    return bmr * activity_factors[activity_level]


"""
Example usage:
Uncomment and adjust the values to use the functions directly
weight = 88  # kg
height = 190  # cm
age = 27  # years
gender = 'male'
activity_level = 'light'  # light exercise/sports 1-3 days/week
body_fat_percentage = 15  # body fat percentage

bmr_msj = calculate_bmr_mifflin_st_jeor(weight, height, age, gender)
bmr_hb = calculate_bmr_harris_benedict(weight, height, age, gender)
bmr_km = calculate_bmr_katch_mcardle(weight, body_fat_percentage)
tdee = calculate_tdee(bmr_msj, activity_level)

print(f"Mifflin-St Jeor BMR: {bmr_msj:.2f} calories/day")
print(f"Harris-Benedict BMR: {bmr_hb:.2f} calories/day")
print(f"Katch-McArdle BMR: {bmr_km:.2f} calories/day")
print(f"Your TDEE is {tdee:.2f} calories/day")
 """


def validate_traininghub_input(current_weight, squat, bench, deadlift, unit_system):
    """
    Validates the input for the traininghub form.

    Parameters:
        current_weight (float): The current body weight.
        squat (float): The squat weight.
        bench (float): The bench press weight.
        deadlift (float): The deadlift weight.
        unit_system (str): The unit system, either 'metric' or 'imperial'.

    Returns:
        list: A list of error messages if validation fails, otherwise an empty list.
    """

    errors = []

    # Set required fields
    required_fields = [current_weight, squat, bench, deadlift, unit_system]
    # Check if all necessary fields are provided
    if not all(required_fields):
        errors.append("All fields are required.")

    # Ensure the unit system is either metric or imperial
    if unit_system not in ["metric", "imperial"]:
        errors.append("Invalid unit system. Must be 'metric' or 'imperial'.")

    # Validate numeric values
    try:
        current_weight = float(current_weight)
        squat = float(squat)
        bench = float(bench)
        deadlift = float(deadlift)
    except ValueError:
        errors.append("All values must be numeric.")

    if current_weight <= 0 or squat < 0 or bench < 0 or deadlift < 0:
        errors.append("Values cannot be negative.")

    if unit_system == 'imperial':
        if current_weight < MIN_LB or current_weight > MAX_LB:
            errors.append(f"Weight must be between {MIN_LB} and {MAX_LB} lbs.")
    else:
        if current_weight < MIN_KG or current_weight > MAX_KG:
            errors.append(f"Weight must be between {MIN_KG} and {MAX_KG} kg.")

    current_weight_kg = current_weight if unit_system == 'metric' else current_weight * 0.453592

    if any(x > current_weight_kg * 5 for x in [squat, bench, deadlift]):
        errors.append("Strength values cannot be more than 5 times your body weight.")

    return errors



def calculate_fitness_level(gender, bodyweight, squat, bench, deadlift):
    """
    Calculates the fitness level of the person according to official metrics found.
    """
    levels = {
        'male': {
            'intermediate': {'squat': 1.25, 'bench': 1.0, 'deadlift': 1.5},
            'advanced': {'squat': 1.75, 'bench': 1.5, 'deadlift': 2.25},
        },
        'female': {
            'intermediate': {'squat': 1.0, 'bench': 0.75, 'deadlift': 1.0},
            'advanced': {'squat': 1.5, 'bench': 1.0, 'deadlift': 2.0},
        }
    }

    if all([squat >= (levels[gender]['advanced']['squat'] * bodyweight),
            bench >= (levels[gender]['advanced']['bench'] * bodyweight),
            deadlift >= (levels[gender]['advanced']['deadlift'] * bodyweight)]):
        return 'advanced'
    elif all([squat >= (levels[gender]['intermediate']['squat'] * bodyweight),
              bench >= (levels[gender]['intermediate']['bench'] * bodyweight),
              deadlift >= (levels[gender]['intermediate']['deadlift'] * bodyweight)]):
        return 'intermediate'
    else:
        return 'beginner'


def validate_progresshub_input(weight, unit_system, date_recorded):
    """
    Validates the weight and date input for the progresshub form.

    Parameters:
        weight (float): The weight.
        unit_system (str): The unit system, either 'metric' or 'imperial'.
        date_recorded (str): The date when the weight was recorded.

    Returns:
        list: A list of error messages if validation fails, otherwise an empty list.
    """

    errors = []

    # Set required fields
    required_fields = [weight, unit_system, date_recorded]
    # Check if all necessary fields are provided
    if not all(required_fields):
        errors.append("All fields are required.")

    # Ensure the unit system is either metric or imperial
    if unit_system not in ["metric", "imperial"]:
        errors.append("Invalid unit system. Must be 'metric' or 'imperial'.")

    # Check date validity
    try:
        date = datetime.strptime(date_recorded, '%Y-%m-%d')
        if date > datetime.now():
            errors.append("Date cannot be in the future.")
    except ValueError:
        errors.append("Invalid date format. Use YYYY-MM-DD.")

    # Validate weight
    try:
        weight = float(weight)
    except ValueError:
        errors.append("Weight must be a numeric value.")

    if unit_system == 'imperial':
        if weight < MIN_LB or weight > MAX_LB:
            errors.append(f"Weight must be between {MIN_LB} and {MAX_LB} lbs.")
    else:
        if weight < MIN_KG or weight > MAX_KG:
            errors.append(f"Weight must be between {MIN_KG} and {MAX_KG} kg.")

    return errors




def validate_edit_entry_input(weight, unit_system):
    """
    Validates the weight input for editing an entry.

    Parameters:
        weight (float): The weight.
        unit_system (str): The unit system, either 'metric' or 'imperial'.

    Returns:
        list: A list of error messages if validation fails, otherwise an empty list.
    """

    errors = []

    # Check required fields
    required_fields = [weight, unit_system]
    # Check if all necessary fields are provided
    if not all(required_fields):
        errors.append("All fields are required.")

    # Ensure the unit system is either metric or imperial
    if unit_system not in ["metric", "imperial"]:
        errors.append("Invalid unit system. Must be 'metric' or 'imperial'.")

    # Validate weight
    try:
        weight = float(weight)
    except ValueError:
        errors.append("Weight must be a numeric value.")

    if unit_system == 'imperial':
        if weight < MIN_LB or weight > MAX_LB:
            errors.append(f"Weight must be between {MIN_LB} and {MAX_LB} lbs.")
    else:
        if weight < MIN_KG or weight > MAX_KG:
            errors.append(f"Weight must be between {MIN_KG} and {MAX_KG} kg.")

    return errors







def validate_settings_input(unit_system, current_weight_kg, height_cm, current_weight_lb, height_ft, height_in, birthday, gender, activity_level, body_fat_percentage):
    errors = []

    # Set required fields
    required_fields = [unit_system, birthday, gender, activity_level]
    if unit_system == "metric":
        required_fields.extend([current_weight_kg, height_cm])
    elif unit_system == "imperial":
        required_fields.extend([current_weight_lb, height_ft, height_in])

    # Check if all necessary fields are provided
    if not all(required_fields):
        errors.append("All fields are required.")

    # Validate activity level
    VALID_ACTIVITY_LEVELS = ['sedentary', 'light', 'moderate', 'active', 'very_active']
    if activity_level not in VALID_ACTIVITY_LEVELS:
        errors.append("Invalid activity level selection.")

    # Ensure the unit system is either metric or imperial
    if unit_system not in ["metric", "imperial"]:
        errors.append("Invalid unit system. Must be 'metric' or 'imperial'.")

    # Validate weights and heights based on unit system
    if unit_system == "metric":
        try:
            current_weight_kg = float(current_weight_kg)
            height_cm = float(height_cm)
            if not (MIN_KG <= current_weight_kg <= MAX_KG):
                errors.append(f"Weight must be between {MIN_KG} kg and {MAX_KG} kg.")
            if not (MIN_CM <= height_cm <= MAX_CM):
                errors.append(f"Height must be between {MIN_CM} cm and {MAX_CM} cm.")
        except (TypeError, ValueError):
            errors.append("Weight and height must be numbers.")
    elif unit_system == "imperial":
        try:
            current_weight_lb = float(current_weight_lb)
            height_ft = float(height_ft)
            height_in = float(height_in)
            total_height_in_inches = height_ft * 12 + height_in
            if not (MIN_LB <= current_weight_lb <= MAX_LB):
                errors.append(f"Weight must be between {MIN_LB} lb and {MAX_LB} lb.")
            if not (MIN_TOTAL_IN <= total_height_in_inches <= MAX_TOTAL_IN):
                errors.append(f"Height must be between {MIN_TOTAL_IN} in and {MAX_TOTAL_IN} in.")
        except (TypeError, ValueError):
            errors.append("Weight and height must be numbers.")

    # Validate birthday
    try:
        birthday_date = datetime.strptime(birthday, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birthday_date.year - ((today.month, today.day) < (birthday_date.month, birthday_date.day))
        if age < MIN_AGE:
            errors.append(f"You must be at least {MIN_AGE} years old.")
        if age > MAX_AGE:
            errors.append(f"You cannot be more than {MAX_AGE} years old.")
    except ValueError:
        errors.append("Invalid date format. Please enter your birthday as YYYY-MM-DD.")

    # Validate gender
    if gender not in ['male', 'female']:
        errors.append("Invalid gender selection.")

    # Validate body fat percentage if provided
    if body_fat_percentage is not None:
        try:
            body_fat_percentage = float(body_fat_percentage)
            if not (0 <= body_fat_percentage <= 100):
                errors.append("Body fat percentage must be between 0 and 100.")
        except (TypeError, ValueError):
            errors.append("Body fat percentage must be a number.")

    return errors
