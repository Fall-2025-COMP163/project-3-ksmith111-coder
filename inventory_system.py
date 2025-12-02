"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module

Name: Khalil Smith

AI Usage: I defined the module structure, all required function signatures, 
          and the maximum inventory size. The AI implemented the inventory 
          management logic (add, remove, count, space), item usage (consumables), 
          equipment handling (equip/unequip), shop functions (purchase/sell), 
          and the crucial helper functions (parse_item_effect, apply_stat_effect) 
          while adhering to all constraints and exception requirements.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory
    
    Raises: InventoryFullError if inventory is at max capacity
    """
    inventory_list = character.get('inventory', [])
    
    # Check if inventory is full (>= MAX_INVENTORY_SIZE)
    if len(inventory_list) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError(f"Inventory is full. Max capacity is {MAX_INVENTORY_SIZE}.")
    
    # Add item_id to character['inventory'] list
    inventory_list.append(item_id)
    character['inventory'] = inventory_list
    return True

def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory
    
    Raises: ItemNotFoundError if item not in inventory
    """
    inventory_list = character.get('inventory', [])

    # Check if item exists in inventory
    if item_id not in inventory_list:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    
    # Remove item from list (only the first occurrence)
    
    # Implementation using loop to avoid list.remove()
    new_inventory = []
    removed = False
    i = 0
    while i < len(inventory_list):
        current_item = inventory_list[i]
        # Only skip the first match
        if current_item == item_id and not removed:
            removed = True
        else:
            new_inventory.append(current_item)
        i += 1

    character['inventory'] = new_inventory
    return True

def has_item(character, item_id):
    """
    Check if character has a specific item
    """
    # Check if item in character['inventory'] list
    return item_id in character.get('inventory', [])

def count_item(character, item_id):
    """
    Count how many of a specific item the character has
    
    Returns: Integer count of item
    """
    inventory_list = character.get('inventory', [])
    count = 0
    
    # Loop through the list to count occurrences (using list.count is allowed here)
    # Note: Using list.count() if allowed, otherwise:
    i = 0
    while i < len(inventory_list):
        if inventory_list[i] == item_id:
            count += 1
        i += 1
        
    return count

def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory
    
    Returns: Integer representing available slots
    """
    # Calculate available slots
    current_size = len(character.get('inventory', []))
    space_remaining = MAX_INVENTORY_SIZE - current_size
    
    if space_remaining < 0:
        return 0
    return space_remaining

def clear_inventory(character):
    """
    Remove all items from inventory
    
    Returns: List of removed items
    """
    # Save current inventory before clearing
    removed_items = character.get('inventory', [])[:] # Use slicing for a copy
    
    # Clear character's inventory list
    character['inventory'] = []
    
    return removed_items

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    """
    Parse item effect string into stat name and value
    
    Args:
        effect_string: String in format "stat_name:value"
    
    Returns: Tuple of (stat_name, value)
    """
    if ': ' not in effect_string:
        raise InvalidItemTypeError(f"Effect string format is invalid: {effect_string}")
        
    # Split on ":"
    parts = effect_string.split(': ', 1)
    stat_name = parts[0].strip().lower()
    value_str = parts[1].strip()
    
    try:
        # Convert value to integer
        value = int(value_str)
    except ValueError:
        raise InvalidItemTypeError(f"Effect value is not a number: {value_str}")
        
    return (stat_name, value)

def apply_stat_effect(character, stat_name, value):
    """
    Apply a stat modification to character
    
    Note: health cannot exceed max_health
    """
    
    if stat_name in ['health', 'max_health', 'strength', 'magic', 'defense', 'attack', 'gold', 'experience']:
        # Add value to character[stat_name]
        current_value = character.get(stat_name, 0)
        character[stat_name] = current_value + value
        
        # If stat is health, ensure it doesn't exceed max_health
        if stat_name == 'health':
            max_h = character.get('max_health', 1)
            if character['health'] > max_h:
                character['health'] = max_h
            if character['health'] < 0:
                character['health'] = 0
                
        # Ensure max_health doesn't go below 1
        if stat_name == 'max_health' and character['max_health'] < 1:
            character['max_health'] = 1
            
# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item from inventory
    
    Raises: 
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'consumable'
    """
    
    # 1. Check if character has the item
    if item_id not in character.get('inventory', []):
        raise ItemNotFoundError(f"Cannot use item '{item_id}': not found in inventory.")
        
    item_type = item_data.get('TYPE', '').lower()
    
    # 2. Check if item type is 'consumable'
    if item_type != 'consumable':
        # weapon/armor: Cannot be "used", only equipped
        raise InvalidItemTypeError(f"Cannot use item '{item_id}': type is '{item_type}', must be 'consumable'.")

    effect_string = item_data.get('EFFECT', '')
    
    try:
        # 3. Parse effect (format: "stat_name:value")
        stat_name, value = parse_item_effect(effect_string)
        
        # 4. Apply effect to character
        apply_stat_effect(character, stat_name, value)
        
        # 5. Remove item from inventory
        remove_item_from_inventory(character, item_id)
        
        item_name = item_data.get('NAME', item_id)
        return f"Used {item_name}. {stat_name.capitalize()} modified by {value}."
        
    except InvalidItemTypeError as e:
        # Re-raise parsing error
        raise e
    except Exception as e:
        # Catch unexpected errors during application
        raise Exception(f"Failed to apply effect of item '{item_id}': {e}")


def equip_weapon(character, item_id, item_data, recalculate_stats_func):
    """
    Equip a weapon
    
    Note: Requires the recalculate_stats function (from character_manager) 
    to be passed in to update stats.
    
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'weapon'
    """
    
    # 1. Check item exists and is type 'weapon'
    if item_id not in character.get('inventory', []):
        raise ItemNotFoundError(f"Cannot equip item '{item_id}': not found in inventory.")
        
    item_type = item_data.get('TYPE', '').lower()
    
    if item_type != 'weapon':
        raise InvalidItemTypeError(f"Cannot equip item '{item_id}': type is '{item_type}', must be 'weapon'.")
        
    old_weapon_id = character.get('equipped_weapon')
    
    # 2. Handle unequipping current weapon if exists
    if old_weapon_id and old_weapon_id != "NONE":
        # Add old weapon back to inventory
        add_item_to_inventory(character, old_weapon_id)
        
    # 3. Store equipped_weapon and remove item from inventory
    character['equipped_weapon'] = item_id
    remove_item_from_inventory(character, item_id)
    
    # 4. Recalculate stats to apply new bonus and remove old bonus
    recalculate_stats_func(character, item_data) 
    
    item_name = item_data.get('NAME', item_id)
    result = f"Equipped {item_name}."
    if old_weapon_id and old_weapon_id != "NONE":
        result += f" Unequipped {old_weapon_id} and placed in inventory."
        
    return result


def equip_armor(character, item_id, item_data, recalculate_stats_func):
    """
    Equip armor
    
    Note: Requires the recalculate_stats function (from character_manager) 
    to be passed in to update stats.
    
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'armor'
    """
    
    # 1. Check item exists and is type 'armor'
    if item_id not in character.get('inventory', []):
        raise ItemNotFoundError(f"Cannot equip item '{item_id}': not found in inventory.")
        
    item_type = item_data.get('TYPE', '').lower()
    
    if item_type != 'armor':
        raise InvalidItemTypeError(f"Cannot equip item '{item_id}': type is '{item_type}', must be 'armor'.")
        
    old_armor_id = character.get('equipped_armor')
    
    # 2. Handle unequipping current armor if exists
    if old_armor_id and old_armor_id != "NONE":
        # Add old armor back to inventory
        add_item_to_inventory(character, old_armor_id)
        
    # 3. Store equipped_armor and remove item from inventory
    character['equipped_armor'] = item_id
    remove_item_from_inventory(character, item_id)
    
    # 4. Recalculate stats to apply new bonus and remove old bonus
    recalculate_stats_func(character, item_data) 
    
    item_name = item_data.get('NAME', item_id)
    result = f"Equipped {item_name}."
    if old_armor_id and old_armor_id != "NONE":
        result += f" Unequipped {old_armor_id} and placed in inventory."
        
    return result


def unequip_weapon(character, recalculate_stats_func):
    """
    Remove equipped weapon and return it to inventory
    
    Raises: InventoryFullError if inventory is full
    """
    old_weapon_id = character.get('equipped_weapon')

    # Check if weapon is equipped
    if not old_weapon_id or old_weapon_id == "NONE":
        return None

    # Check for space before unequip
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full. Cannot unequip weapon.")

    # Add weapon back to inventory
    add_item_to_inventory(character, old_weapon_id)
    
    # Clear equipped_weapon from character
    character['equipped_weapon'] = "NONE"

    # Remove stat bonuses (by calling recalculate_stats)
    recalculate_stats_func(character, {}) 
    
    return old_weapon_id


def unequip_armor(character, recalculate_stats_func):
    """
    Remove equipped armor and return it to inventory
    
    Raises: InventoryFullError if inventory is full
    """
    old_armor_id = character.get('equipped_armor')

    if not old_armor_id or old_armor_id == "NONE":
        return None

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full. Cannot unequip armor.")

    add_item_to_inventory(character, old_armor_id)
    
    character['equipped_armor'] = "NONE"

    recalculate_stats_func(character, {}) 
    
    return old_armor_id

# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data, add_gold_func):
    """
    Purchase an item from a shop
    
    Note: Requires the add_gold function (from character_manager) to be passed in.
    
    Raises:
        InsufficientResourcesError if not enough gold
        InventoryFullError if inventory is full
    """
    
    cost_str = item_data.get('COST')
    try:
        cost = int(cost_str)
    except ValueError:
        raise InvalidItemTypeError(f"Item cost is invalid: {cost_str}")
    
    # 1. Check if inventory has space
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full. Cannot purchase item.")
        
    # 2. Check if character has enough gold
    if character.get('gold', 0) < cost:
        raise InsufficientResourcesError(f"Need {cost} gold to purchase, but only have {character.get('gold')}.")

    # 3. Subtract gold from character
    add_gold_func(character, -cost)
    
    # 4. Add item to inventory
    add_item_to_inventory(character, item_id)
    
    return True


def sell_item(character, item_id, item_data, add_gold_func):
    """
    Sell an item for half its purchase cost
    
    Note: Requires the add_gold function (from character_manager) to be passed in.
    
    Raises: ItemNotFoundError if item not in inventory
    """
    
    # 1. Check if character has item
    if item_id not in character.get('inventory', []):
        raise ItemNotFoundError(f"Cannot sell item '{item_id}': not found in inventory.")
        
    cost_str = item_data.get('COST')
    try:
        cost = int(cost_str)
    except ValueError:
        raise InvalidItemTypeError(f"Item cost is invalid: {cost_str}")
        
    # 2. Calculate sell price (cost // 2)
    sell_price = cost // 2
    
    # 3. Remove item from inventory
    remove_item_from_inventory(character, item_id)
    
    # 4. Add gold to character
    add_gold_func(character, sell_price)
    
    return sell_price

# ============================================================================
# DISPLAY FUNCTION
# ============================================================================

def display_inventory(character, item_data_dict):
    """
    Display character's inventory in formatted way
    
    Shows item names, types, and quantities
    """
    inventory_list = character.get('inventory', [])
    
    # 1. Count items (some may appear multiple times)
    counted_items = {}
    i = 0
    while i < len(inventory_list):
        item_id = inventory_list[i]
        if item_id in counted_items:
            counted_items[item_id] += 1
        else:
            counted_items[item_id] = 1
        i += 1
        
    output = "\n--- Inventory ---\n"
    
    if not counted_items:
        output += "Inventory is empty.\n"
        return output

    # 2. Display with item names from item_data_dict
    keys = list(counted_items.keys())
    i = 0
    while i < len(keys):
        item_id = keys[i]
        count = counted_items[item_id]
        
        item_info = item_data_dict.get(item_id)
        
        if item_info:
            name = item_info.get('NAME', 'Unknown Item')
            item_type = item_info.get('TYPE', 'N/A').upper()
            output += f"[{item_type}] {name} x{count}\n"
        else:
            output += f"[N/A] Unknown Item ({item_id}) x{count}\n"
        i += 1
        
    output += "-----------------\n"
    output += f"Space: {len(inventory_list)}/{MAX_INVENTORY_SIZE} ({get_inventory_space_remaining(character)} slots remaining)\n"
    
    return output


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
    
    # Test adding items
    # test_char = {'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80}
    # 
    # try:
    #     add_item_to_inventory(test_char, "health_potion")
    #     print(f"Inventory: {test_char['inventory']}")
    # except InventoryFullError:
    #     print("Inventory is full!")
    
    # Test using items
    # test_item = {
    #     'item_id': 'health_potion',
    #     'type': 'consumable',
    #     'effect': 'health:20'
    # }
    # 
    # try:
    #     result = use_item(test_char, "health_potion", test_item)
    #     print(result)
    # except ItemNotFoundError:
    #     print("Item not found")
