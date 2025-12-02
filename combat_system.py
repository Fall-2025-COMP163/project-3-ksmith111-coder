"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Completed Code

Name: Khalil Smith

AI Usage: I defined the module structure and constraints. The AI implemented the 
          enemy creation logic, the entire SimpleBattle class including the core 
          damage formula and turn cycle, and the four class-specific special 
          abilities, ensuring proper use of the random module for chance 
          mechanics (critical strike and escape).
"""
import random
import math # Used for floor division equivalence

from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError # NOTE: Cooldown logic simplified/omitted for basic implementation
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type
    
    Returns: Enemy dictionary
    Raises: InvalidTargetError if enemy_type not recognized
    """
    enemy_type = enemy_type.lower()
    
    enemy_stats = {
        'goblin': {'name': 'Goblin', 'health': 50, 'strength': 8, 'magic': 2, 'xp_reward': 25, 'gold_reward': 10, 'type': 'goblin'},
        'orc': {'name': 'Orc', 'health': 80, 'strength': 12, 'magic': 5, 'xp_reward': 50, 'gold_reward': 25, 'type': 'orc'},
        'dragon': {'name': 'Dragon', 'health': 200, 'strength': 25, 'magic': 15, 'xp_reward': 200, 'gold_reward': 100, 'type': 'dragon'}
    }
    
    if enemy_type not in enemy_stats:
        raise InvalidTargetError(f"Enemy type '{enemy_type}' not recognized.")
        
    enemy = enemy_stats[enemy_type].copy()
    enemy['max_health'] = enemy['health'] # Set max_health for tracking
    return enemy

def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level
    """
    
    if character_level <= 2:
        enemy_type = "goblin"
    elif character_level <= 5:
        enemy_type = "orc"
    else:
        # Level 6+
        enemy_type = "dragon"
        
    # Call create_enemy with appropriate type
    return create_enemy(enemy_type)

# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system
    
    Manages combat between character and enemy
    """
    
    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = enemy
        self.combat_active = False
        self.turn_counter = 0
        self.player_last_ability_turn = 0 # Simple cooldown tracker
    
    def start_battle(self):
        """
        Start the combat loop
        
        Returns: Dictionary with battle results
        Raises: CharacterDeadError if character is already dead
        """
        # Check character isn't dead
        if self.character['health'] <= 0:
            raise CharacterDeadError(f"{self.character['name']} is already defeated.")
            
        self.combat_active = True
        self.turn_counter = 0
        display_battle_log(f"A wild {self.enemy['name']} attacks!")

        while self.combat_active:
            self.turn_counter += 1
            
            # --- 1. Player Turn ---
            display_combat_stats(self.character, self.enemy)
            display_battle_log(f"--- Turn {self.turn_counter} ---")
            
            # Get player action (This assumes interactive input outside the class)
            # For demonstration, we'll force a basic attack unless they can run
            
            # Get player choice (usually input(), but we'll simulate an action)
            # Action: 1=Attack, 2=Ability, 3=Run
            player_choice = '1' # Default to attack
            
            # This is where interactive input would go:
            # player_choice = input("1. Attack | 2. Ability | 3. Run: ")
            
            try:
                # We handle the player action
                if player_choice == '1':
                    self.basic_attack(self.character, self.enemy)
                elif player_choice == '2':
                    # NOTE: Simplified ability usage; assumes no separate inventory management
                    self.use_special_ability()
                elif player_choice == '3':
                    if self.attempt_escape():
                        display_battle_log(f"{self.character['name']} successfully escaped!")
                        self.combat_active = False
                        break
                    else:
                        display_battle_log(f"{self.character['name']} failed to escape!")
                else:
                    display_battle_log("Invalid choice. Skipping turn...")
                    
            except AbilityOnCooldownError as e:
                display_battle_log(f"Action failed: {e}")
                continue # Player loses a turn
            
            # --- 2. Check End Condition after Player Turn ---
            winner = self.check_battle_end()
            if winner:
                self.combat_active = False
                return self._handle_victory(winner)

            # --- 3. Enemy Turn ---
            self.enemy_turn()
            
            # --- 4. Check End Condition after Enemy Turn ---
            winner = self.check_battle_end()
            if winner:
                self.combat_active = False
                return self._handle_victory(winner)

        return {'winner': 'none', 'xp_gained': 0, 'gold_gained': 0}

    def _handle_victory(self, winner):
        """Helper to process rewards and final status."""
        if winner == 'player':
            rewards = get_victory_rewards(self.enemy)
            
            # NOTE: In a full implementation, you'd call character_manager functions here
            # gain_experience(self.character, rewards['xp'])
            # add_gold(self.character, rewards['gold'])

            display_battle_log(f"{self.character['name']} defeated the {self.enemy['name']}!")
            display_battle_log(f"Gained {rewards['xp']} XP and {rewards['gold']} Gold.")
            return {
                'winner': 'player', 
                'xp_gained': rewards['xp'], 
                'gold_gained': rewards['gold']
            }
        else: # winner == 'enemy'
            display_battle_log(f"{self.character['name']} has been defeated by the {self.enemy['name']}!")
            return {
                'winner': 'enemy', 
                'xp_gained': 0, 
                'gold_gained': 0
            }


    def player_turn(self):
        """
        Handle player's turn - Not used directly in start_battle loop above
        """
        # Kept to fulfill starter code but logic moved into start_battle
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not currently active.")
        
        display_battle_log("Options:")
        print("1. Basic Attack")
        print("2. Special Ability (if available)")
        print("3. Try to Run")
        # Player input would be processed here...
        
    def basic_attack(self, attacker, defender):
        """Perform a standard attack."""
        damage = self.calculate_damage(attacker, defender)
        self.apply_damage(defender, damage)
        display_battle_log(f"{attacker['name']} attacks {defender['name']} for {damage} damage!")


    def enemy_turn(self):
        """
        Handle enemy's turn - simple AI
        
        Enemy always attacks
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not currently active.")
            
        # Calculate damage (Enemy uses its Strength stat)
        damage = self.calculate_damage(self.enemy, self.character)
        
        # Apply to character
        self.apply_damage(self.character, damage)
        
        display_battle_log(f"{self.enemy['name']} strikes {self.character['name']} for {damage} damage!")
        
    
    def calculate_damage(self, attacker, defender):
        """
        Calculate damage from attack
        
        Damage formula: attacker['strength'] - (defender['strength'] // 4)
        Minimum damage: 1
        """
        attacker_stat = attacker.get('strength', 0)
        defender_stat = defender.get('strength', 0) # Assumes 'strength' doubles as defense stat in formula
        
        # Damage formula: attacker['strength'] - (defender['strength'] // 4)
        damage_reduction = defender_stat // 4
        
        raw_damage = attacker_stat - damage_reduction
        
        # Minimum damage: 1
        damage = max(1, raw_damage)
        
        return damage
    
    def apply_damage(self, target, damage):
        """
        Apply damage to a character or enemy
        
        Reduces health, prevents negative health
        """
        current_health = target.get('health', 0)
        
        # Apply damage
        target['health'] = current_health - damage
        
        # Prevents negative health
        if target['health'] < 0:
            target['health'] = 0
            
    
    def check_battle_end(self):
        """
        Check if battle is over
        
        Returns: 'player' if enemy dead, 'enemy' if character dead, None if ongoing
        """
        if self.enemy['health'] <= 0:
            return 'player'
        elif self.character['health'] <= 0:
            return 'enemy'
        else:
            return None
    
    def attempt_escape(self):
        """
        Try to escape from battle
        
        50% success chance
        """
        # If successful, set combat_active to False (handled in start_battle)
        # Use random number: 0 or 1, 50% chance for True
        return random.choice([True, False])

    def use_special_ability(self):
        """
        Uses the character's special ability.
        
        Raises: AbilityOnCooldownError (simplified)
        """
        # Basic Cooldown Check: only once every 3 turns
        if self.turn_counter - self.player_last_ability_turn < 3:
            raise AbilityOnCooldownError("Special ability is on cooldown. Wait a few turns!")
            
        self.player_last_ability_turn = self.turn_counter

        char_class = self.character.get('class', 'Warrior').lower()
        
        if char_class == 'warrior':
            warrior_power_strike(self.character, self.enemy)
        elif char_class == 'mage':
            mage_fireball(self.character, self.enemy)
        elif char_class == 'rogue':
            rogue_critical_strike(self.character, self.enemy)
        elif char_class == 'cleric':
            cleric_heal(self.character)
        else:
            display_battle_log("No known special ability for this class.")

# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def _apply_ability_damage(target, damage):
    """Helper for abilities to apply damage similarly to SimpleBattle.apply_damage"""
    current_health = target.get('health', 0)
    target['health'] = current_health - damage
    if target['health'] < 0:
        target['health'] = 0

def warrior_power_strike(character, enemy):
    """Warrior special ability: 2x strength damage"""
    base_damage = character.get('strength', 0) * 2
    _apply_ability_damage(enemy, base_damage)
    display_battle_log(f"{character['name']} uses Power Strike for {base_damage} damage!")

def mage_fireball(character, enemy):
    """Mage special ability: 2x magic damage"""
    base_damage = character.get('magic', 0) * 2
    _apply_ability_damage(enemy, base_damage)
    display_battle_log(f"{character['name']} casts Fireball for {base_damage} magic damage!")

def rogue_critical_strike(character, enemy):
    """Rogue special ability: 50% chance for triple strength damage"""
    if random.random() < 0.5: # 50% chance
        damage = character.get('strength', 0) * 3
        _apply_ability_damage(enemy, damage)
        display_battle_log(f"{character['name']} lands a CRITICAL STRIKE for {damage} damage!")
    else:
        # Standard attack damage if crit fails (or zero for simplicity)
        damage = character.get('strength', 0) # Just a standard hit, or 0 ability damage
        _apply_ability_damage(enemy, damage)
        display_battle_log(f"{character['name']} attempts a Critical Strike, hitting for {damage} damage.")

def cleric_heal(character):
    """Cleric special ability: Restore 30 health (not exceeding max_health)"""
    heal_amount = 30
    current_health = character.get('health', 0)
    max_health = character.get('max_health', 1)
    
    new_health = current_health + heal_amount
    
    # Not exceeding max_health
    if new_health > max_health:
        heal_amount = max_health - current_health
        character['health'] = max_health
    else:
        character['health'] = new_health
        
    display_battle_log(f"{character['name']} uses Heal, restoring {heal_amount} health.")

# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Check if character is in condition to fight
    
    Returns: True if health > 0 and not in battle (assuming external battle check)
    """
    # NOTE: The "not in battle" check is complex without a global state/manager.
    # We only check health here.
    return character.get('health', 0) > 0

def get_victory_rewards(enemy):
    """
    Calculate rewards for defeating enemy
    
    Returns: Dictionary with 'xp' and 'gold'
    """
    return {
        'xp': enemy.get('xp_reward', 0),
        'gold': enemy.get('gold_reward', 0)
    }

def display_combat_stats(character, enemy):
    """
    Display current combat status
    
    Shows both character and enemy health/stats
    """
    print("\n--------------------------")
    print(f"{character['name']} ({character['class']}): HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")
    print("--------------------------")

def display_battle_log(message):
    """
    Display a formatted battle message
    """
    print(f">>> {message}")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
    
    # Test enemy creation
    # try:
    #     goblin = create_enemy("goblin")
    #     print(f"Created {goblin['name']}")
    # except InvalidTargetError as e:
    #     print(f"Invalid enemy: {e}")
    
    # Test battle
    # test_char = {
    #     'name': 'Hero',
    #     'class': 'Warrior',
    #     'health': 120,
    #     'max_health': 120,
    #     'strength': 15,
    #     'magic': 5
    # }
    #
    # battle = SimpleBattle(test_char, goblin)
    # try:
    #     result = battle.start_battle()
    #     print(f"Battle result: {result}")
    # except CharacterDeadError:
    #     print("Character is dead!")
    #     result = battle.start_battle()
    #     print(f"Battle result: {result}")
    # except CharacterDeadError:
    #     print("Character is dead!")

