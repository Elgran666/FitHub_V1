from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, calculate_bmr_mifflin_st_jeor, calculate_bmr_katch_mcardle, calculate_tdee, validate_signup_data, calculate_age, validate_caloriehub_input, validate_traininghub_input, calculate_fitness_level, validate_progresshub_input, validate_settings_input, validate_edit_entry_input
from datetime import datetime
""" below only for debugging """

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fithub.db")


@app.context_processor
# Global variable names for all templates / routes in case we want to change name of any tab
def inject_hub_names():
    return {
        'site_name': 'FitHub',
        'home': 'Home',
        'info_hub': 'Info Hub',
        'calorie_hub': 'Calorie Hub',
        'training_hub': 'Training Hub',
        'progress_hub': 'Progress Hub',
        'personal_details_hub': 'Personal Details Hub',
        'sign_in': '',
        'sign_up': '',
        'sign_out': '',
        'settings': 'Settings',
    }


@app.after_request
# Cache handling from flask.
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", defaults={"path": ""})
# Catch-all route for any undefined paths
# If route = "/" it'll default to an empty string. This effectively means that the root URL (/) will be processed by the catch_all function.
# The <path:path> part captures the entire remaining part of the URL after the initial / and assigns it to the variable path.
# --> Essentially a wildcard route that catches all undefined paths.
@app.route("/<path:path>")
def catch_all(path):
    """
    Catch-all route for undefined paths.

    This route will catch any URL that does not match the explicitly defined routes.
    It checks if the user is logged in by looking for 'user_id' in the session.
    - If the user is not logged in, they are redirected to the login page.
    - If the user is logged in, they are redirected to the home page.

    Parameters:
    path (str): The remaining part of the URL after the initial '/'

    Returns:
    redirect: A redirect response to either the login or home page.
    """
    if 'user_id' not in session:
        # User is not logged in, redirect to login page
        return redirect(url_for('login'))
    else:
        # User is logged in, redirect to home page
        return redirect(url_for('home'))


@app.route("/check_username", methods=["POST"])
# Check if user is in database.
def check_username():
    """
    Endpoint to check if a username exists in the database.

    This function handles POST requests to the /check_username URL.
    It retrieves the username from the form data and checks if a user with
    that username exists in the database.

    Returns:
    - A JSON (jsonify converts a Python dictionary into a JSON) indicating whether the username exists in the database.
        - {"exists": True} if the username is found.
        - {"exists": False} if the username is not found.
    """
    username = request.form.get("username")
    user_exists = db.execute(
        "SELECT * FROM users WHERE username = ?", username)
    if user_exists:
        return jsonify({"exists": True})
    return jsonify({"exists": False})


@app.route("/login", methods=["GET", "POST"])
# Handles "/login" route and if a user used "login" functionality
def login():
    """Log user in"""

    # Forget any user_id in the session
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Process the login form
        username = request.form.get("signInUsername")
        password = request.form.get("signInPassword")

        # Check if username and password are provided
        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html")

        # Query database for the user
        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Check if the user exists and the password is correct
        # len(user) != 1: Ensures exactly one user is found with the given username
        # check_password_hash: Verifies if the provided password matches the hashed password stored in the database
        if len(user) != 1 or not check_password_hash(user[0]['hash_password'], password):
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        # Remember the user's id in the session
        session['user_id'] = user[0]['id']
        flash(f"Login successful, welcome back {username}!", "success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/signup", methods=["POST"])
def signup():
    if request.method == "POST":
        # Get all relevant form data
        user_data = {
            "username": request.form.get("createAccountUsername"),
            "password": request.form.get("createAccountPassword"),
            "confirmed_password": request.form.get("createAccountConfirmPassword"),
            "birthday": request.form.get("birthday"),
            "gender": request.form.get("gender"),
            "activity_level": request.form.get("activity_level"),
            "unit_system": request.form.get("unit_system"),
            "current_weight_kg": request.form.get("current_weight_kg"),
            "height_cm": request.form.get("height_cm"),
            "current_weight_lb": request.form.get("current_weight_lb"),
            "height_ft": request.form.get("height_ft"),
            "height_in": request.form.get("height_in"),
            "body_fat_percentage": request.form.get("body_fat_percentage")
        }

        # Handle empty body_fat_percentage as its optional and if not provided ends up as an empty string
        if user_data['body_fat_percentage'] == "":
            user_data['body_fat_percentage'] = None

        # Perform validation
        errors = validate_signup_data(**user_data)
        if errors:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for('login'))

        # Convert to metric for storage if imperial and round to one decimal place
        if user_data["unit_system"] == "imperial":
            user_data["current_weight_kg"] = round(
                float(user_data["current_weight_lb"]) * 0.453592, 1)
            total_height_in_inches = (
                float(user_data["height_ft"]) * 12) + float(user_data["height_in"])
            user_data["height_cm"] = round(total_height_in_inches * 2.54, 1)

        # Checking for username uniqueness
        user_exists = db.execute(
            "SELECT * FROM users WHERE username = ?", user_data["username"])
        if user_exists:
            logging.info("Username already taken.")
            flash("Username already taken.", "warning")
            return redirect(url_for('login'))

        # Registering the user
        try:
            hashed_password = generate_password_hash(user_data["password"])
            user_id = db.execute(
                "INSERT INTO users (username, hash_password, unit_system, current_weight_kg, height_cm, birthday, gender, activity_level, body_fat_percentage) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                user_data["username"], hashed_password, user_data["unit_system"], user_data["current_weight_kg"], user_data[
                    "height_cm"], user_data["birthday"], user_data["gender"], user_data["activity_level"], user_data["body_fat_percentage"]
            )

            # Create session['user_id'] to use throughout the session
            session['user_id'] = user_id
            flash(
                f"Created account successfully! Welcome, {user_data['username']}!", "success")
            return redirect("/home")
        except Exception as e:
            flash("An error occurred during registration. Please try again.", "danger")
            return redirect(url_for('login'))

    return redirect("/login")


@app.route("/home")
# Home route
@login_required
def home():
    """Show the homepage."""
    return render_template("home.html")


@app.route("/infohub")
# Infohub route
@login_required
def infohub():
    """Show the infohub calculator page."""
    return render_template("infohub.html")


@app.route("/caloriehub", methods=["GET", "POST"])
# Caloriehub route
@login_required
def caloriehub():
    user_id = session['user_id']

    # Fetch user data from the database
    user_data = db.execute('SELECT * FROM users WHERE id = ?', user_id)[0]
    user_data['age'] = calculate_age(user_data['birthday'])

    # Convert weight and height to imperial if necessary
    if user_data['unit_system'] == 'imperial':
        user_data['weight_lb'] = round(
            user_data['current_weight_kg'] / 0.453592, 1)  # Round to nearest 0.1 lb
        user_data['height_ft'] = round(
            user_data['height_cm'] / 30.48)  # Round to nearest full ft
        user_data['height_in'] = round(
            (user_data['height_cm'] % 30.48) / 2.54)  # Round to nearest full in
    else:
        user_data['weight_lb'] = None
        user_data['height_ft'] = None
        user_data['height_in'] = None

    return render_template("caloriehub.html", user_data=user_data)


@app.route("/caloriehub_plans", methods=["POST"])
# caloriehub_plans route is for valdiation + caculating calorie output + showing charts etc.
@login_required
def caloriehub_plans():
    # Get all relevant form data, if one field is not provided, it defaults to an empty string ""
    user_data = {
        'unit_system': request.form.get('unit_system'),
        'weight_kg': request.form.get('weight_kg'),
        'weight_lb': request.form.get('weight_lb'),
        'height_cm': request.form.get('height_cm'),
        'height_ft': request.form.get('height_ft'),
        'height_in': request.form.get('height_in'),
        'age': request.form.get('age'),
        'gender': request.form.get('gender'),
        'activity_level': request.form.get('activity_level'),
        'body_fat_percentage': request.form.get('body_fat_percentage')
    }

    # Handle empty body_fat_percentage as its optional and if not provided ends up as an empty string    if user_data['body_fat_percentage'] == "":
    if user_data['body_fat_percentage'] == "":
        user_data['body_fat_percentage'] = None

    # Validate input data
    # ** passes in the dictionary at a whole and flask unpacks it so we can just use the variable names in the function rigth away instead of dict["key"] or dict.key
    errors = validate_caloriehub_input(**user_data)
    if errors:
        flash("<br>".join(errors), 'danger')
        return redirect(url_for('caloriehub'))

    # Attempt to convert and calculate based on the unit system
    if user_data['unit_system'] == 'metric':
        weight = float(user_data['weight_kg'])
        height = float(user_data['height_cm'])
    elif user_data['unit_system'] == 'imperial':
        weight = float(user_data['weight_lb']) * \
            0.453592  # convert pounds to kg
        # convert feet and inches to cm
        height = (float(user_data['height_ft']) * 30.48) + \
            (float(user_data['height_in']) * 2.54)

    # Calculate BMR
    if user_data['body_fat_percentage'] is not None:
        bmr = calculate_bmr_katch_mcardle(
            weight, float(user_data['body_fat_percentage']))
    else:  # if its "None", hence not provided
        bmr = calculate_bmr_mifflin_st_jeor(
            weight, height, int(user_data['age']), user_data['gender'])

    # Calculate TDEE for the user's provided activity level
    tdee = calculate_tdee(bmr, user_data['activity_level'])

    # Define activity levels for the table and user input section
    activity_levels = {
        'sedentary': "Little or no exercise",
        'light': "Exercise/sports 1-3 days/week",
        'moderate': "Exercise/sports 3-5 days/week",
        'active': "Exercise/sports 6-7 days/week",
        'very_active': "Exercise/sports & physical job or 2x training/day",
    }

    """
    Retrieve the detailed activity level description for the user's activity level.
    activity_levels.get(user_data['activity_level'], user_data['activity_level']) will:
        1. Return the description if the activity level key exists in the activity_levels dictionary.
        2. Use the activity level key itself as a fallback if it does not exist in the dictionary.
        --> This ensures a meaningful value is always assigned to user_data['activity_level_description'].
        --> either we get the description, or otherwise we return the key itself i.e. moderate
        --> second user_data['activity_level'] is the fallback mechanism for the key itself
    """
    user_data['activity_level_description'] = activity_levels.get(
        user_data['activity_level'], user_data['activity_level'])

    # Create a dictionary to store TDEE (Total Daily Energy Expenditure) for different activity levels
    tdee_activity_levels = {}

    # Loop through each activity level and its description
    for level, description in activity_levels.items():
        # Calculate TDEE for the current activity level using the BMR (Basal Metabolic Rate) and the activity level factor
        tdee_value = calculate_tdee(bmr, level)

        # Create a dictionary entry for the current activity level with its description and calculated TDEE
        tdee_activity_levels[level] = {
            "description": description,
            "calories": f"{int(tdee_value)} cal/day"
        }

    diets = [
        {
            'id': 'maintenance',
            'name': 'Maintenance',
            'title': 'Your Maintenance Diets',
            'description': f'Your maintenance diet helps you to maintain weight and uses <u><b>{int(tdee)} calories</u></b> per day.',
            'calorie_adjustment': 0  # No adjustment for maintenance
        },
        {
            'id': 'lose-weight',
            'name': 'Lose Weight',
            'title': 'Your Weight Loss Diets',
            'description': f'Your weight loss diet helps you to lose weight by consuming <u><b>{int(tdee - 500)} calories</u></b> per day, which is <b><u>500 calories less than your maintenance level</u></b>. This deficit can help you lose body fat, as approximately 7,000 calories need to be burned over time to lose 1 kg of body fat.<br>',
            'calorie_adjustment': -500  # -500 for weight loss
        },
        {
            'id': 'build-muscle',
            'name': 'Build Muscle',
            'title': 'Your muscle-building Diets',
            'description': f'Your muscle-building diet helps you gain muscle mass by consuming <u><b>{int(tdee + 200)} calories</u></b> per day, which is <b><u>200 calories more than your maintenance level</u></b>. To optimize muscle growth, it is generally recommended to maintain a slight calorie surplus.<br>',
            'calorie_adjustment': +200  # + 200 for muscle building
        }
    ]

    # Pass all data to the template
    return render_template('caloriehub_plans.html',
                           user_data=user_data,
                           tdee=int(tdee),
                           tdee_activity_levels=tdee_activity_levels,
                           bmr=int(bmr),
                           diets=diets
                           )


@app.route("/traininghub", methods=['GET', 'POST'])
# traininghub route for creating custom workout plans
@login_required
def traininghub():
    user_id = session['user_id']

    # Fetch user data from the database
    user_data = db.execute('SELECT * FROM users WHERE id = ?', user_id)[0]
    unit_system = user_data['unit_system']
    current_weight_kg = user_data['current_weight_kg']
    current_weight = round(current_weight_kg if unit_system ==
                           'metric' else current_weight_kg / 0.453592, 1)

    user_data = {
        'current_weight': current_weight,
        'unit_system': unit_system,
        'squat': None,
        'bench': None,
        'deadlift': None,
    }

    if request.method == 'POST':
        # Collect form data
        user_data.update({
            'current_weight': request.form.get('current_weight'),
            'squat': request.form.get('squat'),
            'bench': request.form.get('bench'),
            'deadlift': request.form.get('deadlift')
        })

        # Validate input data
        # ** passes in the dictionary at a whole and flask unpacks it so we can just use the variable names in the function rigth away instead of dict["key"] or dict.key
        errors = validate_traininghub_input(**user_data)
        if errors:
            flash("<br>".join(errors), 'danger')
            return render_template("traininghub.html", **user_data)

        user_data['current_weight'] = float(user_data['current_weight'])
        user_data['squat'] = float(user_data['squat'])
        user_data['bench'] = float(user_data['bench'])
        user_data['deadlift'] = float(user_data['deadlift'])

        # Convert to kg if the unit system is imperial
        if unit_system == 'imperial':
            user_data['current_weight_kg'] = round(
                user_data['current_weight'] * 0.453592, 1)
            user_data['squat'] = round(user_data['squat'] * 0.453592, 1)
            user_data['bench'] = round(user_data['bench'] * 0.453592, 1)
            user_data['deadlift'] = round(user_data['deadlift'] * 0.453592, 1)
        else:
            user_data['current_weight_kg'] = round(
                user_data['current_weight'], 1)

        # Calculate the fitness level based on the strength metrics
        user_data['fitness_level'] = calculate_fitness_level(
            user_data['gender'], user_data['current_weight_kg'], user_data['squat'], user_data['bench'], user_data['deadlift'])

    # ** passes in the dictionary at a whole and flask unpacks it so we can just use the variable names in the function rigth away instead of dict["key"] or dict.key
    return render_template('traininghub.html', **user_data)


@app.route('/progresshub', methods=['GET', 'POST'])
# progresshub route lets user track their body weight progress over time
@login_required
def progresshub():
    user_id = session['user_id']

    # Fetch the user's unit system
    user_data = db.execute(
        'SELECT unit_system FROM users WHERE id = ?', user_id)[0]
    unit_system = user_data['unit_system']

    if request.method == 'POST':
        weight = request.form['weight']
        date_recorded = request.form.get(
            'date_recorded', datetime.now().strftime('%Y-%m-%d'))

        # Validate weight input
        error = validate_progresshub_input(weight, unit_system, date_recorded)
        if error:
            flash(error, 'danger')
            return redirect(url_for('progresshub'))

        weight = float(weight)

        # Convert weight to kg if the unit is lb
        if unit_system == 'imperial':
            weight_kg = round(weight * 0.453592, 1)
        else:
            # Ensure metric weight is also rounded to one decimal place
            weight_kg = round(weight, 1)

        # Check if entry for this date already exists
        existing_entry = db.execute(
            'SELECT id FROM weight_entries WHERE user_id = ? AND date_recorded = ?', user_id, date_recorded)

        if existing_entry:
            db.execute('UPDATE weight_entries SET weight_kg = ? WHERE id = ?',
                       weight_kg, existing_entry[0]['id'])
            flash('Weight entry updated.', 'success')
        else:
            db.execute('INSERT INTO weight_entries (user_id, weight_kg, date_recorded) VALUES (?, ?, ?)',
                       user_id, weight_kg, date_recorded)
            flash('Weight entry added.', 'success')

        return redirect(url_for('progresshub'))

    # Always fetch and display existing data
    entries = db.execute(
        'SELECT id, weight_kg, date_recorded FROM weight_entries WHERE user_id = ? ORDER BY date_recorded', user_id)

    # Convert weights to user's preferred unit system for display
    for entry in entries:
        if unit_system == 'imperial':
            # Round to one decimal place
            entry['weight'] = round(entry['weight_kg'] / 0.453592, 1)
            entry['unit'] = 'lb'
        else:
            # Round to one decimal place
            entry['weight'] = round(entry['weight_kg'], 1)
            entry['unit'] = 'kg'

    return render_template('progresshub.html', entries=entries, current_date=datetime.now().strftime('%Y-%m-%d'), unit_system=unit_system)


@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
# Route to handle deletion of a weight entry
@login_required
def delete_entry(entry_id):
    user_id = session['user_id']
    # Delete the entry if it belongs to the logged-in user
    db.execute(
        'DELETE FROM weight_entries WHERE id = ? AND user_id = ?', entry_id, user_id)
    flash('Weight entry deleted.', 'success')
    return redirect(url_for('progresshub'))


@app.route('/edit_entry/<int:entry_id>', methods=['POST'])
# Route to handle editing of a weight entry
@login_required
def edit_entry(entry_id):
    user_id = session['user_id']
    weight = request.form['weight']
    date_recorded = request.form['date_recorded']
    unit_system = db.execute('SELECT unit_system FROM users WHERE id = ?', user_id)[
        0]['unit_system']

    # Validate weight input
    error = validate_edit_entry_input(weight, unit_system)
    if error:
        return jsonify({"error": error}), 400

    weight = float(weight)

    # Convert weight to kg if the unit is lb
    if unit_system == 'imperial':
        weight_kg = weight * 0.453592
    else:
        weight_kg = weight

    # Update the entry with the new weight and date
    db.execute('UPDATE weight_entries SET weight_kg = ?, date_recorded = ? WHERE id = ?',
               weight_kg, date_recorded, entry_id)
    return jsonify({"message": "Weight entry updated successfully."}), 200


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user_id = session['user_id']

    if request.method == "GET":
        user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
        # we simply calculate this below as
        #   1) if the unit system is imperial we need the data
        #   2) if the unit system is metric but the user changes to imperial, it should auto convert the current value.
        current_weight_lb = round(user_data['current_weight_kg'] / 0.453592, 1)
        total_height_in_inches = round(user_data['height_cm'] / 2.54)
        height_ft = int(total_height_in_inches // 12)
        height_in = int(total_height_in_inches % 12)

        # Create a dictionary to pass to the template
        template_data = {
            'user_data': user_data,
            'current_weight_lb': current_weight_lb,
            'height_ft': height_ft,
            'height_in': height_in
        }

        # ** passes in the dictionary at a whole and flask unpacks it so we can just use the variable names in the function rigth away instead of dict["key"] or dict.key
        return render_template("settings.html", **template_data)

    if request.method == "POST":
        user_data = {
            'unit_system': request.form.get("unit_system"),
            'birthday': request.form.get("birthday"),
            'gender': request.form.get("gender"),
            'activity_level': request.form.get("activity_level"),
            'body_fat_percentage': request.form.get("body_fat_percentage", None),
            'current_weight_kg': request.form.get("current_weight_kg"),
            'height_cm': request.form.get("height_cm"),
            'current_weight_lb': request.form.get("current_weight_lb"),
            'height_ft': request.form.get("height_ft"),
            'height_in': request.form.get("height_in")
        }

        # Handle empty body_fat_percentage as its optional and if not provided ends up as an empty string
        if user_data['body_fat_percentage'] == "":
            user_data['body_fat_percentage'] = None

        # Validate input data
        # ** passes in the dictionary at a whole and flask unpacks it so we can just use the variable names in the function rigth away instead of dict["key"] or dict.key
        errors = validate_settings_input(**user_data)
        if errors:
            flash("<br>".join(errors), "danger")
            return redirect(url_for('settings'))

        # Convert to metric for storage if imperial and round to one decimal place
        if user_data['unit_system'] == 'imperial':
            user_data['current_weight_kg'] = round(
                float(user_data['current_weight_lb']) * 0.453592, 1)
            user_data['height_cm'] = round(
                (float(user_data['height_ft']) * 30.48) + (float(user_data['height_in']) * 2.54), 1)

        db.execute(
            "UPDATE users SET unit_system = ?, current_weight_kg = ?, height_cm = ?, birthday = ?, gender = ?, activity_level = ?, body_fat_percentage = ? WHERE id = ?",
            user_data['unit_system'], user_data['current_weight_kg'], user_data['height_cm'], user_data[
                'birthday'], user_data['gender'], user_data['activity_level'], user_data['body_fat_percentage'], user_id
        )

        flash("Settings updated successfully!", "success")
        return redirect(url_for('settings'))


@app.route("/change_password", methods=["POST"])
# lets user change their password
@login_required
def change_password():
    user_id = session['user_id']
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]

    # Validate current password
    if not check_password_hash(user_data['hash_password'], current_password):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for('settings'))

    # Validate new password and confirmation
    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for('settings'))

    # Update password
    new_password_hash = generate_password_hash(new_password)
    db.execute("UPDATE users SET password = ? WHERE id = ?",
               new_password_hash, user_id)

    flash("Password updated successfully.", "success")
    return redirect(url_for('settings'))


@app.route("/logout")
# Logout route
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

# test everything once more!
# upload to the server
