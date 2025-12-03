"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module

Name: Khalil Smith

AI Usage: I defined the base character structure, class names, and all core function signatures. 
          The AI assisted with implementing the detailed file I/O logic, including manual string 
          parsing for loading key-value pairs and converting list data (inventory, quests). 
          The AI also implemented the stat management functions (gain_experience, take_damage, etc.) 
          and ensures correct exception handling as required by the project.
"""

import os
import shutil 
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# Base stats for the four required classes
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
    Create a new character with stats based on class
    
    Raises: InvalidCharacterClassError if class is not valid
    """
    valid_classes = list(BASE_STATS_MAP.keys())

    if character_class not in valid_classes:
        # Validate character_class first
        raise InvalidCharacterClassError(f"Invalid class: {character_class}. Must be one of {valid_classes}")

    stats = BASE_STATS_MAP[character_class]
    
    # Initialize character dictionary
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
        
        # Current Calculated Stats
        "health": stats["health"],
        "max_health": stats["health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "defense": 0, 
        "attack": 0, 
        
        # Inventory and Quests
        "inventory": [],
        "equipped_weapon": "NONE",
        "equipped_armor": "NONE",
        "active_quests": [],
        "completed_quests": []
    }

    return character


def save_character(character, save_directory="data/save_games"):
    """
    Save character to file
    """

    if not os.path.exists(save_directory):
        os.makedirs(save_directory, exist_ok=True)

    filename = os.path.join(save_directory, f"{character['name']}_save.txt")

    # Helper function to convert list fields into comma-separated strings
    def list_to_str(key):
        # Lists should be saved as comma-separated values
        return ",".join(character.get(key, [])) or "NONE"

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
        ("EQUIPPED_WEAPON", character.get("equipped_weapon") or "NONE"),
        ("EQUIPPED_ARMOR", character.get("equipped_armor") or "NONE"),
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
        # Handle any file I/O errors appropriately
        raise SaveFileCorruptedError(f"Failed to write save file: {e}")

    return True


def load_character(character_name, save_directory="data/save_games"):
    """
    Load character from save file
    
    Raises: CharacterNotFoundError, SaveFileCorruptedError, InvalidSaveDataError
    """

    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    # Check if file exists → CharacterNotFoundError
    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save file found for '{character_name}'")

    data = {}
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            # Try to read file → SaveFileCorruptedError
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Validate data format → InvalidSaveDataError
                if ": " not in line:
                    raise InvalidSaveDataError(f"Invalid line in save file for '{character_name}': missing ': ' separator.")
                    
                # Parse the key and value
                parts = line.split(": ", 1)
                key = parts[0].strip().upper()
                val = parts[1].strip()
                data[key] = val
                
    except InvalidSaveDataError:
        raise
    except Exception as e:
        raise SaveFileCorruptedError(f"Could not read or parse save file: {e}")

    # Validation step 1: Check for critical missing keys
    required_keys = [
        "NAME", "CLASS", "LEVEL", "HEALTH", "MAX_HEALTH",
        "STRENGTH", "MAGIC", "EXPERIENCE", "GOLD",
        "BASE_HEALTH", "BASE_STRENGTH", "BASE_MAGIC", 
        "EQUIPPED_WEAPON", "EQUIPPED_ARMOR",
        "INVENTORY", "ACTIVE_QUESTS", "COMPLETED_QUESTS"
    ]
    
    i = 0
    while i < len(required_keys):
        key = required_keys[i]
        if key not in data:
             raise InvalidSaveDataError(f"Critical field missing from save file: {key}")
        i += 1


    try:
        # Helper function to parse saved string lists (comma-separated)
        def parse_list_str(s):
            # Parse comma-separated lists back into Python lists
            return [] if s.upper() in ("", "NONE") else s.split(",")

        # Helper to parse equipment (NONE -> None)
        def parse_equipment_str(s):
            return None if s.upper() in ("", "NONE") else s

        # Rebuild character dictionary
        character = {
            "name": data["NAME"],
            "class": data["CLASS"],
            "level": int(data["LEVEL"]),
            "health": int(data["HEALTH"]),
            "max_health": int(data["MAX_HEALTH"]),
            "strength": int(data["STRENGTH"]),
            "magic": int(data["MAGIC"]),
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
        # Catch errors from int() conversion
        raise InvalidSaveDataError(f"Invalid numeric value found in save file: {e}")

    # Final structure and type validation
    validate_character_data(character)

    return character


def list_saved_characters(save_directory="data/save_games"):
    """
    Get list of all saved character names
    """

    if not os.path.exists(save_directory):
        # Return empty list if directory doesn't exist
        return []

    files = os.listdir(save_directory)
    names = []

    # Loop through all files in the directory
    i = 0
    while i < len(files):
        fn = files[i]
        # Check if the file ends with the save suffix
        if fn.endswith("_save.txt"):
            # Extract character names from filenames
            if len(fn) > 9: 
                 names.append(fn[:-9]) 
        i += 1
    return names

def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file
    """
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    # Verify file exists before attempting deletion
    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save file found for '{character_name}' to delete.")

    try:
        os.remove(filename)
    except Exception as e:
        # Catch unexpected errors like permission issues during deletion
        raise SaveFileCorruptedError(f"Failed to delete save file '{character_name}': {e}")
    
    return True

# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """
    Add experience to character and handle level ups
    
    Raises: CharacterDeadError if character health is 0
    """
    xp_amount = int(xp_amount)
    
    # Check if character is dead first
    if is_character_dead(character):
        raise CharacterDeadError(f"{character.get('name')} is dead and cannot gain XP")

    leveled = False
    character["experience"] += xp_amount

    # Level-up loop
    while True:
        current_level = character["level"]
        needed = current_level * 100 # Level up formula: level_up_xp = current_level * 100

        if character["experience"] >= needed:
            character["experience"] -= needed
            character["level"] += 1

            # Update stats on level up
            character["base_health"] += 10
            character["base_strength"] += 2
            character["base_magic"] += 2
            
            # Update current stats to reflect the new base values
            character["max_health"] = character["base_health"]
            character["strength"] = character["base_strength"]
            character["magic"] = character["base_magic"]

            leveled = True
        else:
            break
            
    # Restore health to full max_health after leveling (before equipment recalculation)
    if leveled:
        character["health"] = character["max_health"]

    return leveled

def add_gold(character, amount):
    """
    Add gold to character's inventory
    """
    amount = int(amount)
    current = character.get("gold", 0)
    new = current + amount

    if new < 0:
        # Raise ValueError if result would be negative
        raise ValueError(f"Cannot perform transaction: removing {abs(amount)} gold would result in negative total.")

    character["gold"] = new
    return new

def heal_character(character, amount):
    """
    Heal character by specified amount
    """
    amount = int(amount)
    max_h = character.get("max_health", 1)
    cur = character.get("health", 0)

    if cur >= max_h or amount <= 0:
        return 0

    space = max_h - cur
    actual = amount
    if amount > space:
        # Health cannot exceed max_health
        actual = space

    character["health"] = cur + actual
    return actual

def is_character_dead(character):
    """
    Check if character's health is 0 or below
    """
    # Returns: True if dead, False if alive
    return character.get("health", 0) <= 0

def revive_character(character):
    """
    Revive a dead character with 50% health
    """
    if not is_character_dead(character):
        return False

    max_h = character.get("max_health", 1)
    # Restore health to half of max_health
    half = max_h // 2
    
    if half < 1:
        half = 1

    character["health"] = half
    return True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """
    Validate that character dictionary has all required fields
    
    Raises: InvalidSaveDataError if missing fields or invalid types
    """

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
            # Check all required keys exist
            raise InvalidSaveDataError(f"Missing required field: {key}")
        i += 1

    # Check numeric fields
    nums = ["level", "health", "max_health", "strength", "magic", "experience", "gold", "base_health", "base_strength", "base_magic"]

    i = 0
    while i < len(nums):
        n = nums[i]
        if not isinstance(character[n], int):
            try:
                # Check that numeric values are numbers
                character[n] = int(character[n])
            except Exception:
                raise InvalidSaveDataError(f"Field {n} must be an integer, but contains: {character[n]}")
        i += 1

    # Check list fields
    lists = ["inventory", "active_quests", "completed_quests"]
    i = 0
    while i < len(lists):
        l = lists[i]
        if not isinstance(character[l], list):
            # Check that lists are actually lists
            raise InvalidSaveDataError(f"Field {l} must be a list")
        i += 1

    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    # Test character creation
    # try:
    #     char = create_character("TestHero", "Warrior")
    #     print(f"Created: {char['name']} the {char['class']}")
    #     print(f"Stats: HP={char['health']}, STR={char['strength']}, MAG={char['magic']}")
    # except InvalidCharacterClassError as e:
    #     print(f"Invalid class: {e}")
    
    # Test saving
    # try:
    #     save_character(char)
    #     print("Character saved successfully")
    # except Exception as e:
    #     print(f"Save error: {e}")
    
    # Test loading
    # try:
    #     loaded = load_character("TestHero")
    #     print(f"Loaded: {loaded['name']}")
    # except CharacterNotFoundError:
    #     print("Character not found")
    # except SaveFileCorruptedError:
<<<<<<< HEAD
    #     print("Save file corrupted")
=======
    #     print("Save file corrupted")
>>>>>>> effbbc7ea9df0b4db805e3ed41175a57fcc9c474
