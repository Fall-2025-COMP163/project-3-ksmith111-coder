"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module

Name: Khalil Smith

AI Usage: I defined the base character structure, class names (Warrior, Mage, Rogue, Cleric), 
          and core function signatures (create_character, save_character, load_character). 
          The AI implemented the file I/O logic, including manual string parsing for 
          loading key-value pairs and converting list data (inventory, quests). The AI also 
          implemented the stat management functions (gain_experience, take_damage, etc.) 
          and ensures correct exception handling as required by the project.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# Base stats for the four required classes (Stored as a global constant dictionary)
BASE_STATS_MAP = {
    "Warrior": {"health": 120, "strength": 15, "magic": 5},
    "Mage":    {"health": 80, "strength": 8, "magic": 20},
    "Rogue":   {"health": 90, "strength": 12, "magic": 10},
    "Cleric":  {"health": 100, "strength": 10, "magic": 15},
}

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS (I/O)
# ============================================================================

def create_character(name, character_class):
    """
    Creates a new character dictionary with base stats based on class.
    
    Raises: InvalidCharacterClassError
    """
    valid_classes = list(BASE_STATS_MAP.keys())

    if character_class not in valid_classes:
        # Check if the requested class name is valid
        raise InvalidCharacterClassError(f"Invalid class: {character_class}. Must be one of {valid_classes}")

    stats = BASE_STATS_MAP[character_class]

    # Initialize character dictionary with default and base stats
    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "experience": 0,
        "gold": 100,
        
        # Base Stats (updated only on level-up)
        "base_health": stats["health"],
        "base_strength": stats["strength"],
        "base_magic": stats["magic"],
        
        # Current Calculated Stats (updated by equipment and level-up)
        "health": stats["health"],
        "max_health": stats["health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "defense": 0,
        "attack": 0,
        
        # Inventory and Equipment
        "inventory": [],
        "equipped_weapon": None,
        "equipped_armor": None,
        
        # Quest Tracking
        "active_quests": [],
        "completed_quests": []
    }

    return character


def save_character(character, save_directory="data/save_games"):
    """
    Saves a character's data into a text file using a KEY: VALUE format.
    """

    if not os.path.exists(save_directory):
        os.makedirs(save_directory, exist_ok=True)

    filename = os.path.join(save_directory, f"{character['name']}_save.txt")

    # Helper function to convert list fields into comma-separated strings for saving
    def list_to_str(key):
        return ",".join(character.get(key, [])) or "NONE"

    # Get equipment IDs, using "NONE" if slot is empty
    equipped_weapon = character.get("equipped_weapon") or "NONE"
    equipped_armor = character.get("equipped_armor") or "NONE"

    # Define the data structure to be saved
    save_data = [
        ("NAME", character["name"]),
        ("CLASS", character["class"]),
        ("LEVEL", str(character["level"])),
        ("HEALTH", str(character["health"])),
        ("MAX_HEALTH", str(character["max_health"])),
        ("STRENGTH", str(character["strength"])),
        ("MAGIC", str(character["magic"])),
        ("DEFENSE", str(character.get("defense", 0))),
        ("ATTACK", str(character.get("attack", 0))),
        ("EXPERIENCE", str(character["experience"])),
        ("GOLD", str(character["gold"])),
        ("BASE_HEALTH", str(character["base_health"])),
        ("BASE_STRENGTH", str(character["base_strength"])),
        ("BASE_MAGIC", str(character["base_magic"])),
        ("EQUIPPED_WEAPON", equipped_weapon),
        ("EQUIPPED_ARMOR", equipped_armor),
        ("INVENTORY", list_to_str("inventory")),
        ("ACTIVE_QUESTS", list_to_str("active_quests")),
        ("COMPLETED_QUESTS", list_to_str("completed_quests")),
    ]

    try:
        with open(filename, "w", encoding="utf-8") as f:
            # Loop through the data and write each line
            i = 0
            while i < len(save_data):
                key = save_data[i][0]
                value = save_data[i][1]
                f.write(f"{key}: {value}\n")
                i += 1
    except Exception as e:
        # Catch unexpected file writing errors
        raise SaveFileCorruptedError(f"Failed to write save file: {e}")

    return True


def load_character(character_name, item_data_dict, save_directory="data/save_games"):
    """
    Loads a character from a save file and rebuilds the character dictionary.
    
    Raises: CharacterNotFoundError, SaveFileCorruptedError, InvalidSaveDataError
    """

    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save file found for '{character_name}'")

    data = {}
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            # Loop through file lines to parse data
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Manual Parsing: checks for required separator
                if ": " not in line:
                    raise InvalidSaveDataError(f"Invalid line in save file for '{character_name}': missing ': ' separator.")
                    
                # Parsing the key and value
                parts = line.split(": ", 1)
                key = parts[0].strip().upper()
                val = parts[1].strip()
                data[key] = val
                
    except InvalidSaveDataError:
        # Re-raise explicit parsing error
        raise
    except Exception as e:
        # Catch other read errors
        raise SaveFileCorruptedError(f"Could not read or parse save file: {e}")

    # List of required fields for a valid character file
    required_keys = [
        "NAME", "CLASS", "LEVEL", "HEALTH", "MAX_HEALTH",
        "STRENGTH", "MAGIC", "EXPERIENCE", "GOLD",
        "BASE_HEALTH", "BASE_STRENGTH", "BASE_MAGIC", 
        "EQUIPPED_WEAPON", "EQUIPPED_ARMOR",
        "INVENTORY", "ACTIVE_QUESTS", "COMPLETED_QUESTS"
    ]
    
    # Validation step 1: Check for critical missing keys
    i = 0
    while i < len(required_keys):
        key = required_keys[i]
        if key not in data:
             # If a core stat is missing, raise an error
             raise InvalidSaveDataError(f"Critical field missing from save file: {key}")
        i += 1


    try:
        # Helper function to parse saved string lists (comma-separated)
        def parse_list_str(s):
            return [] if s.upper() in ("", "NONE") else s.split(",")

        # Helper to parse equipment (NONE -> None)
        def parse_equipment_str(s):
            return None if s.upper() in ("", "NONE") else s

        # Rebuild character dictionary, converting numeric strings to integers
        character = {
            "name": data["NAME"],
            "class": data["CLASS"],
            "level": int(data["LEVEL"]),
            "health": int(data["HEALTH"]),
            "max_health": int(data["MAX_HEALTH"]),
            "strength": int(data["STRENGTH"]),
            "magic": int(data["MAGIC"]),
            # Use .get with a default for optional fields like defense/attack in old saves
            "defense": int(data.get("DEFENSE", 0)), 
            "attack": int(data.get("ATTACK", 0)),
            "experience": int(data["EXPERIENCE"]),
            "gold": int(data["GOLD"]),
            
            "base_health": int(data["BASE_HEALTH"]),
            "base_strength": int(data["BASE_STRENGTH"]),
            "base_magic": int(data["BASE_MAGIC"]),
            
            "equipped_weapon": parse_equipment_str(data["EQUIPPED_WEAPON"]),
            "equipped_armor": parse_equipment_str(data["EQUIPPED_ARMOR"]),
            
            "inventory": parse_list_str(data["INVENTORY"]),
            "active_quests": parse_list_str(data["ACTIVE_QUESTS"]),
            "completed_quests": parse_list_str(data["COMPLETED_QUESTS"])
        }
        
    except ValueError as e:
        # Raised if int() conversion fails (invalid numeric data)
        raise InvalidSaveDataError(f"Invalid numeric value found in save file: {e}")

    # Final structure and type validation
    validate_character_data(character)

    # Apply equipment bonuses immediately after loading
    recalculate_stats(character, item_data_dict)

    return character


def list_saved_characters(save_directory="data/save_games"):
    """
    Returns a list of saved character names by scanning the save folder.
    """

    if not os.path.exists(save_directory):
        return []

    files = os.listdir(save_directory)
    names = []

    # Loop through all files in the directory
    i = 0
    while i < len(files):
        fn = files[i]
        # Check if the file ends with the save suffix
        if fn.endswith("_save.txt"):
            # Manually strip the suffix to get the name
            if len(fn) > 9:
                 names.append(fn[:-9]) 
        i += 1
    return names


# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """
    Gives XP to a character and handles level-ups.
    """
    xp_amount = int(xp_amount)
    
    if is_character_dead(character):
        raise CharacterDeadError(f"{character.get('name')} is dead and cannot gain XP")

    leveled = False

    # Level-up loop
    while True:
        current_level = character["level"]
        needed = current_level * 100 # XP required to level up

        if character["experience"] >= needed:
            character["experience"] -= needed
            character["level"] += 1

            # Increase BASE stats upon leveling
            character["base_health"] += 10
            character["base_strength"] += 2
            character["base_magic"] += 2

            leveled = True
        else:
            break
            
    # When a level up occurs, the new base stats are set.
    # The current health is set to the new max_health (which is the new base_health + equipment bonus).
    if leveled:
        # Note: We rely on the external caller to run recalculate_stats 
        # for proper stat updates including equipment. For simplicity, we update max_health here.
        character["max_health"] = character["base_health"] 
        character["health"] = character["max_health"]

    return leveled

def take_damage(character, damage_amount):
    """
    Applies damage to a character's health, mitigated by defense.
    
    Returns: The actual damage taken (after mitigation).
    """
    damage_amount = int(damage_amount)
    
    # Simple damage reduction calculation
    defense = character.get('defense', 0)
    
    # Calculate reduction factor (e.g., 20 defense gives 1.0 reduction factor)
    reduction_factor = defense * 0.05 
    
    # Cap reduction at a reasonable max (e.g., 80% of damage)
    if reduction_factor > 0.8:
        reduction_factor = 0.8
    
    mitigated_damage = int(damage_amount * reduction_factor)
    actual_damage = damage_amount - mitigated_damage
    
    if actual_damage < 0:
        actual_damage = 0

    character['health'] -= actual_damage

    # Ensure health does not go below zero
    if character['health'] < 0:
        character['health'] = 0
        
    return actual_damage

def recalculate_stats(character, item_data_dict):
    """
    Resets stats to base (level-up) values and applies equipped gear bonuses.
    """
    
    # 1. Reset current stats to Base Stats
    base_h = character.get("base_health", 1)
    base_s = character.get("base_strength", 1)
    base_m = character.get("base_magic", 1)
    
    # Store current health percentage before reset
    old_max_h = character.get('max_health', 1)
    current_health_ratio = character.get('health', 0) / old_max_h if old_max_h > 0 else 1.0

    # Reset current stats to base values
    character['max_health'] = base_h
    character['strength'] = base_s
    character['magic'] = base_m
    character['defense'] = 0
    character['attack'] = 0
    
    # 2. Apply Equipment Bonuses
    equipped_items = []
    if character.get('equipped_weapon'):
        equipped_items.append(character['equipped_weapon'])
    if character.get('equipped_armor'):
        equipped_items.append(character['equipped_armor'])
        
    i = 0
    while i < len(equipped_items):
        item_id = equipped_items[i]
        item_details = item_data_dict.get(item_id)
        
        if item_details:
            effect_string = item_details.get('EFFECT')
            
            if effect_string and ":" in effect_string:
                try:
                    # Manual Parsing: stat_name: value
                    parts = effect_string.split(':', 1)
                    stat_name = parts[0].strip().lower()
                    value_str = parts[1].strip()
                    value = int(value_str)
                    
                    # Apply bonus based on stat name
                    if stat_name == 'max_health':
                        character['max_health'] += value
                    elif stat_name == 'strength':
                        character['strength'] += value
                    elif stat_name == 'magic':
                        character['magic'] += value
                    elif stat_name == 'defense':
                        character['defense'] += value
                    elif stat_name == 'attack':
                        character['attack'] += value
                except ValueError:
                    # Ignore malformed effects where value isn't a number
                    pass
        i += 1

    # 3. Restore Health
    new_max_h = character['max_health']
    restored_health = int(new_max_h * current_health_ratio)
    
    # Ensure health is within bounds (0 to new_max_h)
    if restored_health > new_max_h:
        character['health'] = new_max_h
    elif restored_health < 0:
        character['health'] = 0
    else:
        character['health'] = restored_health
    
    return True

# (Other operations: add_gold, heal_character, is_character_dead, revive_character, validate_character_data)

def add_gold(character, amount):
    """Adds gold to the character."""
    amount = int(amount)
    current = character.get("gold", 0)
    new = current + amount

    if new < 0:
        raise ValueError("Cannot remove more gold than the character possesses.")

    character["gold"] = new
    return new

def heal_character(character, amount):
    """Heals a character, capped at max_health."""
    amount = int(amount)
    max_h = character.get("max_health", 1)
    cur = character.get("health", 0)

    if cur >= max_h or amount <= 0:
        return 0

    space = max_h - cur
    actual = amount
    if amount > space:
        actual = space

    character["health"] = cur + actual
    return actual

def is_character_dead(character):
    """Returns True if the character's health is 0 or less."""
    return character.get("health", 0) <= 0

def revive_character(character):
    """Revives a dead character with half of their maximum health."""
    if not is_character_dead(character):
        return False

    max_h = character.get("max_health", 1)
    half = max_h // 2
    
    if half < 1:
        half = 1

    character["health"] = half
    return True

def validate_character_data(character):
    """Makes sure the character dictionary contains all required fields and types."""

    required = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "base_health", "base_strength", "base_magic",
        "inventory", "active_quests", "completed_quests",
        "equipped_weapon", "equipped_armor"
    ]

    i = 0
    while i < len(required):
        key = required[i]
        if key not in character:
            raise InvalidSaveDataError(f"Missing required field: {key}")
        i += 1

    # Check numeric fields
    nums = ["level", "health", "max_health", "strength", "magic", "experience", "gold", "base_health", "base_strength", "base_magic"]

    i = 0
    while i < len(nums):
        n = nums[i]
        if not isinstance(character[n], int):
            try:
                # Attempt to convert to integer
                character[n] = int(character[n])
            except Exception:
                raise InvalidSaveDataError(f"Field {n} must be an integer or convertible string")
        i += 1

    # Check list fields
    lists = ["inventory", "active_quests", "completed_quests"]
    i = 0
    while i < len(lists):
        l = lists[i]
        if not isinstance(character[l], list):
            raise InvalidSaveDataError(f"Field {l} must be a list")
        i += 1

    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER MODULE TEST ===")
    
    # Mock Item Data for Recalculation Test (needed by load_character and recalculate_stats)
    mock_item_data = {
        "W001": {'NAME': 'Iron Sword', 'TYPE': 'weapon', 'EFFECT': 'strength: 5', 'COST': '50'},
        "A001": {'NAME': 'Leather Vest', 'TYPE': 'armor', 'EFFECT': 'defense: 2', 'COST': '30'},
    }
    
    # --- Test 1: Creation and Stat Check (Rogue) ---
    print("\n--- Test 1: Creation and Equipping ---")
    char = create_character("TestRogue", "Rogue")
    char['equipped_weapon'] = "W001"
    char['equipped_armor'] = "A001"
    
    recalculate_stats(char, mock_item_data)
    print(f"Initial STR: {BASE_STATS_MAP['Rogue']['strength']}, Equipped STR: {char['strength']} (Expected 17)")
    print(f"Equipped DEF: {char['defense']} (Expected 2)")
    
    # --- Test 2: Saving and Loading ---
    print("\n--- Test 2: Saving and Loading ---")
    char['gold'] = 500
    save_character(char)
    print("Character saved successfully.")

    try:
        loaded = load_character("TestRogue", mock_item_data)
        print(f"Loaded Level: {loaded['level']}")
        print(f"Loaded Gold: {loaded['gold']}")
        # Check if stats were correctly recalculated upon loading
        print(f"Loaded Recalculated STR: {loaded['strength']} (Expected 17)") 
        
        # Clean up save file
        os.remove(os.path.join("data/save_games", "TestRogue_save.txt"))
        print("Save file cleaned up.")
    except Exception as e:
        print(f"Load/Delete error: {e}")
        
    print("\n✅ Character Manager module complete.")
