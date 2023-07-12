import time
import random

# Dungeon and Dragon Combat game
# inspired by Luc Rieffel's CS course
# Coded by David Cui
# 7/1/2023 - 7/10/2023

# Game Prep
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

#Global Variable
user_class = None
opponent_class = None
PC_health = 0
NPC_health = 0
PC_action = ""
NPC_action = ""
lightSwitch = False

# Game Operations
def choose_character():
    # step 1: print out character options for user
    # step 2: make sure user input is valid
    # step 3: print out users character selection and begin game in a separate function
    class_type = []
    for character in character_type:
        print(
            f"Class: {character['playerClass']}, Health: {character['health']}, Attack: {character['attack']}, Cooldown: {character['coolDown']}")
        class_type.append(character['playerClass'])
    print()
    global user_class
    user_class = input(
        "Pick a class for your champion from the list above: ").title()
    while user_class not in class_type:
        user_class = input(
            "Pick a class for your champion from the list above: ").title()

    global opponent_class
    opponent_ask = input(
        "Would you like to pick your opponent? (Y/N) ").lower()
    while opponent_ask not in ['yes', 'y', 'no', 'n']:
        opponent_ask = input(
            "Invalid input. Would you like to pick your opponent? ").lower()

    if opponent_ask in ['yes', 'y']:
        for character in npc_character:
            print(
                f"Class: {character['playerClass']}, Health: {character['health']}, Attack: {character['attack']}, Cooldown: {character['coolDown']}")
        opponent_class = input("Select your opponent class: ").title()
        print()
    else:
        opponent_class = random.choice(npc_characters)
        print()
    global NPC_health
    global PC_health
    print(f"Your opponent is {opponent_class}")
    opponent_stats = next(
        (character for character in npc_character if character['playerClass'] == opponent_class), None)
    if opponent_stats:
        NPC_health = int(opponent_stats['health'])
        print(
            f"Opponent's stats ==> Health: {opponent_stats['health']}, Attack: {opponent_stats['attack']}, Cooldown: {opponent_stats['coolDown']}")
    print(f"Your class is {user_class}")
    user_stats = next(
        (character for character in character_type if character['playerClass'] == user_class), None)
    if user_stats:
        PC_health = int(user_stats['health'])
        print(
            f"User's stats ==> Health: {user_stats['health']}, Attack: {user_stats['attack']}, Cooldown: {user_stats['coolDown']}")
    print()
    return user_class, opponent_class
    


def dice_roll():
    d20 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
           12, 13, 14, 15, 16, 17, 18, 19, 20]
    return int(random.choice(d20))

def dodge(incoming_attack):  # DODGE
    return round(incoming_attack * (0.2), 2)


def attack(attacker_class, action):  # Parameter: the attacker and action
    # 1.) Take in the attacker dictionary
    # 2.) Take in the attacker action(s): (attack, special, or dogge)
    attacker_stats = next(
        (character for character in character_type if character['playerClass'] == attacker_class), None)
    if attacker_stats is None:
        attacker_stats = next(
            (character for character in npc_character if character['playerClass'] == attacker_class), None)
    
    roll = dice_roll()
    damage_dealt = 0 
    if attacker_stats:
        if action in ['attack']:
            attack = attacker_stats['attack']
        elif action in ['special']:
            attack = attacker_stats['specialAttack']
        else:
            attack = roll + dodge(0)
            pass
    damage_dealt = roll + int(attack)
  
    return damage_dealt

def cooldown_timer(cooldown_time): #helper method
    start_time = time.time()
    end_time = start_time + cooldown_time
    while time.time() < end_time:
        remaining_time = round(float(end_time - time.time()), 2)
        print(f"Cooldown remaining: {remaining_time}s", end="\r")
        time.sleep(0.1)
    print("\nCooldown expired!")
    return remaining_time

def cooldown_checker(current_player, current_player_action):
    cooldown_active = False
    #First checks through the dictionary of both PC and NPC
    current_player_stats = next(
        (character for character in character_type if character['playerClass'] == current_player), None)
    if current_player_stats is None:
        current_player_stats = next(
            (character for character in npc_character if character['playerClass'] == current_player), None)
    
    if current_player_stats: #convert from integer to a float value
        global lightSwitch
        if current_player_action == 'special':#If this is the first time, special is used
            if lightSwitch == False:
                cooldown_active = False
                lightSwitch = True
            else:#if this is the second time and cooldown didn't finish, special will turn to normal attack
                cooldown_active = True
                coolDown = float(current_player_stats['coolDown'])
                remaining_time = cooldown_timer(coolDown)
                if remaining_time > 0:
                    print(f"Cooldown active. Wait {remaining_time} seconds before using special attack.")
                    current_player_action = 'attack'
                lightSwitch = False
    #This function will return true if cooldown is active and also change the attack from a special to a normal attack
    return cooldown_active, current_player_action

def results(PC_action, NPC_action, PC_damage, NPC_damage):
        #Need to include different statements for different combonations
    global PC_health
    global NPC_health
    
    print(f"You chose {PC_action.title()}!")
    print(f"Computer chose {NPC_action.title()}!")
         
    if PC_action in ["attack", "special"] and NPC_action in ["attack", "special"]:
        PC_health -= NPC_damage
        NPC_health -= PC_damage
        print(f"You attacked {opponent_class} and dealt {PC_damage} damage!")
        print(f"The {opponent_class} attacked you, the {user_class}, and dealt {NPC_damage} damage!")
    elif PC_action in ["attack", "special"] and NPC_action in ["dodge"]:
        NPC_health -= dodge(PC_damage)
        print(f"You attacked {opponent_class}, but he dodged resulting in only {dodge(PC_damage)} damage!")
    elif PC_action in ["dodge"] and NPC_action in ["attack", "special"]:
        PC_health -= dodge(NPC_damage)
        print(f"The {opponent_class} attacked you, but you dodged, resulting in {dodge(NPC_damage)} damage!")
    elif PC_action == "dodge" and NPC_action == "dodge":
        print("Both players have chosen to dodge. No one takes damage!")
    else:
        print("Invalid actions.")
    print()

def gamePlay():
    global user_class
    global opponent_class
    global PC_health
    global NPC_health
    moves = ['attack', 'special', 'dodge']

    player1, player2 = choose_character() #user_class and then NPC
    current_player = player1 #PC
    non_current_player = player2 #NPC
    round = 0
    
    while (PC_health > 0 or NPC_health > 0):
        round += 1
        current_player_action = input(f"Round {round}: Select your move (attack, special, or dodge): ").lower()
        while current_player_action not in moves:
            current_player_action = input(f"Not a valid move. Select your action (attack, special, or dodge): ").lower()
        
        #Simultaneous moves 
        if current_player == player1:
            non_current_player_action = random.choice(moves)
            
        cooldown_active, current_player_action = cooldown_checker(current_player, current_player_action)
        if current_player_action == "special":
            if cooldown_active:
                current_player_action = "attack"
            PC_damage = attack(current_player, current_player_action)
        else:
            PC_damage = attack(current_player, current_player_action)
            
        #The other player
        cooldown_active, non_current_player_action = cooldown_checker(non_current_player, non_current_player_action)
        if non_current_player_action == "special":
            if cooldown_active:
                non_current_player_action = "attack"
            NPC_damage = attack(non_current_player, non_current_player_action)
        else:
            NPC_damage = attack(non_current_player, non_current_player_action)
        NPC_action = current_player_action
         
        results(current_player_action, non_current_player_action, PC_damage, NPC_damage)
    
    if PC_health > 0 and NPC_health <= 0:
        print(f"The {opponent_class}'s health has reached 0. You have won!")
    elif PC_health <=0 and NPC_health > 0:
        print(f"The {user_class}'s health has reached 0. You have lost...")
    else: 
        if current_player == player1:
            print(f"The {opponent_class}'s health has reached 0. You have won!")
        else:
            print(f"The {user_class}'s health has reached 0. You have lost...")
            
gamePlay()
