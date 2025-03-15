from flask import Flask, request, render_template_string, session, redirect, url_for
import random
import time
import os

app = Flask(__name__)
app.secret_key = 'batman'  # Must use "secret_key" (not "secrety_key")

# --------------------------------
# DATA STRUCTURES
# --------------------------------
character_type = [
    {"playerClass": "Barbarian", "health": 200, "attack": 15,
     "specialAttack": 45, "coolDown": 2, "dodge": 0.2},
    {"playerClass": "Bard", "health": 130, "attack": 20,
     "specialAttack": 50, "coolDown": 4, "dodge": 0.2},
    {"playerClass": "Cleric", "health": 200, "attack": 20,
     "specialAttack": 55, "coolDown": 4.5, "dodge": 0.2},
    {"playerClass": "Druid", "health": 125, "attack": 18,
     "specialAttack": 48, "coolDown": 3, "dodge": 0.2},
    {"playerClass": "Warlock", "health": 150, "attack": 20,
     "specialAttack": 50, "coolDown": 3, "dodge": 0.2},
    {"playerClass": "Ranger", "health": 130, "attack": 20,
     "specialAttack": 40, "coolDown": 2, "dodge": 0.2},
    {"playerClass": "Paladin", "health": 200, "attack": 25,
     "specialAttack": 60, "coolDown": 4, "dodge": 0.2}
]
npc_character = [
    {"playerClass": "Rogue", "health": 150, "attack": 25,
     "specialAttack": 55, "coolDown": 2, "dodge": 0.2},
    {"playerClass": "Fighter", "health": 175, "attack": 20,
     "specialAttack": 45, "coolDown": 1.5, "dodge": 0.2},
    {"playerClass": "Sorcerer", "health": 130, "attack": 20,
     "specialAttack": 40, "coolDown": 1, "dodge": 0.2}
]
npc_characters = ["Rogue", "Fighter", "Sorcerer"]

# --------------------------------
# HELPER FUNCTIONS
# --------------------------------
def dice_roll():
    return random.randint(1, 20)

def dodge(incoming_attack):
    """If someone dodges, reduce the incoming damage by 80%."""
    return round(incoming_attack * 0.2, 2)

def attack(attacker_class, action):
    """Calculate total damage = dice roll + attack/specialAttack. 
       If attacker is 'dodge', damage is 0 (no direct attack)."""
    attacker_stats = next((c for c in character_type if c['playerClass'] == attacker_class), None)
    if attacker_stats is None:
        attacker_stats = next((c for c in npc_character if c['playerClass'] == attacker_class), None)

    roll = dice_roll()
    if attacker_stats:
        if action == 'attack':
            base = attacker_stats['attack']
        elif action == 'special':
            base = attacker_stats['specialAttack']
        else:
            # if user/npc selected "dodge", no direct attack
            base = 0
        return roll + int(base)

    return 0

def initialize_game():
    """Initialize everything in the session (like a 'new game' state)."""
    session['user_class'] = None
    session['opponent_class'] = None
    session['PC_health'] = 0
    session['NPC_health'] = 0
    session['round'] = 0

# --------------------------------
# ROUTES
# --------------------------------
@app.route('/', methods=["GET", "POST"])
def index():
    # If we have no game in progress, initialize
    if 'PC_health' not in session:
        initialize_game()

    # 1) If user_class not selected yet, show the class selection
    if not session['user_class']:
        if request.method == "POST":
            chosen_class = request.form.get('chosen_class')
            if chosen_class:
                # Store user’s chosen class
                session['user_class'] = chosen_class

                # Randomly pick an opponent
                session['opponent_class'] = random.choice(npc_characters)

                # Set health from data structures
                user_stats = next((c for c in character_type 
                                   if c['playerClass'] == chosen_class), None)
                npc_stats = next((c for c in npc_character
                                  if c['playerClass'] == session['opponent_class']), None)

                session['PC_health'] = user_stats['health']
                session['NPC_health'] = npc_stats['health']

                session['round'] = 1

                return redirect(url_for('index'))

        # Render class selection form
        classes_list = [c['playerClass'] for c in character_type]
        return render_template_string(choose_class_template, classes=classes_list)

    # 2) Otherwise, game is in progress
    user_class = session['user_class']
    opponent_class = session['opponent_class']
    PC_health = session['PC_health']
    NPC_health = session['NPC_health']
    round_num = session['round']

    result_message = ""
    if request.method == "POST":
        # The user chose a move
        player_move = request.form.get("move", "").lower()
        valid_moves = ['attack', 'special', 'dodge']

        if player_move in valid_moves:
            # Opponent picks a move
            npc_move = random.choice(valid_moves)

            # Calculate damage
            PC_damage = attack(user_class, player_move)
            NPC_damage = attack(opponent_class, npc_move)

            # If either side dodges, reduce incoming damage
            if player_move == 'dodge':
                NPC_damage = dodge(NPC_damage)
            if npc_move == 'dodge':
                PC_damage = dodge(PC_damage)

            # Apply damage
            PC_health -= NPC_damage
            NPC_health -= PC_damage

            # Update session
            session['PC_health'] = PC_health
            session['NPC_health'] = NPC_health
            session['round'] = round_num + 1

            # Summarize result
            result_message = (
                f"**Round {round_num} Results**<br>"
                f"You chose {player_move.title()}, Opponent chose {npc_move.title()}<br>"
                f"You dealt {PC_damage} damage, and received {NPC_damage} damage.<br>"
            )

    # Check if game is over
    game_over = False
    if PC_health <= 0 or NPC_health <= 0:
        game_over = True
        if PC_health > 0:
            result_message += f"<br>You won! The {opponent_class}'s health is 0."
        elif NPC_health > 0:
            result_message += f"<br>You lost! Your {user_class}'s health is 0."
        else:
            result_message += f"<br>Double KO! Both fighters reached 0."

    return render_template_string(
        gameplay_template,
        result_message=result_message,
        user_class=user_class,
        opponent_class=opponent_class,
        PC_health=PC_health,
        NPC_health=NPC_health,
        game_over=game_over
    )

@app.route("/reset")
def reset():
    """Reset the game session to start over."""
    initialize_game()
    return redirect(url_for("index"))

# --------------------------------
# HTML TEMPLATES (EMBEDDED STRINGS)
# --------------------------------
choose_class_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Choose Your Class</title>
</head>
<body>
    <h1>Choose Your Champion</h1>
    <form method="POST">
        <label for="chosen_class">Select a class:</label>
        <select name="chosen_class" id="chosen_class">
            {% for c in classes %}
            <option value="{{ c }}">{{ c }}</option>
            {% endfor %}
        </select>
        <button type="submit">Confirm</button>
    </form>
</body>
</html>
"""

gameplay_template = """
<!DOCTYPE html>
<html>
<head>
    <title>D&D Combat Game</title>
</head>
<body>
    <h1>D&D Combat Game</h1>
    <p>Your Class: {{ user_class }} (Health: {{ PC_health }})<br/>
       Opponent: {{ opponent_class }} (Health: {{ NPC_health }})</p>
    <p style="color:blue;">{{ result_message|safe }}</p>

    {% if not game_over %}
        <form method="POST">
            <label for="move">Select your move:</label>
            <select name="move" id="move">
                <option value="attack">Attack</option>
                <option value="special">Special</option>
                <option value="dodge">Dodge</option>
            </select>
            <button type="submit">Go</button>
        </form>
    {% else %}
        <p style="color:red;">Game Over!</p>
        <form method="GET" action="/reset">
            <!-- Quick button to reset the session and play again -->
            <button type="submit" name="playagain" value="yes">Play Again</button>
        </form>
    {% endif %}
</body>
</html>
"""

if __name__ == "__main__":
    # For local testing. On PythonAnywhere, you'll use a WSGI file.
    app.run(debug=True)
