"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Completed Code

Name: Khalil Smith

AI Usage: I defined the module structure and integration points. The AI 
          implemented the main menu and game loop logic, handling user input, 
          managing the global state (current_character), and orchestrating 
          calls to all imported modules (character_manager, inventory_system, 
          quest_handler, combat_system) while incorporating necessary error 
          handling for file operations and game mechanics exceptions.
"""

# Import all our custom modules
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *
import os # For file operations in game loading
import sys # For graceful exit

# ============================================================================
# GAME STATE
# ============================================================================

# Global variables for game data
current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """
    Display main menu and get player choice
    
    Returns: Integer choice (1-3)
    """
    while True:
        print("\n--- Main Menu ---")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")
        
        try:
            choice = input("Enter your choice (1-3): ").strip()
            choice_int = int(choice)
            if 1 <= choice_int <= 3:
                return choice_int
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def new_game():
    """
    Start a new game
    """
    global current_character
    
    print("\n--- New Game ---")
    
    # Get character name from user
    name = input("Enter your character's name: ").strip()
    if not name:
        print("Character creation cancelled.")
        return
        
    # Get character class from user
    print("\nAvailable Classes:")
    print("1. Warrior (Strength focus)")
    print("2. Mage (Magic focus)")
    print("3. Rogue (High damage chance)")
    print("4. Cleric (Healing focus)")
    
    class_map = {'1': 'Warrior', '2': 'Mage', '3': 'Rogue', '4': 'Cleric'}
    
    while True:
        class_choice = input("Select your class (1-4): ").strip()
        selected_class = class_map.get(class_choice)
        
        if selected_class:
            break
        else:
            print("Invalid class choice. Please select 1, 2, 3, or 4.")
            
    try:
        # Create character
        current_character = character_manager.create_character(name, selected_class)
        print(f"\nWelcome, {current_character['name']} the {current_character['class']}!")
        
        # Start game loop
        game_loop()
        
    except InvalidCharacterClassError as e:
        print(f"Error creating character: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during character creation: {e}")

def load_game():
    """
    Load an existing saved game
    """
    global current_character
    
    print("\n--- Load Game ---")
    
    # Get list of saved characters
    try:
        saved_chars = character_manager.get_saved_characters()
    except Exception:
        print("Error accessing save directory.")
        saved_chars = []

    if not saved_chars:
        print("No saved characters found.")
        return

    print("Saved Characters:")
    for i, name in enumerate(saved_chars):
        print(f"{i + 1}. {name}")
    
    while True:
        try:
            choice = input("Select character number to load, or 'c' to cancel: ").strip().lower()
            if choice == 'c':
                return
            
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(saved_chars):
                selected_name = saved_chars[choice_index]
                break
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a number or 'c'.")
            
    try:
        # Try to load character
        current_character = character_manager.load_character(selected_name)
        print(f"\nSuccessfully loaded {current_character['name']}.")
        
        # Start game loop
        game_loop()
        
    except CharacterNotFoundError:
        print(f"Error: Save file for '{selected_name}' not found.")
    except SaveFileCorruptedError as e:
        print(f"Error: Save file for '{selected_name}' is corrupted: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during loading: {e}")

# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    """
    Main game loop - shows game menu and processes actions
    """
    global game_running, current_character
    
    game_running = True
    
    while game_running:
        try:
            # Check for death after any action
            if current_character['health'] <= 0:
                handle_character_death()
                if not game_running:
                    break
            
            # Display game menu
            choice = game_menu()
            
            # Execute chosen action
            if choice == 1:
                view_character_stats()
            elif choice == 2:
                view_inventory()
            elif choice == 3:
                quest_menu()
            elif choice == 4:
                explore()
            elif choice == 5:
                shop()
            elif choice == 6:
                save_game()
                game_running = False
            else:
                print("Invalid choice. Please select 1-6.")
            
            # Save game after each action (except for Save and Quit, which handles it)
            if game_running and choice != 6:
                save_game()
                
        except Exception as e:
            # Catch general unhandled exceptions during gameplay
            print(f"\n[SYSTEM ERROR] An unexpected error occurred: {e}")
            print("Saving game state before returning to main menu.")
            save_game()
            game_running = False


def game_menu():
    """
    Display game menu and get player choice
    
    Returns: Integer choice (1-6)
    """
    while True:
        print("\n--- Game Menu ---")
        print("1. View Character Stats")
        print("2. View Inventory")
        print("3. Quest Menu")
        print("4. Explore (Find Battles)")
        print("5. Shop")
        print("6. Save and Quit")
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            choice_int = int(choice)
            if 1 <= choice_int <= 6:
                return choice_int
            else:
                print("Invalid choice. Please select 1-6.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# ============================================================================
# GAME ACTIONS
# ============================================================================

def view_character_stats():
    """Display character information"""
    global current_character
    
    character_manager.display_character_stats(current_character)
    quest_handler.display_character_quest_progress(current_character, all_quests)


def view_inventory():
    """Display and manage inventory"""
    global current_character, all_items
    
    while True:
        print(inventory_system.display_inventory(current_character, all_items))
        
        if not current_character.get('inventory'):
            return # Exit if inventory is empty
            
        print("Inventory Options:")
        print("1. Use Consumable")
        print("2. Equip Weapon/Armor")
        print("3. Back")
        
        choice = input("Enter choice (1-3): ").strip()

        if choice == '3':
            return
        elif choice in ('1', '2'):
            item_id = input("Enter item ID (e.g., 'health_potion'): ").strip()
            item_data = all_items.get(item_id)
            
            if not item_data:
                print(f"Error: Item ID '{item_id}' not found in item data.")
                continue

            try:
                if choice == '1':
                    print(inventory_system.use_item(current_character, item_id, item_data))
                elif choice == '2':
                    item_type = item_data.get('TYPE', '').lower()
                    
                    # NOTE: Assuming character_manager has a recalculate_stats function
                    recalc_func = character_manager.recalculate_stats 

                    if item_type == 'weapon':
                        print(inventory_system.equip_weapon(current_character, item_id, item_data, recalc_func))
                    elif item_type == 'armor':
                        print(inventory_system.equip_armor(current_character, item_id, item_data, recalc_func))
                    else:
                        raise InvalidItemTypeError(f"Item '{item_id}' is not a weapon or armor.")
                        
            except (ItemNotFoundError, InvalidItemTypeError, InventoryFullError) as e:
                print(f"[INVENTORY ERROR] {e}")
            except Exception as e:
                print(f"[SYSTEM ERROR] Could not perform action: {e}")
        else:
            print("Invalid inventory option.")

def quest_menu():
    """Quest management menu"""
    global current_character, all_quests
    
    while True:
        print("\n--- Quest Menu ---")
        print("1. View Active Quests")
        print("2. View Available Quests")
        print("3. Accept Quest")
        print("4. Abandon Quest")
        print("5. Complete Quest (DEBUG)")
        print("6. Back")
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == '6':
            return
        elif choice == '1':
            quest_handler.display_quest_list(quest_handler.get_active_quests(current_character, all_quests))
        elif choice == '2':
            quest_handler.display_quest_list(quest_handler.get_available_quests(current_character, all_quests))
        elif choice == '3':
            quest_id = input("Enter Quest ID to accept: ").strip()
            try:
                if quest_handler.accept_quest(current_character, quest_id, all_quests):
                    print(f"Quest '{quest_id}' accepted!")
            except (QuestNotFoundError, InsufficientLevelError, QuestRequirementsNotMetError, QuestAlreadyCompletedError) as e:
                print(f"[QUEST ERROR] Could not accept quest: {e}")
        elif choice == '4':
            quest_id = input("Enter Quest ID to abandon: ").strip()
            try:
                if quest_handler.abandon_quest(current_character, quest_id):
                    print(f"Quest '{quest_id}' abandoned.")
            except QuestNotActiveError as e:
                print(f"[QUEST ERROR] Could not abandon quest: {e}")
        elif choice == '5':
            # DEBUG OPTION: Completes an active quest
            quest_id = input("Enter Quest ID to COMPLETE: ").strip()
            try:
                rewards = quest_handler.complete_quest(current_character, quest_id, all_quests)
                print(f"Quest '{quest_id}' completed! Rewards: {rewards['reward_xp']} XP, {rewards['reward_gold']} Gold.")
            except (QuestNotFoundError, QuestNotActiveError) as e:
                print(f"[QUEST ERROR] Could not complete quest: {e}")
        else:
            print("Invalid quest menu option.")

def explore():
    """Find and fight random enemies"""
    global current_character
    
    print("\n--- Exploring the Wilds ---")
    
    if not character_manager.can_character_fight(current_character):
        print("You are too wounded to explore right now.")
        return
        
    try:
        # Generate random enemy based on character level
        enemy = combat_system.get_random_enemy_for_level(current_character.get('level', 1))
        
        # Start combat
        battle = combat_system.SimpleBattle(current_character, enemy)
        
        print(f"You encounter a dangerous {enemy['name']}!")
        
        # Start battle and handle results
        results = battle.start_battle()
        
        if results['winner'] == 'player':
            # Grant rewards using character manager functions
            character_manager.gain_experience(current_character, results['xp_gained'])
            character_manager.add_gold(current_character, results['gold_gained'])
            character_manager.check_for_level_up(current_character)
            
        elif results['winner'] == 'enemy':
            # Character died, let the main loop handle death
            pass 
        
    except InvalidTargetError as e:
        print(f"[EXPLORE ERROR] Could not create enemy: {e}")
    except CharacterDeadError as e:
        print(f"[COMBAT ERROR] Cannot start combat: {e}")
    except Exception as e:
        print(f"[SYSTEM ERROR] An error occurred during exploration: {e}")


def shop():
    """Shop menu for buying/selling items"""
    global current_character, all_items
    
    # NOTE: In a real game, this would filter for only 'shop' items.
    shop_items = [v for k, v in all_items.items() if v.get('COST') is not None] 
    
    while True:
        print("\n--- The General Store ---")
        print(f"Current Gold: {current_character.get('gold', 0)}")
        print("Options: 1. Buy | 2. Sell | 3. Back")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '3':
            return
        
        elif choice == '1': # Buy Item
            print("\nItems for Sale:")
            # Display items in a simple format
            for item in shop_items:
                print(f"- {item['NAME']} ({item['ITEM_ID']}): {item['COST']} Gold")

            buy_id = input("Enter Item ID to buy: ").strip()
            item_data = all_items.get(buy_id)
            if not item_data:
                print("Item not found.")
                continue

            try:
                # NOTE: Assuming character_manager has add_gold function
                add_gold_func = character_manager.add_gold 
                if inventory_system.purchase_item(current_character, buy_id, item_data, add_gold_func):
                    print(f"Purchased {item_data['NAME']} for {item_data['COST']} gold.")
            except (InsufficientResourcesError, InventoryFullError, InvalidItemTypeError) as e:
                print(f"[SHOP ERROR] Purchase failed: {e}")

        elif choice == '2': # Sell Item
            print(inventory_system.display_inventory(current_character, all_items))
            sell_id = input("Enter Item ID to sell: ").strip()
            item_data = all_items.get(sell_id)
            if not item_data:
                print("Item not found.")
                continue
            
            try:
                # NOTE: Assuming character_manager has add_gold function
                add_gold_func = character_manager.add_gold 
                sell_price = inventory_system.sell_item(current_character, sell_id, item_data, add_gold_func)
                print(f"Sold {item_data['NAME']} for {sell_price} gold.")
            except (ItemNotFoundError, InvalidItemTypeError) as e:
                print(f"[SHOP ERROR] Sale failed: {e}")

        else:
            print("Invalid shop option.")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_game():
    """Save current game state"""
    global current_character
    
    if current_character:
        try:
            character_manager.save_character(current_character)
            print(f"\nGame saved for {current_character['name']}.")
        except Exception as e:
            print(f"[SAVE ERROR] Failed to save game: {e}")


def load_game_data():
    """Load all quest and item data from files"""
    global all_quests, all_items
    
    # Try to load quests
    all_quests = game_data.load_quests()
    
    # Try to load items
    all_items = game_data.load_items()


def handle_character_death():
    """Handle character death"""
    global current_character, game_running
    
    print("\n" + "=" * 50)
    print(f"              {current_character['name']} HAS FALLEN!")
    print("=" * 50)
    
    revive_cost = 50 * current_character.get('level', 1)
    current_gold = current_character.get('gold', 0)
    
    while True:
        print(f"Current Gold: {current_gold}")
        print(f"1. Revive at town (Cost: {revive_cost} Gold)")
        print("2. Quit Game (Character remains dead)")
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == '1':
            if current_gold >= revive_cost:
                try:
                    character_manager.revive_character(current_character, revive_cost)
                    print(f"\n{current_character['name']} is revived! Lost {revive_cost} gold.")
                    return # Exit death loop
                except InsufficientResourcesError as e:
                    # Should be caught by the gold check, but as a safeguard
                    print(f"[REVIVE ERROR] {e}")
            else:
                print(f"You do not have enough gold to revive. Need {revive_cost}.")
        elif choice == '2':
            print("\nGame Over. Farewell, hero.")
            game_running = False
            return # Exit death loop
        else:
            print("Invalid choice.")


def display_welcome():
    """Display welcome message"""
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!")
    print()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main game execution function"""
    
    # Display welcome message
    display_welcome()
    
    # Load game data
    try:
        load_game_data()
        
        # Post-load validation (e.g., check quest prerequisites)
        quest_handler.validate_quest_prerequisites(all_quests) 
        
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Creating default game data...")
        game_data.create_default_data_files()
        
        # Attempt to load again after creating files
        try:
            load_game_data()
            quest_handler.validate_quest_prerequisites(all_quests)
            print("Default game data created and loaded successfully!")
        except Exception as e:
            print(f"FATAL ERROR: Failed to load default data: {e}")
            return
            
    except InvalidDataFormatError as e:
        print(f"FATAL ERROR: Error loading game data: {e}")
        print("Please check data files for errors.")
        return
    except QuestNotFoundError as e:
        print(f"FATAL ERROR: Data validation failed: {e}")
        return
    
    # Main menu loop
    while True:
        choice = main_menu()
        
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break
        else:
            print("Invalid choice. Please select 1-3.")

if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> effbbc7ea9df0b4db805e3ed41175a57fcc9c474
